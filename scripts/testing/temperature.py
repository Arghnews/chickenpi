#!/usr/bin/env python3

import glob
import os
import subprocess
import sys
import time

import my_logger
import utils

import RPi.GPIO as GPIO

from pins import InputPin, OutputPin
from door import Door
import datetime

# https://stackoverflow.com/a/38836918
def is_now_in_time_period(start_time, end_time, now_time = None):
    if now_time is None:
        now_time = datetime.datetime.now().time()
    if start_time < end_time:
        return now_time >= start_time and now_time <= end_time
    else: #Over midnight
        return now_time >= start_time or now_time <= end_time

def mayn(argv):
    logger = my_logger.get_console_and_file_logger("/home/pi/temperature.log")
    from RPi import GPIO

    # Active low
    ON, OFF = GPIO.LOW, GPIO.HIGH

    heater = 40
    logger.info("Heater on pin " + str(heater))
    GPIO.setup(heater, GPIO.OUT, initial=OFF)

    on_temp = 1.0
    off_temp = 2.5
    logger.info("Temperature on/off thresholds in degrees C: " +
            str(on_temp) + "/" + str(off_temp))

    wall_door = Door("wall door",
            input_bottom = InputPin(3), input_top = InputPin(5),
            output_open = OutputPin(37), output_close = OutputPin(8))
    near_door = Door("near door",
            input_bottom = InputPin(10), input_top = InputPin(11),
            output_open = OutputPin(12), output_close = OutputPin(13))
    try:
        assert on_temp <= off_temp
        if is_now_in_time_period(datetime.time(9), datetime.time(9, 5)):
            logger.info("Opening doors")
            wall_door.open()
            near_door.open()
        while True:
            temp = read_temp(device_file)
            # if not temp # TEMP MAY BE uyy0
            if temp is None:
                logger.warning("Error reading temperature")
            else:
                log_temp_str = "Read temperature as " + str(temp)
                if temp <= on_temp:
                    log_temp_str += " - setting heater on"
                    GPIO.output(heater, ON)
                elif temp >= off_temp:
                    log_temp_str += " - setting heater off"
                    GPIO.output(heater, OFF)
                logger.info(log_temp_str)

            time.sleep(60)
    except Exception as e:
        logger.critical("Exception raised: " + str(e))
    finally:
        logger.info("Cleaning up and turning off heater")
        GPIO.output(heater, OFF)
        GPIO.cleanup()
    logger.info("Done - exiting")

if __name__ == "__main__":
    sys.exit(main(sys.argv))

