from repository import repo, models, requests_um, session, data_loader
import utils


def download_all_bus_stops(stop_registry):
    resp_text = requests_um.get_stops().text
    for dict_ in data_loader.dict_from_get_request(resp_text):
        stop_registry.add_new(dict_)

    session.add_all(stop_registry.new_objects)
    session.commit()


if __name__ == "__main__":
    with utils.Timer():
        stop_registry = models.StopDataRegistry.from_queried_all(
            repo.get_bus_stops_sole()
        )
        download_all_bus_stops(stop_registry)
