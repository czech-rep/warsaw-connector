import json
from repository import models, requests_um
from typing import Dict, List


def convert_weird_key_value_list_to_dict(dict_in: Dict):
    """
    convert from
    {"values": [
        {"value": "1001", "key": "zespol"},
        {"value": "01", "key": "slupek"},
        {"value": "Kijowska", "key": "nazwa_zespolu"},
        {"value": "2201", "key": "id_ulicy"},
        {"value": "52.248455", "key": "szer_geo"},
        {"value": "21.044827", "key": "dlug_geo"},
        {"value": "al.Zieleniecka", "key": "kierunek"},
        {"value": "2022-07-01 00:00:00.0", "key": "obowiazuje_od"},
    ]}
    to:
    ("zespol", "1001"), ("slupek", "01"), ...
    """
    for dict_ in dict_in["values"]:
        yield dict_["key"], dict_["value"]


def dict_from_get_request(api_payload: Dict):
    """provide result of get request
    iterate out dictionaries
    """
    data_dict = json.loads(api_payload)
    for data_dict in data_dict["result"]:
        values_dict = {}
        for key, value in convert_weird_key_value_list_to_dict(data_dict):
            values_dict[key] = value
        yield values_dict


def get_all_stops():
    yield from dict_from_get_request(requests_um.get_stops().text)


async def get_tables_for_stop_line(
    busstop_id: str, busstop_nr: str, line_number: str
) -> List[models.TableData]:
    api_response = await requests_um.async_get_table(busstop_id, busstop_nr, line_number)
    if not api_response.status_code == 200:
        raise Exception(f"status code {api_response.status_code} on {busstop_nr} {line_number} {api_response.text}")
    return list(dict_from_get_request(api_response.text))


def values_of_lines(api_payload: Dict):
    """flatten lines payload to list of strings"""
    """{"result": [
        {"values": [{"value": "138", "key": "linia"}]},
        {"values": [{"value": "166", "key": "linia"}]},
        {"values": [{"value": "509", "key": "linia"}]},
        {"values": [{"value": "N21", "key": "linia"}]},
    ]
    }"""
    data_dict = json.loads(api_payload)
    list_of_line_ids = []
    for data_dict in data_dict["result"]:
        for key, value in convert_weird_key_value_list_to_dict(data_dict):
            if key == "linia":
                list_of_line_ids.append(value)
    return list_of_line_ids


async def get_lines_for_stop(stop_id: str, number: str) -> List[str]:
    response = await requests_um.async_get_lines(stop_id, number)
    return values_of_lines(response.text)
