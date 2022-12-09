from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    Column,
    DateTime,
    Time,
    UniqueConstraint,
)
from sqlalchemy.schema import Table, MetaData, Index
from sqlalchemy.orm import registry, relationship
from repository import models


# holds a collection of Table objects as well as an optional binding to an Engine or Connection
metadata = MetaData()

bus_stops_table = Table(
    "bus_stops",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("stop_id", String(10), nullable=False),
    Column("number", String(10), nullable=False),
    Column("name", String(60), nullable=False),
    UniqueConstraint("stop_id", "number", name="unique_stop_id_number"),
    Index("ix_stop_id", "stop_id"),
)

bus_stop_data_table = Table(
    "bus_stop_data",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "bus_stop_id", ForeignKey("bus_stops.id", ondelete="CASCADE"), nullable=False
    ),  # defining foreign keys use table_name.column
    Column("street_id", String(20)),
    Column("geo_width", String(20), nullable=False),
    Column("geo_length", String(20), nullable=False),
    Column("direction", String(60)),
    Column("valid_from", DateTime, nullable=False),
    UniqueConstraint("bus_stop_id", "valid_from", name="unique_stop_id_date"),
)

lines_table = Table(  # TODO table
    "lines",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("line_number", String(10), nullable=False, unique=True),
)


time_tables_table = Table(
    "tables",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("brigade", String(10), nullable=False),
    Column("direction", String(50), nullable=False),
    Column("route", String(20), nullable=False),
    Column("time", Time, nullable=False),
    Column("bus_stop", ForeignKey("bus_stops.id", ondelete="CASCADE"), nullable=False),
    Column("line", ForeignKey("lines.id", ondelete="CASCADE"), nullable=False),
    UniqueConstraint(
        "brigade",
        "bus_stop",
        "line",
        "time",
        name="one_brigade_of_line_on_stop_at_time",
    ),
    Index("ix_bus_stop_and_time", "bus_stop", "time"),
    Index("ix_search_course", "line", "brigade", "direction", "route", "time"),
)

mapper_registry = registry()
# uses the engine object to create all the defined table objects and stores the information in metadata
# metadata.create_all(bind=engine)

## MAPPERS ##

# many to many
bus_stop_lines = Table(
    "bus_stop_lines",
    metadata,
    Column(
        "bus_stop_id", ForeignKey("bus_stops.id", ondelete="CASCADE"), primary_key=True
    ),
    Column("line_id", ForeignKey("lines.id", ondelete="CASCADE"), primary_key=True),
)

# backref - creates on provided bi directional ref
# secondary - for a many-to-many relationship, specifies the intermediary table
mapper_registry.map_imperatively(
    models.BusStop,
    bus_stops_table,
    properties={  # defining relationships use Model class
        "stop_data": relationship(
            models.StopData, back_populates="bus_stop", lazy="raise"
        ),  # remove back_populates
        "lines": relationship(
            models.Lines,
            back_populates="bus_stops",
            secondary=bus_stop_lines,
            lazy="raise",
        ),
    },  # relationships are defined only for python, DB doesn't know
)
mapper_registry.map_imperatively(
    models.StopData,
    bus_stop_data_table,
    properties={
        "bus_stop": relationship(models.BusStop, back_populates="stop_data"),
    },
)
mapper_registry.map_imperatively(
    models.Lines,
    lines_table,
    properties={
        "bus_stops": relationship(
            models.BusStop,
            back_populates="lines",
            secondary=bus_stop_lines,
            lazy="raise",
        ),
    },
)
mapper_registry.map_imperatively(
    models.TableData,
    time_tables_table,
    properties={
        "bus_stop_obj": relationship(models.BusStop, lazy="selectin"),
        "line_obj": relationship(models.Lines, lazy="selectin"),
    },
)
