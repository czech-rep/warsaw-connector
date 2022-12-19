import datetime
import utils
from repository import models, alchemy_tables
from repository.models import TableData, BusStop
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from repository import session
from typing import Iterable
from functools import lru_cache


@lru_cache(3000)
def get_bus_stops_of_same_unit(bus_stop: BusStop):
    q = select(BusStop).filter(BusStop.stop_id == bus_stop.stop_id)
    return session.execute(q).scalars()


def get_outgoing_tables(
    bus_stop_ids, time: datetime.time, min_ahead: int = 60
) -> Iterable[TableData]:
    q = (
        select(TableData)
        .filter(TableData.bus_stop.in_(bus_stop_ids))
        .filter(TableData.time >= time)
        .filter(TableData.time < utils.add_minutes_to_hour(time, min_ahead))
        .order_by(TableData.time)
    )
    return session.execute(q).scalars()


# the same from any stop number
def get_departures_from_unit(
    bus_stop: BusStop, time: datetime.time, min_ahead: int = 60
) -> Iterable[TableData]:
    time = utils.add_minutes_to_hour(time, 1)
    # add 1 to have a minute for change TODO do it better
    bus_stop_ids = list(stop.id for stop in get_bus_stops_of_same_unit(bus_stop))
    return get_outgoing_tables(bus_stop_ids, time, min_ahead)


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
