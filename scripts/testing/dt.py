#!/usr/bin/env python3

import sys
import datetime

# https://stackoverflow.com/a/38836918
def is_now_in_time_period(start_time, end_time, now_time = None):
    if now_time is None:
        now_time = datetime.datetime.now().time()
    if start_time < end_time:
        return now_time >= start_time and now_time <= end_time
    else: #Over midnight
        return now_time >= start_time or now_time <= end_time

def main(argv):
    print(is_now_in_time_period(datetime.time(8, 30), datetime.time(8, 32), datetime.time(8,31)))
    print("Hello world!")

if __name__ == "__main__":
    sys.exit(main(sys.argv))
