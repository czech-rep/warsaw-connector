from repository import models, session
from repository.walk_repo import get_departures_from_unit, get_route_of_one_course
from repository.models import TableData, BusStop
import datetime
from typing import Dict, List, Union
import utils
from dataclasses import dataclass, field


@dataclass
class Ride:
    table_start: TableData
    table_end: TableData
    previous_ride: Union["Ride", None] = None

    @property
    def arrival_stop(self):
        return self.table_end.bus_stop_obj

    @property
    def arrival_time(self):
        return self.table_end.time

    def __str__(self) -> str:
        return (
            f"from {self.table_start.bus_stop_obj} take {self.table_start.line_obj} at {self.table_start.time} "
            f"to {self.table_end.bus_stop_obj} at {self.table_end.time}"
        )

    def get_solution(self):
        if self.previous_ride is None:
            yield f"Started from {self.table_start.bus_stop_obj} at {self.table_start.time}"
            yield str(self)
            return
        yield from self.previous_ride.get_solution()
        yield str(self)

    def print_solution(self):
        # print(self.get_solution())
        # print("\n".join(self.get_solution()))
        for elem in self.get_solution():
            print(elem)


# @dataclass
# class Path:
#     # __slots__ = "start", "rides"
#     start: BusStop
#     start_time: datetime.time
#     rides: List[Ride] = field(default=list)

#     @property
#     def final_stop(self):
#         return self.rides[-1].table_end.bus_stop_obj if self.rides else self.start

#     @property
#     def final_time(self):
#         return self.rides[-1].table_end.time if self.rides else self.start_time

#     def __str__(self) -> str:
#         return (
#             f"Started from {self.start} at {self.start_time}",
#             "\n".join(*(str(elem) for elem in self.rides)),
#             f"\nFinished on {self.final_stop} at {self.final_time}",
#         )


class Walker:
    max_depth = 5
    additional_depth = 0  # after finding solution
    max_solutions_from_edge = 2
    max_solutions = 8

    def __init__(self, start: models.BusStop, end: models.BusStop, time: datetime.time):
        self.start = start
        self.end = end
        self.time_start = time
        self.unit_to_ride: Dict[str, Ride] = {}
        # for now, we keep only one option, the earliest
        self.courses_seen = set()  # watch Table.course_id seen

        self.another_step_queue = []
        self.solutions: List[Ride] = []

    def solve(self):
        print(f"search from {self.start} at {self.time_start} to {self.end}")

        self.do_first_step()

        for i in range(1, self.max_depth):
            if self.solutions:
                break
            print("iteration", i)
            self.do_one_step()

        for j in range(self.additional_depth):
            print("additional iteration", j)
            self.do_one_step()

        for obj in self.solutions:
            obj.print_solution()
            print("---")

    def do_first_step(self):
        self.process_departures(self.start, self.time_start, None)

    def do_one_step(self):
        main_queue = sorted(
            self.another_step_queue, key=lambda obj: obj.arrival_time, reverse=True
        )
        self.another_step_queue = []
        print(f"start with {len(main_queue)} nodes")
        while main_queue:
            start_ride: Ride = main_queue.pop()
            self.process_departures(
                start_ride.arrival_stop, start_ride.arrival_time, start_ride
            )
            if len(self.solutions) > self.max_solutions:
                break

    def process_departures(self, stop_: BusStop, time_: datetime.time, current_start):
        # if stop_ not in self.stop_to_ride or self.stop_to_ride[stop_].time_ > time_:
        # we process outgoing courses from this stop
        for depart in get_departures_from_unit(stop_, time_, min_ahead=25):
            # TODO now it automaticly add 1 minute
            # may happen, we will want to go back and search bigger timespan
            if depart.course_hash in self.courses_seen:  # depart - course FROM stop
                continue
            self.courses_seen.add(depart.course_hash)
            # now we analyze stops of course taken - course TO stop
            possible_arrivals = get_route_of_one_course(depart, depart.time)
            self.analyze_arrivals(current_start, depart, possible_arrivals)

    def analyze_arrivals(
        self, current_start: Union[Ride, None], depart: TableData, possible_arrivals
    ):
        for possible_time_table in possible_arrivals:
            # dest: BusStop = possible_time_table.bus_stop_obj
            # if (
            #     dest.unit in self.unit_to_ride
            #     and self.unit_to_ride[dest.unit].time <= possible_time_table.time
            # ):
            #     continue  # we already have arrival and its faster

            # self.unit_to_ride[dest.unit] = Ride(
            #     table_start=depart.bus_stop_obj,
            #     table_end=dest,
            # )
            ride = Ride(
                table_start=depart,
                table_end=possible_time_table,
                previous_ride=current_start,
            )
            if possible_time_table.bus_stop_obj.unit == self.end.unit:
                self.solutions.append(ride)
                # print("solution found")
                break  # do not analyze other possible stops
            else:
                self.another_step_queue.append(ride)


pogodna_bus_stop = session.get(BusStop, 2831)
_bus_stop = session.get(BusStop, 6991)  # cm polnocny
# _bus_stop = session.get(BusStop, 12) # zabkowska
# _bus_stop = session.get(BusStop, 174) # ksieznej anny
with utils.Timer():
    walker = Walker(pogodna_bus_stop, _bus_stop, datetime.time(11, 45))
    walker.solve()


# TODO what can go wrong? cycles, no solution, start == end
# TODO when theres no solution?
# TODO when found first solution, dont explore 1.2 times longer
