from repository import data_loader, models, repo, session


stop_registry = models.StopDataRegistry.from_queried_all(repo.get_bus_stops())
lines_registry = models.LinesRegistry.from_queried_all(repo.get_all_lines())
tables_registry = models.TableRegistry()


async def handle_lines_for_id(bus_stop: models.BusStop):
    """our worker concurrent function
    what it does, it modifies global line registry and stop registry
    all in one session
    work time 4:47"""
    print(f"start for {bus_stop.id}")
    lines = await data_loader.get_lines_for_stop(
        stop_id=bus_stop.stop_id,
        number=bus_stop.number,
    )
    for line in lines:
        line_object = lines_registry.get_new(line)
        if line_object not in bus_stop.lines:
            bus_stop.lines.append(line_object)
    print(f"{len(bus_stop.lines)} in stop {bus_stop.id}")


async def handle_timetables_for_one_stop(bus_stop: models.BusStop):
    print("start", bus_stop.id)
    for line in bus_stop.lines:
        tables_dicts = await data_loader.get_tables_for_stop_line(
            busstop_id=bus_stop.stop_id,
            busstop_nr=bus_stop.number,
            line_number=line.line_number,
        )
        for tab_dict in tables_dicts:
            table = models.TableData.from_api_data(
                api_dict=tab_dict, bus_stop_id=bus_stop.id, line_id=line.id
            )
            if table.bus_stop is None:
                raise Exception(table)
            if not tables_registry.already_exist(table):
                session.add(table)
    print("end", bus_stop.id)
