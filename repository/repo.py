from repository import models, alchemy_tables
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from repository import session


def get_bus_stops_sole():
    q = select(models.BusStop)
    return session.execute(q).scalars()


def get_bus_stops():
    q = (
        select(models.BusStop)
        .options(joinedload(models.BusStop.lines))
        .order_by(models.BusStop.id)
    )
    return session.execute(q).unique().scalars()


def get_bus_stops_from(from_id: int, limit=None):
    q = (
        select(models.BusStop)
        .filter(models.BusStop.id >= from_id)
        .options(selectinload(models.BusStop.lines))
        .order_by(models.BusStop.id)
    )
    if limit:
        q = q.limit(limit)
    return session.execute(q).unique().scalars()


def get_all_lines():
    q = select(models.Lines).options(joinedload(models.Lines.bus_stops))
    return session.execute(q).unique().scalars()
