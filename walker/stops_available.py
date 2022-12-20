from repository import models, session
from repository.walk_repo import (
    get_departures_from_unit,
    get_route_of_one_course,
    get_departures_from_unit_cached,
)
from repository.models import TableData, BusStop
import datetime
from typing import Dict, List, Union
import utils
from utils import substract_times_to_minutes
from dataclasses import dataclass, field


@dataclass
class Ride:
    table_start: TableData
    table_end: TableData
    start_time: datetime.time
    previous_ride: Union["Ride", None] = None
    start_course_id: int = None

    @property
    def arrival_stop(self):
        return self.table_end.bus_stop_obj

    @property
    def arrival_time(self):
        return self.table_end.time

    @property
    def journey_minutes(self) -> int:
        return substract_times_to_minutes(self.arrival_time, self.start_time)

    def __str__(self) -> str:
        return (
            f"from {self.table_start.bus_stop_obj} take {self.table_start.line_obj} at {self.table_start.time} "
            f"to {self.table_end.bus_stop_obj} at {self.table_end.time}"
        )

    def get_solution(self):
        if self.previous_ride is None:
            yield f"Started from {self.table_start.bus_stop_obj} at {self.table_start.time}"
            yield str(self)
        else:
            yield from self.previous_ride.get_solution()
            yield str(self)

    def print_solution(self):
        # print(self.get_solution())
        # print("\n".join(self.get_solution()))
        for elem in self.get_solution():
            print(elem)
        print(f"takes {self.journey_minutes} minutes")


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
    additional_depth = 1
    max_solutions_from_edge = 2
    max_solutions = 8  # only when no additional depth

    def __init__(self, start: models.BusStop, end: models.BusStop, time: datetime.time):
        self.start = start
        self.end = end
        self.time_start = time
        self.unit_to_minutes: Dict[str, int] = {}
        self.seen_time_tables_hashes = set()

        self.another_step_queue = []
        self.solution_list: List[Ride] = []
        self.solutions: Dict[int, Ride] = {}

    def solve(self):
        print(f"search from {self.start} at {self.time_start} to {self.end}")

        self.do_first_step()

        for i in range(1, self.max_depth):
            if self.solutions:
                break
            self.do_one_step(i)

        for i in range(self.additional_depth):
            self.do_one_step(i)

        for i, obj in enumerate(self.solution_list, start=1):
            print("---", i)
            obj.print_solution()

    def do_first_step(self):
        self.process_departures(self.start, self.time_start, None, unique_routes=False)

    def do_one_step(self, i):
        main_queue = sorted(
            self.another_step_queue, key=lambda obj: obj.arrival_time, reverse=True
        )
        self.another_step_queue = []
        print(f"start iteration {i} with {len(main_queue)} nodes")
        while main_queue:
            start_ride: Ride = main_queue.pop()
            self.process_departures(
                start_ride.arrival_stop, start_ride.arrival_time, start_ride, True
            )
            if len(self.solutions) > self.max_solutions and self.additional_depth == 0:
                break

    def process_departures(
        self, stop_: BusStop, time_: datetime.time, current_start, unique_routes: bool
    ):
        # if stop_ not in self.stop_to_ride or self.stop_to_ride[stop_].time_ > time_:
        # we process outgoing courses from this stop
        # if (
        #     stop_.unit in self.unit_to_ride
        # ):
        # raise Exception(self.unit_to_ride[dest.unit])
        # self.unit_to_ride[stop_.unit] += 1
        # else:
        # self.unit_to_ride[stop_.unit] = 1
        for depart in get_departures_from_unit_cached(
            stop_, time_, min_ahead=33, unique_routes=unique_routes
        ):
            # depart - course FROM stop
            # for depart in get_departures_from_unit(stop_, time_, min_ahead=33):
            # TODO now it automaticly add 1 minute
            # may happen, we will want to go back and search bigger timespan
            if depart.course_hash in self.seen_time_tables_hashes:
                continue
            self.seen_time_tables_hashes.add(depart.course_hash)
            # now we analyze stops of course taken - course TO stop
            possible_arrivals = get_route_of_one_course(depart, depart.time)
            self.analyze_arrivals(current_start, depart, possible_arrivals)

    def analyze_arrivals(
        self, current_start: Union[Ride, None], depart: TableData, possible_arrivals
    ):
        start_of_jurney = current_start.start_time if current_start else depart.time
        for possible_table in possible_arrivals:
            minutes_to_arrive = substract_times_to_minutes(possible_table.time, start_of_jurney)
            if self.skip_due_to_arrival_time(
                dest_unit=possible_table.bus_stop_obj.unit,
                minutes_to_arrive=minutes_to_arrive,
            ):
                continue

            ride = Ride(
                table_start=depart,
                table_end=possible_table,
                start_time=start_of_jurney,
                previous_ride=current_start,
                start_course_id=current_start.start_course_id if current_start else None
            )
            if possible_table.bus_stop_obj.unit == self.end.unit:
                if current_start and current_start.start_course_id in self.solutions:
                    if self.solutions[current_start.start_course_id].journey_minutes < minutes_to_arrive:
                        continue
                elif current_start is None:
                    if self.solutions[current_start].journey_minutes < minutes_to_arrive:
                        continue

                self.solutions[current_start.start_course_id if current_start else None] = ride

                self.solution_list.append(ride)
                print("solution found", ride.journey_minutes)
                break  # do not analyze other possible stops
            else:
                self.another_step_queue.append(ride)

    def skip_due_to_arrival_time(self, dest_unit, minutes_to_arrive):
        if dest_unit not in self.unit_to_minutes:
            self.unit_to_minutes[dest_unit] = minutes_to_arrive
            return False
        # not interested if arrival > 1.2 times slower than best
        if 1.2 * self.unit_to_minutes[dest_unit] < minutes_to_arrive:
            return True

        if minutes_to_arrive < self.unit_to_minutes[dest_unit]:
            self.unit_to_minutes[dest_unit] = minutes_to_arrive

        return False


pogodna_bus_stop = session.get(BusStop, 2831)
# _bus_stop = session.get(BusStop, 6991)  # cm polnocny # takes 18s
_bus_stop = session.get(BusStop, 334)  # odlewnicza takes 18s -> 13 s

# _bus_stop = session.get(BusStop, 12) # zabkowska
# _bus_stop = session.get(BusStop, 174) # ksieznej anny
# now it takes 17 seconds
with utils.Timer():
    walker = Walker(pogodna_bus_stop, _bus_stop, datetime.time(11, 45))
    walker.solve()


# TODO what can go wrong? cycles, no solution, start == end
# TODO when theres no solution?
# TODO when found first solution, dont explore 1.2 times longer

# bus stop redundantly analysed maximum count was 331. average: 24 times. No, it was just checking.
# this counted times when we had arrival on the same stop
