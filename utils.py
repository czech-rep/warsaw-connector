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


def add_timedelta_to_time(
    t: datetime.time, delta: datetime.timedelta
) -> datetime.time:
    added = datetime.datetime.combine(datetime.date.today(), t) + delta
    return added.time()
    # TODO implement inequality search in table of hours that support all hours

def add_minutes_to_hour(t, minutes):
    return add_timedelta_to_time(t, datetime.timedelta(minutes=minutes))
