from repository import models, session
from repository.walk_repo import get_departures_from_unit, get_route_of_one_course
from repository.models import TableData, BusStop
import datetime
from typing import Dict
import utils


class Ride:
    """how U got to that stop? we need stop, hour
    stop start, table start, table end
    """

    def __init__(
        self,
        start: BusStop,  # are these needed? yes bc starting point has no tab
        end: BusStop,
        time: datetime.time,
        tab_start: TableData = None,
        tab_end: TableData = None,
    ) -> None:
        self.start = start
        self.end = end
        self.time = time
        self.table_start = tab_start
        self.table_end = tab_end

    def __str__(self) -> str:
        if self.table_start:
            return (
                f"{self.table_start.line_obj} {self.table_start.time} from {self.table_start.bus_stop_obj} "
                f"to {self.table_end.bus_stop_obj} at {self.table_end.time}"
            )
        return f"start at {self.start} at {self.time}"


class Walker:
    max_depth = 5
    additional_depth = 0  # after finding solution

    def __init__(self, start: models.BusStop, end: models.BusStop, time: datetime.time):
        self.start = start
        self.end = end
        self.time_start = time
        self.unit_to_ride: Dict[str, Ride] = {}
        # for now, we keep only one option, the earliest
        self.courses_seen = set()  # watch Table.course_id seen
        self.solution_found = False

        self.unit_to_ride[start.unit] = Ride(self.start, self.start, self.time_start)
        self.another_step_queue = [(start, time)]

    def solve(self):
        print(f"search to {self.end} from {self.start} at {self.time_start}")

        for i in range(self.max_depth):
            print("iteration", i)
            if self.do_one_step():
                break

        for j in range(self.additional_depth):
            print("additional iteration", j)
            self.do_one_step()

        for obj in self.get_solution_sequence():
            print(obj)

    def do_one_step(self):
        stops_times_queue, self.another_step_queue = self.another_step_queue, []
        print(f"start with {len(stops_times_queue)} nodes")
        while stops_times_queue:
            stop_, time_ = stops_times_queue.pop()
            # if stop_ not in self.stop_to_ride or self.stop_to_ride[stop_].time_ > time_:
            # we process outgoing courses from this stop
            for depart in get_departures_from_unit(
                stop_, time_, min_ahead=60
            ):  # TODO now it automaticly add 1 minute
                # may happer, we will want to go back and search bigger timespan
                if depart.course_id in self.courses_seen:  # tab - course FROM stop
                    continue
                self.courses_seen.add(depart.course_id)
                # we analyze stops of course taken - course TO stop
                possible_arrivals = get_route_of_one_course(depart, depart.time)
                self.analyze_arrivals(depart, possible_arrivals)

        return self.solution_found

    def analyze_arrivals(self, depart: TableData, possible_arrivals):
        for possible_time_table in possible_arrivals:
            dest: BusStop = possible_time_table.bus_stop_obj
            if (
                dest.unit in self.unit_to_ride
                and self.unit_to_ride[dest.unit].time <= possible_time_table.time
            ):
                continue  # we already have arrival and its faster

            self.unit_to_ride[dest.unit] = Ride(
                start=depart.bus_stop_obj,
                end=dest,
                time=possible_time_table.time,
                tab_start=depart,
                tab_end=possible_time_table,
            )
            if dest.unit == self.end.unit:
                self.solution_found = True
                print("solution found")
            else:
                self.another_step_queue.append((dest, possible_time_table.time))

    def get_solution_sequence(self):
        # TODO what can go wrong? cycles, no solution, start == end
        solution = []
        current_ride = self.unit_to_ride[self.end.unit]
        solution.append(current_ride)
        while current_ride.start.unit != self.start.unit:
            current_ride = self.unit_to_ride[current_ride.start.unit]
            solution.append(current_ride)
        return solution[::-1]


pogodna_bus_stop = session.get(BusStop, 2835)  # pogodna
_bus_stop = session.get(BusStop, 6894)  # cm polnocny
# _bus_stop = session.get(BusStop, 174) # ksieznej anny
with utils.Timer():
    walker = Walker(pogodna_bus_stop, _bus_stop, datetime.time(11, 45))
    walker.solve()
