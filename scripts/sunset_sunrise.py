#!/usr/bin/env python3

import datetime
import requests
import sys
import time
import pytz
import textwrap
# import tzlocal

# Credit to https://sunrise-sunset.org for their free API

class TimesToday:
    """
    This class should have next_day called periodically. When next_day
    returns true - on first call or when the day changes - all the datetimes
    stored will also change.
    Attributes are stored (listed below) all in utc and local times.

    sunrise_utc
    sunrise_local
    sunset_utc
    sunset_local
    earliest_open_utc
    earliest_open_local
    latest_close_utc
    latest_close_local
    """

    def __init__(self, earliest_open_hour, earliest_open_minute,
            latest_close_hour, latest_close_minute):
        self.today = None
        self.earliest_open_hour = earliest_open_hour
        self.earliest_open_minute = earliest_open_minute
        self.latest_close_hour = latest_close_hour
        self.latest_close_minute = latest_close_minute

    # Half open interval, returns t + from_ <= now < t + to, [from_, to)
    def _now_in_period_minutes_after_datetime(self, t, from_, to):
        assert from_ < to
        assert to < 600 # If this doesn't hold likely a mistake
        # Get timezone aware utc datetime now
        now = datetime.datetime.now(tz = datetime.timezone.utc)
        from_delta = datetime.timedelta(minutes = from_)
        to_delta = datetime.timedelta(minutes = to)
        return t + from_delta <= now < t + to_delta

    # Half open interval, from_ <= x < to, [from_, to)
    def now_in_period_minutes_after_earliest_open(self, from_, to):
        return self._now_in_period_minutes_after_datetime(
                self.earliest_open_utc, from_, to)

    # Half open interval, from_ <= x < to, [from_, to)
    def now_in_period_minutes_after_latest_close(self, from_, to):
        assert to < 60
        return self._now_in_period_minutes_after_datetime(
                self.latest_close_utc, from_, to)

    def next_day_utc(self):
        # new_date = datetime.datetime.today().date()
        # Changed to utc rather than local now as sunset/rise API works on utc
        new_date = datetime.datetime.utcnow().date()
        if self.today == new_date:
            return False

        print("New day")
        self.today = new_date
        # Refresh all values
        self.sunrise_utc, self.sunset_utc = get_sunrise_sunset_datetimes_utc()
        self.sunrise_local = utc_to_local(self.sunrise_utc)
        self.sunset_local = utc_to_local(self.sunset_utc)

        self.earliest_open_local = self.sunrise_local.replace(
                hour = self.earliest_open_hour,
                minute = self.earliest_open_minute)
        if self.earliest_open_local < self.sunrise_local:
            self.earliest_open_local = self.sunrise_local

        self.latest_close_local = self.sunset_local.replace(
                hour = self.latest_close_hour,
                minute = self.latest_close_minute)
        if self.latest_close_local > self.sunset_local:
            self.latest_close_local = self.sunset_local

        self.earliest_open_utc = local_to_utc(self.earliest_open_local)
        self.latest_close_utc = local_to_utc(self.latest_close_local)
        return True

    def __str__(self):
        if self.today is None:
            return "TimesToday instance uninitialised (call self.next_day_utc)"
        return textwrap.dedent("""\
        {:<30} {}
        {:<30} {}
        {:<30} {}

        {:<30} {:02d}:{:02d}
        {:<30} {:02d}:{:02d}

        {:<30} {}
        {:<30} {}
        {:<30} {}
        {:<30} {}

        {:<30} {}
        {:<30} {}
        {:<30} {}
        {:<30} {}\
        """).format(
                "Today utc:", self.today,
                "Datetime now utc:", utc_now().replace(microsecond = 0),
                "Datetime now local:", utc_to_local(utc_now()).replace(microsecond = 0),

                "Earliest open time local:",
                    self.earliest_open_hour, self.earliest_open_minute,
                "Latest close time local:",
                    self.latest_close_hour, self.latest_close_minute,

                "Sunrise utc:", self.sunrise_utc,
                "Sunrise local:", self.sunrise_local,
                "Sunset utc:", self.sunset_utc,
                "Sunset local:", self.sunset_local,

                "Earliest open utc:", self.earliest_open_utc,
                "Earliest <b>open</b> local:          ", self.earliest_open_local,
                "Latest close utc:", self.latest_close_utc,
                "Latest <b>close</b> local:           ", self.latest_close_local,
                )
        # The above spacing for times is to bolden the open/close
        # This all comes as html, spacing for formatting, quick and dirty fix

def get_sunrise_sunset_as_times():
    # TODO: remove this version
    return tuple(map(lambda x: x.time(), get_sunrise_sunset_datetimes_utc()))

def get_sunrise_sunset_datetimes_utc():
    return tuple(map(parse_iso_datetime, download_sunrise_sunset()))

def utc_now():
    # return datetime.datetime.now(pytz.utc)
    return datetime.datetime.now(tz = datetime.timezone.utc)

def utc_to_local(utc_dt):
    # Concerned about this, doesn't look "aware"? But works for now so leave it
    return utc_dt.replace(tzinfo = datetime.timezone.utc).astimezone(tz = None)

def local_to_utc(local_dt):
    return local_dt.astimezone(pytz.utc)

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
    # Tests, daylight savings day in the UK, clocks move forward
    # Sunrise UTC : 2019-03-31 01:01:11+00:00
    # utc -> local: 2019-03-31 02:01:11+01:00
    # pytz        : 2019-03-31 02:01:11+01:00

    # return "2019-03-31T00:01:11+00:00", "2019-06-27T03:01:11+00:00"
    return result["civil_twilight_begin"], result["nautical_twilight_end"]

# def utc_to_local_pytz(utc_dt):
#     local_tz = tzlocal.get_localzone()
#     local_dt = utc_dt.replace(tzinfo = pytz.utc).astimezone(local_tz)
#     return local_tz.normalize(local_dt) # .normalize might be unnecessary

def main(argv):
    times_today = TimesToday(
            earliest_open_hour = 4, earliest_open_minute = 0,
            latest_close_hour = 22, latest_close_minute = 55,
            )
    print(times_today.next_day())
    print(times_today)
    print(times_today.now_in_period_minutes_after_earliest_open(0, 5))
    print(times_today.now_in_period_minutes_after_earliest_open(5, 10))
    print(times_today.now_in_period_minutes_after_latest_close(0, 5))
    print(times_today.now_in_period_minutes_after_latest_close(5, 10))

    # print(help(TimesToday))

   # sunrise, sunset = get_sunrise_sunset_datetimes_utc()
    # print("Sunrise     :", sunrise)
    # print("utc -> local:", utc_to_local(sunrise))
    # # print("pytz        :", utc_to_local_pytz(sunrise))
    # print("")

    # sunrise_local, sunset_local = utc_to_local(sunrise), utc_to_local(sunset)
    # print("Sunrise (UTC)  :", sunrise)
    # print("Sunrise (local):", sunrise_local)
    # print("Sunset  (UTC)  :", sunset)
    # print("Sunset  (local):", sunset_local)

    # print("")
    # # local = tzlocal.get_localzone()
    # # print("local:", local)
    # # local_dt = local.localize(sunrise)
    # # print("local_dt:", local_dt)
    # utc_dt = local_to_utc(sunrise_local)
    # print("utc_dt:", utc_dt)

    # early = sunrise_local.replace(hour = 5, minute = 30)
    # if early > sunrise_local:
    #     print("Would use early:", early)

    # late = sunset_local.replace(hour = 22, minute = 55)
    # if late < sunset_local:
    #     print("Would use late:", late)

if __name__ == "__main__":
    sys.exit(main(sys.argv))
