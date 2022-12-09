import datetime
from dataclasses import dataclass, field
from typing import Union, List, Dict, Iterable


@dataclass  # column bus_stops
class BusStop:
    id: int = field(init=False)
    stop_id: str # TODO change to unit
    number: str  #  "01", "02", "78", ... - not consistent
    name: str
    stop_data: List["StopData"] = field(default_factory=list)
    lines: List["Lines"] = field(default_factory=list)

    @property
    def unit(self):
        return self.stop_id

    def __hash__(self):
        return hash((self.stop_id, self.number))

    def __eq__(self, other):
        return (self.stop_id, self.number) == (other.stop_id, other.number)

    def __repr__(self) -> str:
        return f"{self.name} {self.number}"


@dataclass
class StopData:  # mapped to column
    id: int = field(init=False)
    street_id: Union[str, None]
    geo_width: str  # TODO create GeoCoords type
    geo_length: str
    direction: Union[str, None]
    valid_from: datetime.datetime
    bus_stop: int  # relation to BusStop

    @classmethod
    def from_api_data(cls, api_data: "StopDataRegistry.ApiStopData", bus_stop: BusStop):
        # we provide a object here, boceouse id may be not yet created
        """[
            {"value": "1001", "key": "zespol"},
            {"value": "01", "key": "slupek"},
            {"value": "Kijowska", "key": "nazwa_zespolu"},
            {"value": "2201", "key": "id_ulicy"},
            {"value": "52.248455", "key": "szer_geo"},
            {"value": "21.044827", "key": "dlug_geo"},
            {"value": "al.Zieleniecka", "key": "kierunek"},
            {"value": "2022-07-01 00:00:00.0", "key": "obowiazuje_od"},
        ]"""
        return cls(
            street_id=api_data.id_ulicy,
            geo_width=api_data.szer_geo,
            geo_length=api_data.dlug_geo,
            direction=api_data.kierunek,
            valid_from=api_data.obowiazuje_od,
            bus_stop=bus_stop,
        )


class StopDataRegistry:
    """class that covers objects from stop data endpoint
    holds registry of objects so that every BusStop is created once
    BusStop may have more than one BusStopData relatives
    """

    def __init__(self, hashes_to_objects: Dict = None) -> None:
        self.bus_stop_objects = hashes_to_objects or {}
        self.new_objects = []  # here we collect new objects to add to db

    @classmethod
    def from_queried_all(cls, models_iter: Iterable[BusStop]):
        return cls({hash(o): o for o in models_iter})

    @property
    def bus_stop_list(self, sorted=False):
        list_ = list(self.bus_stop_objects.values())
        if not sorted:
            return list_
        return sorted(list_, key=lambda obj: obj.id)

    def add_new(self, data_dict):
        """we check is BusStop already created
        we always create new BusStopData"""
        stop_api_object = self.ApiStopData(**data_dict)
        if stop_api_object in self.bus_stop_objects:
            stop_model = self.bus_stop_objects[stop_api_object]
        else:
            stop_model = BusStop(
                stop_id=stop_api_object.zespol,
                number=stop_api_object.slupek,
                name=stop_api_object.nazwa_zespolu,
            )
            self.bus_stop_objects[stop_api_object] = stop_model
            self.new_objects.append(stop_model)
        self.new_objects.append(StopData.from_api_data(stop_api_object, stop_model))

    @dataclass
    class ApiStopData:
        """models api response
        street_id - sometimes 'null'
        direction - sometimes "____" or 'null'"""

        zespol: str
        slupek: str
        nazwa_zespolu: str
        id_ulicy: Union[str, None]
        szer_geo: str
        dlug_geo: str
        kierunek: Union[str, None]
        obowiazuje_od: str

        def __post_init__(self):
            if self.id_ulicy == "null":
                self.id_ulicy = None
            if self.kierunek == "null" or self.kierunek.startswith("__"):
                self.kierunek = None

        def __hash__(self):
            return hash((self.zespol, self.slupek))

        def __eq__(self, other):
            return (self.zespol, self.slupek) == (other.zespol, other.slupek)


@dataclass
class Lines:
    id: int = field(init=False)
    line_number: str

    def __repr__(self) -> str:
        return f"Line {self.line_number}"


class LinesRegistry:
    def __init__(self, lines_to_objects: Dict = None) -> None:
        self.lines_to_objects = lines_to_objects or {}
        self.new_objects = []

    @classmethod
    def from_queried_all(cls, models_iter: Iterable[Lines]):
        return cls({o.line_number: o for o in models_iter})

    def get_new(self, linia: str):
        if linia in self.lines_to_objects:
            return self.lines_to_objects[linia]
        new_line_model = Lines(line_number=linia)
        self.lines_to_objects[linia] = new_line_model
        self.new_objects.append(new_line_model)
        return new_line_model


@dataclass
class ApiStopTable:
    """mode api data aboute time tables"""

    __slots__ = (
        "brygada",
        "kierunek",
        "trasa",
        "czas",
        "symbol_1",
        "symbol_2",
    )
    brygada: str
    kierunek: str
    trasa: str
    czas: str
    symbol_1: str
    symbol_2: str

    def __post_init__(self):
        """time format: HH:MM:SS
        night buses schedules go like: 26:20 ;)
        """
        hour, minute, sec = map(int, self.czas.strip().split(":"))
        if hour >= 24:
            hour -= 24
        self.czas = datetime.time(hour, minute, sec)

    # TODO implement here hash and eq instead of TableData.
    # Move class definition to table registry


@dataclass
class TableData:
    """model of time table unit"""  # TODO use slots

    id: int = field(init=False)
    brigade: str
    direction: str
    route: str
    time: datetime.time
    # from relations:
    bus_stop: int
    line: int
    bus_stop_obj: BusStop = field(init=False)
    line_obj: Lines = field(init=False)

    @classmethod
    def from_api_data(cls, api_dict, bus_stop_id: int, line_id: int):
        """[
            {"value": "null", "key": "symbol_2"},
            {"value": "null", "key": "symbol_1"},
            {"value": "59", "key": "brygada"},
            {"value": "Dw.Wschodni (Lubelska)", "key": "kierunek"},
            {"value": "TP-DWL", "key": "trasa"},
            {"value": "05:34:00", "key": "czas"},
        ]"""
        api_data = ApiStopTable(**api_dict)
        return cls(
            brigade=api_data.brygada,
            direction=api_data.kierunek,
            route=api_data.trasa,
            time=api_data.czas,
            bus_stop=bus_stop_id,
            line=line_id,
        )

    def __hash__(self) -> int:
        return hash((self.brigade, self.bus_stop, self.line, self.time))

    @property
    def course_id(self):
        return hash((self.brigade, self.direction, self.route, self.line))

    def __repr__(self) -> str:
        return f"{self.id}: {self.line_obj} from {self.bus_stop_obj} at {self.time.strftime('%H:%M')} to {self.direction}"


class TableRegistry:
    def __init__(self) -> None:
        self.table_set = set()

    def already_exist(self, obj: TableData):
        if hash(obj) not in self.table_set:
            self.table_set.add(hash(obj))
            return False
        return True
