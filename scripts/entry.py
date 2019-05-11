#!/usr/bin/env python3

import datetime
import time
import sys

from pins import InputPin, OutputPin
from door import Door
from camera import Camera
from heater import Heater
from thermometer import Thermometer
from my_logger import get_console_and_file_logger
from donetimer import DoneTimer
from sunset_sunrise import get_sunrise_sunset_as_times

import utils
utils.setup_gpio()
import RPi.GPIO as GPIO

# TODO: logger send raw or just send newline
# Finish this lel, for example make a timer firing thing to replace crappy 5
# minute interval stuff
# Probably loads more crap but I forget atm.
# Oh yeh website frontend dur.
# Change hard coded door closing times to either be pulled from a light sensor
# (to be bought) or pull data from web
# eg. https://www.thetimeandplace.info/uk/london-city-of-london

def main(argv):

    wall_door = Door("wall door",
            input_bottom = InputPin(3), input_top = InputPin(5),
            output_open = OutputPin(37), output_close = OutputPin(8))
    near_door = Door("near door",
            input_bottom = InputPin(10), input_top = InputPin(11),
            output_open = OutputPin(12), output_close = OutputPin(13))
    camera = Camera(OutputPin(15), timeout_sec = 99999)
    camera.on()

    logger = get_console_and_file_logger("/home/pi/temperature.log")

    logger.info("Started")

    #TESTING THIS
    try:
        sunrise, sunset = datetime.time(8, 0), datetime.time(21, 0)
        # Download new sunrise/sunset times on switch on or on day change
        heater = Heater(1.0, 3.0, pin = OutputPin(40),
                thermometer = Thermometer())
        record_temp_timer = DoneTimer(300)
        bool_to_str = lambda x: "on" if x else "off"
        last_date = None

        while True:

            # For things that run once per day when day changes or when
            # switched on
            if last_date != datetime.datetime.today().date():
                last_date = datetime.datetime.today().date()
                sunrise, sunset = get_sunrise_sunset_as_times()
                logger.info("New sunrise time: " + str(sunrise) + " and sunset time: " +
                        str(sunset))

            if heater.poll():
                logger.info("Heater now " + bool_to_str(heater.state()) +
                        " as temperature now " +
                        str(heater.read_temperature()))
            elif record_temp_timer.is_done()[0]:
                logger.debug("Temperature (celsius): " +
                        str(heater.read_temperature()))
                record_temp_timer.reset()

            # if is_now_in_time_period(datetime.time(7, 0), datetime.time(7, 5)):
            if is_now_in_time_period(sunrise, add_time(sunrise, minutes = 10)):
                logger.info("Opening doors")
                wall_door.open()
                near_door.open()
            if is_now_in_time_period(sunset, add_time(sunset, minutes = 10)):
                logger.info("Closing doors")
                wall_door.close()
                near_door.close()
            # if is_now_in_time_period(datetime.time(0, 0), datetime.time(0, 5)):
            #     # Print blank line for end of day
            #     logger.info("")
            wall_door.poll()
            near_door.poll()
            time.sleep(60)
    except Exception as e:
        logger.exception(e)
        raise

# https://stackoverflow.com/a/100345
def add_time(dt_time, **kwargs):
    # Date is irrelevant
    return (datetime.datetime.combine(datetime.date(2000, 1, 1), dt_time) + \
            datetime.timedelta(**kwargs)).time()

# https://stackoverflow.com/a/38836918
def is_now_in_time_period(start_time, end_time, now_time = None):
    if now_time is None:
        now_time = datetime.datetime.utcnow().time()
        # now_time = datetime.datetime.now()
    if start_time < end_time:
        return now_time >= start_time and now_time <= end_time
    else: #Over midnight
        return now_time >= start_time or now_time <= end_time

if __name__ == "__main__":
    sys.exit(main(sys.argv))
