#!/usr/bin/env python3

import datetime
import json
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
from json_socket import JsonSocket

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

    wall_door = Door("wall",
            input_bottom = InputPin(3), input_top = InputPin(5),
            output_open = OutputPin(37), output_close = OutputPin(8))
    near_door = Door("near",
            input_bottom = InputPin(10), input_top = InputPin(11),
            output_open = OutputPin(12), output_close = OutputPin(13))
    camera = Camera(OutputPin(15), timeout_sec = 99999)
    camera.on()

    logger = get_console_and_file_logger("/home/pi/temperature.log")

    logger.info("Started")

    logger.info("Starting jsonsocket")
    json_socket = JsonSocket(2520)
    logger.info("jsonsocket started successfully")

    #TESTING THIS
    try:
        sunrise, sunset = datetime.time(8, 0), datetime.time(21, 0)
        # Download new sunrise/sunset times on switch on or on day change
        heater = Heater(1.0, 3.0, pin = OutputPin(40),
                thermometer = Thermometer())
        record_temp_timer = DoneTimer(300)
        bool_to_str = lambda x: "on" if x else "off"
        last_date = None
        doors = [wall_door, near_door]
        door_actions = ["open", "stop", "close", "check_position"]

#         for door in doors:
#             door.close()
#         time.sleep(80)
#         input("Done closing doors")

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
            # TODO; changed this for now so it doesn't open so early
            # Think of elegant solution for this for summer/winter split
            if is_now_in_time_period(add_time(sunrise, minutes = 90), add_time(sunrise, minutes = 100)):
                logger.info("Doors will not be opened automatically for now.")
                # logger.info("Opening doors")
                # wall_door.open()
                # near_door.open()
            if is_now_in_time_period(sunset, add_time(sunset, minutes = 10)):
                logger.info("Closing doors")
                wall_door.close()
                near_door.close()
            else:
                print("Time now:", datetime.datetime.utcnow().time(), "vs sunset:", sunset)

            if is_now_in_time_period(datetime.time(0, 0), datetime.time(0, 5)):
                # Print blank line
                # or end of day
                logger.info("")

            wall_door.poll()
            near_door.poll()

            # for door in doors:
            #     print(door.name())
            #     print("Is open:", door.is_fully_open())
            #     print("Is middle:", door.is_in_middle())
            #     print("Is closed:", door.is_closed())

            # Setting this timer high is an easy way to stall the loop when
            # the website is not being used
            json_in = json_socket.read(timeout = 30)
            if json_in is not None:
                reply = json_response(json_in, doors = doors,
                        door_actions = door_actions,
                        sunset = sunset, sunrise = sunrise)
                logger.info("json_socket read in \"" + str(json_in) + "\"")
                if reply is not None:
                    logger.info("Replying with " + str(reply))
                    json_socket.write(reply)
                    print("Done writing out reply")

            time.sleep(0.1)
    except Exception as e:
        logger.exception(e)
        raise
    finally:
        json_socket.close()

def json_response(json_in, **kwargs):
    if json_in is None:
        return None

    # At least for now
    doors = kwargs["doors"]
    door_actions = kwargs["door_actions"]
    sunset = kwargs["sunset"]
    sunrise = kwargs["sunrise"]

    obj_out = {}
    if "request" not in json_in:
        obj_out["status"] = "Unknown input - no key \"request\""
        return json.dumps(obj_out)

    request = json_in["request"]
    if request == "list_doors":
        response = {}

        response["doors"] = []
        for door in doors:
            response["doors"].append(
                    {
                        "door_name": door.name(),
                        "door_actions": door_actions,
                        })

        response["sunset"] = str(sunset)
        response["sunrise"] = str(sunrise)
        obj_out["response"] = response
    elif request == "door_action":
        door_name = json_in["door_name"]
        door_action = json_in["door_action"]
        status_message_out = ""

        if door_name.casefold() not in [d.name().casefold() for d in doors]:
            status_message_out = "Door called " + door_name + " not in doors: [" + \
                    ", ".join(d.name() for d in doors) + "]"
        elif door_action not in door_actions:
            status_message_out = "Action called " + door_action + \
                    " not in actions: [" + ", ".join(door_actions) + "]"
        else:
            door = doors[[i for i, d in enumerate(doors) if d.name() == door_name][0]]
            if door_action == "open":
                door.open()
            elif door_action == "close":
                door.close()
            elif door_action == "stop":
                door.stop()
            elif door_action == "check_position":
                pass
            status_message_out = str(door)
        obj_out["status"] = status_message_out
    return json.dumps(obj_out)

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
