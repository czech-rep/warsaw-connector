import time
import datetime


class Timer:
    def __init__(self, subject=""):
        self.subject = subject

    def __enter__(self):
        self.t0 = time.perf_counter()

    def __exit__(self, *args, **kwargs):
        measured = time.perf_counter() - self.t0
        print(f"- {self.subject} measured {self.format_minutes(measured)}")

    def format_minutes(self, seconds_count):
        return f"{seconds_count//60:.0f} min {seconds_count%60:.1f} s"


def add_timedelta_to_time(t: datetime.time, delta: datetime.timedelta) -> datetime.time:
    added = datetime.datetime.combine(datetime.date.today(), t) + delta
    return added.time()
    # TODO implement inequality search in table of hours that support all hours (after midnight)


def add_minutes_to_hour(t, minutes):
    return add_timedelta_to_time(t, datetime.timedelta(minutes=minutes))


def substract_times_to_minutes(t1: datetime.time, t2: datetime.time):
    diff_hours = t1.hour - t2.hour
    if diff_hours < 0:
        diff_hours += 24
    return 60 * diff_hours + t1.minute - t2.minute
