import requests
import asyncio
import requests_async
from config import api_key

api_host = "https://api.um.warszawa.pl/api/action/{}"

url_timetable = api_host.format("dbtimetable_get")
resource_busstop = "b27f4c17-5c50-4a5b-89dd-236b282bc499"
resource_lines = "88cd555f-6f31-43ca-9de4-66c479ad5942"
resource_table = "e923fa0e-d96c-43f9-ae6e-60518c9f3238"

resource_stops = "ab75c33d-3a26-4342-b36a-6e5fef0a3ac3"

url_stops = api_host.format("dbstore_get")


def get_busstop(name): # not used
    """nazwa przystaku
    -> busstopId"""
    return requests.get(
        url_timetable, params={"id": resource_busstop, "apikey": api_key, "name": name}
    )


def get_lines(busstop_id, busstop_nr):
    """busstop_id -  from first
    busstop_nr - str: 01, 02. invalid returns empty list
    -> list of lines from this point"""
    return requests.get(
        url_timetable,
        params={
            "id": resource_lines,
            "apikey": api_key,
            "busstopId": busstop_id,
            "busstopNr": busstop_nr,
        },
    )


async def async_get_lines(busstop_id, busstop_nr):
    """busstop_id -  from first
    busstop_nr - str: 01, 02. invalid returns empty list
    -> list of lines from this point"""
    return await requests_async.get(
        url_timetable,
        params={
            "id": resource_lines,
            "apikey": api_key,
            "busstopId": busstop_id,
            "busstopNr": busstop_nr,
        },
    )


def get_table(busstop_id, busstop_nr, line):
    return requests.get(
        url_timetable,
        params={
            "id": resource_table,
            "apikey": api_key,
            "busstopId": busstop_id,
            "busstopNr": busstop_nr,
            "line": line,
        },
    )


async def async_get_table(busstop_id, busstop_nr, line):
    return await requests_async.get(
        url_timetable,
        params={
            "id": resource_table,
            "apikey": api_key,
            "busstopId": busstop_id,
            "busstopNr": busstop_nr,
            "line": line,
        },
    )


def get_stops():
    """
        this is a list of objects:
        {
        "result": [
            {
                "values": [
                    {"value": "1001", "key": "zespol"},
                    {"value": "01", "key": "slupek"},
                    {"value": "Kijowska", "key": "nazwa_zespolu"},
                    {"value": "2201", "key": "id_ulicy"},
                    {"value": "52.248455", "key": "szer_geo"},
                    {"value": "21.044827", "key": "dlug_geo"},
                    {"value": "al.Zieleniecka", "key": "kierunek"},
                    {"value": "2022-07-01 00:00:00.0", "key": "obowiazuje_od"},
                ]
            },
            {
                "values": [
                    {"value": "1001", "key": "zespol"},
                    {"value": "02", "key": "slupek"},
                    {"value": "Kijowska", "key": "nazwa_zespolu"},
                    {"value": "2201", "key": "id_ulicy"},
                    {"value": "52.249078", "key": "szer_geo"},
                    {"value": "21.044443", "key": "dlug_geo"},
                    {"value": "Z\\u0105bkowska", "key": "kierunek"},
                    {"value": "2022-07-01 00:00:00.0", "key": "obowiazuje_od"},
                ]
            },
        ]
    }
    complete response size: 2.6 Mb"""
    return requests.get(
        url_stops,
        params={"id": resource_stops, "apikey": api_key},
    )
