#!/usr/bin/env python3

import datetime
import requests
import sys
import time

# Credit to https://sunrise-sunset.org for their free API

def parse_iso_datetime(datetime_str):
    # https://en.wikipedia.org/wiki/ISO_8601 - but can't have ":" in offset
    # before Python 3.7 so must remove it
    # datetime_str = "2015-05-21T04:36:17+00:00"
    if datetime_str[-3] == ":":
        datetime_str = datetime_str[:-3] + datetime_str[-2:]
    date_time = datetime.datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S%z")
    return date_time

def download_sunrise_sunset():
    payload = {"lat": 51.416039, "lng": -0.753980, "formatted": 0,}
    result = requests.get("https://api.sunrise-sunset.org/json",
        params = payload)
    result.raise_for_status() # Throws if something went wrong
    result = result.json()["results"]
    # Civil twilight begin to open a little earlier, nautical to close a little
    # later
    return result["civil_twilight_begin"], result["nautical_twilight_end"]

def get_sunrise_sunset_as_times():
    return tuple(map(
        lambda x: parse_iso_datetime(x).time(), download_sunrise_sunset()))

def main(argv):
    print(get_sunrise_sunset())

if __name__ == "__main__":
    sys.exit(main(sys.argv))
