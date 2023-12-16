import datetime
from datetime import datetime, timedelta
import random
import time


def current_time_milliseconds():
    time.sleep(1)
    # Get the current time
    current_time_seconds = time.time()
    # Convert seconds to milliseconds
    in_milliseconds = int(current_time_seconds * 10000)
    # milliseconds_slice = str(milliseconds)[-6:]

    return in_milliseconds


def key_id():
    uuid = str(random.randint(1111, 99999)) + str(current_time_milliseconds())[-5:]
    return uuid


def time_remaining(end_time):
    end_time_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    time_remaining = end_time_dt - current_time

    # Check if the time difference is less than or equal to zero
    if time_remaining.total_seconds() <= 0:
        return timedelta(seconds=0)  # Return zero if time has already passed
    else:
        return time_remaining