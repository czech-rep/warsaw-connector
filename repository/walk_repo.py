from dataclasses import dataclass, field
import datetime
import utils
from repository import models, alchemy_tables
from repository.models import TableData, BusStop
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from repository import session
from typing import Iterable, Set
from functools import lru_cache
from typing import Dict, List
from utils import add_minutes_to_hour


MIN_AHEAD = 40
MIN_BACK = -6
MINIMUM_MIN_BUFFER = 18


@lru_cache(3000)
def get_bus_stops_of_same_unit(bus_stop: BusStop):
    q = select(BusStop).filter(BusStop.stop_id == bus_stop.stop_id)
    return session.execute(q).scalars()


def get_outgoing_tables(
    bus_stop_ids, time: datetime.time, unique_routes:bool, min_ahead: int = 60
) -> Iterable[TableData]:
    q = (
        select(TableData)
        .filter(TableData.bus_stop.in_(bus_stop_ids))
        .filter(TableData.time >= time)
        .filter(TableData.time < utils.add_minutes_to_hour(time, min_ahead))
        .order_by(TableData.route, TableData.time)
    )
    if unique_routes:
        # we just need distinct routes, bc different direction means different route
        q = q.distinct(TableData.route)
    return session.execute(q).scalars()


def count_called(fn):
    counter = 1

    def inner(*a, **k):
        nonlocal counter
        counter += 1
        if counter % 400 == 0:
            print("- ", counter)
        return fn(*a, **k)

    return inner


# the same from any stop number
@count_called
def get_departures_from_unit(
    bus_stop: BusStop, time: datetime.time, min_ahead: int, unique_routes: bool
) -> Iterable[TableData]:
    time = utils.add_minutes_to_hour(time, 1)
    # add 1 to have a minute for change TODO do it better
    bus_stop_ids = list(stop.id for stop in get_bus_stops_of_same_unit(bus_stop))
    return get_outgoing_tables(bus_stop_ids, time, unique_routes, min_ahead)


def cache_departures(get_departres):
    """we need to cache function that returns a time section"""
    cache: Dict[BusStop, CachedTimeTables] = {}

    def inner(bus_stop: BusStop, time: datetime.time, min_ahead, unique_routes):
        if bus_stop in cache and cache[bus_stop].time_valid(time):
            return cache[bus_stop].elements_from(time)
        query_from = add_minutes_to_hour(time, MIN_BACK)
        query_to = add_minutes_to_hour(time, min_ahead)
        elements = get_departres(bus_stop, query_from, min_ahead, unique_routes)
        if bus_stop not in cache:
            cache[bus_stop] = CachedTimeTables(query_from, query_to, set(elements))
        else:
            cache[bus_stop].extend(elements, query_from, query_to)
        return cache[bus_stop].elements_from(time)

    return inner


@dataclass
class CachedTimeTables:
    queried_from: datetime.time
    queried_to: datetime.time
    elements: Set[TableData]

    def time_valid(self, time):
        if self.queried_from > time:
            return False
        if self.queried_to < utils.add_minutes_to_hour(time, MINIMUM_MIN_BUFFER):
            return False
        return True

    def new_time_span(self, time):
        if self.queried_from > time:
            return (time, self.queried_from)
        else:
            return self.queried_to, add_minutes_to_hour(self.queried_to, MIN_AHEAD)

    def elements_from(self, time):
        # TODO use a sorted structure
        return filter(lambda obj: obj.time >= time, self.elements)

    def extend(self, elems, queried_from, queried_to):
        if self.queried_from > queried_from:
            self.queried_from = queried_from
        if self.queried_to < queried_to:
            self.queried_to = queried_to

        for elem in elems:
            self.elements.add(elem)


get_departures_from_unit_cached = cache_departures(get_departures_from_unit)


def get_route_of_one_course(
    table: TableData, time: datetime.time, min_ahead: int = 80
) -> Iterable[TableData]:
    """explore this course"""
    # do we want to support id?
    # if not isinstance(table, TableData):
    #     query_table = select(TableData).filter(TableData.id == table)
    #     table = session.execute(query_table).scalar_one()
    q = (
        select(TableData)
        .filter(TableData.line == table.line)
        .filter(TableData.route == table.route)
        .filter(TableData.direction == table.direction)
        .filter(TableData.brigade == table.brigade)
        .filter(TableData.time > time)
        .filter(TableData.time < utils.add_minutes_to_hour(time, min_ahead))
        .order_by(TableData.time)
        .options(joinedload(TableData.bus_stop_obj))
    )
    return session.execute(q).scalars()


## not used
def get_all_stops_from_id(stop_unit_id: str):
    """7001 -> (7001, 01), (7001, 02), ..."""
    q = select(models.BusStop).filter(models.BusStop.stop_id == stop_unit_id)
    return session.execute(q).scalars()


def get_all_stops_from_name(name: str):
    """Pogodna -> (7001, 01), (7001, 02), ..."""
    q = select(models.BusStop).filter(models.BusStop.name == name)
    return session.execute(q).scalars()


def get_name_from_stop(bus_stop_id: int):
    """7001 -> Pogodna"""
    q = select(models.StopData).filter(models.StopData.bus_stop == bus_stop_id)
    return session.execute(q).first()[0].name


def get_line(id_):
    q = select(models.Lines).filter(models.Lines.id == id_)
    return session.execute(q).scalar_one().line_number
