#!/usr/bin/env python3

import datetime
import json
import sys
import time

import camera
import datetime
import donetimer
import door
import heater
import json_socket
import my_logger
import pins
import sunset_sunrise
import weather
# from thermometer import Thermometer

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

# FIXME: heater disabled as not showing up in /sys/bus/w1/devices/28* is what looking for -_-

def main(argv):

    wall_door = door.Door("wall",
            input_bottom = pins.InputPin(3), input_top = pins.InputPin(5),
            output_open = pins.OutputPin(37), output_close = pins.OutputPin(8))
    near_door = door.Door("near",
            input_bottom = pins.InputPin(10), input_top = pins.InputPin(11),
            output_open = pins.OutputPin(12), output_close = pins.OutputPin(13))
    camera = pins.OutputPin(15, initial = True)
    heater = pins.OutputPin(40, initial = False)

    logger = my_logger.get_console_and_file_logger("/home/pi/temperature.log")

    logger.info("Started")

    logger.info("Starting jsonsocket")
    json_sock = json_socket.JsonSocket(2520)
    logger.info("jsonsocket started successfully")

    #TESTING THIS
    try:
        sunrise, sunset = datetime.time(8, 0), datetime.time(21, 0)
        times_today = sunset_sunrise.TimesToday(
                earliest_open_hour = 4, earliest_open_minute = 0,
                latest_close_hour = 22, latest_close_minute = 55,
                )
        api_key = weather.read_api_key_from_file("weatherstack_api_key")
        temperature_celsius = weather.download_temperature_now_from_weatherstack(
                api_key)
        heater_on_threshold_temperature = 4
        door_opening_time_seconds = weather.calculate_door_open_time(
                temperature_celsius)
        # Download new sunrise/sunset times on switch on or on day change
        # heater = heater.Heater(1.0, 3.0, pin = pins.OutputPin(40),
        #         thermometer = Thermometer())
        record_temp_timer = donetimer.DoneTimer(300)
        bool_to_str = lambda x: "on" if x else "off"
        doors = [wall_door, near_door]
        door_actions = ["open", "stop", "close", "check_position"]
        heater_active = False
        # Bit messy this one. Should make idempotent on/off pin wrapper really
        # that when on is called twice on a pin doesn't put the call through
        # the second time.
        heater_last_state = None

#         for door in doors:
#             door.close()
#         time.sleep(80)
#         input("Done closing doors")

        while True:

            # For things that run once per day when day changes or when
            # switched on
            if times_today.next_day_utc():
                logger.info("\nNew day (utc)")
                logger.info(str(times_today))
                temperature_celsius = weather.download_temperature_now_from_weatherstack(
                        api_key)
                logger.info("Temperature recorded as: "
                        + str(temperature_celsius))
                door_opening_time_seconds = weather.calculate_door_open_time(
                        temperature_celsius)
                logger.info("Door opening time calculated as:" +
                        str(door_opening_time_seconds))
                heater_active = temperature_celsius <= heater_on_threshold_temperature
                logger.info("Heater threshold temperature: "
                    + str(heater_on_threshold_temperature))
                if heater_active:
                    logger.info("Enabling heater based on temperature")

            # If temperature when recorded was below threshold
            # Simple way to switch on for 5 mins then off for 5 mins
            if heater_active and bool((datetime.datetime.now().minute % 10) // 5):
                if not heater_last_state:
                    logger.debug("Switching heater on")
                    heater.on()
                    heater_last_state = True
            else:
                if heater_last_state:
                    logger.debug("Switching heater off")
                    heater.off()
                    heater_last_state = False
            # if heater.poll():
            #     logger.info("Heater now " + bool_to_str(heater.state()) +
            #             " as temperature now " +
            #             str(heater.read_temperature()))
            # elif record_temp_timer.is_done()[0]:
            #     logger.debug("Temperature (celsius): " +
            #             str(heater.read_temperature()))
            #     record_temp_timer.reset()

            # TODO: when enabling door opening again, copy closing time idiom
            # if is_now_in_time_period(datetime.time(7, 0), datetime.time(7, 5)):
            # TODO; changed this for now so it doesn't open so early
            # Think of elegant solution for this for summer/winter split
            if times_today.now_in_period_seconds_after_earliest_open(
                    0, door_opening_time_seconds):
                logger.info("Opening door:" + str(wall_door))
                wall_door.open()
            elif times_today.now_in_period_seconds_after_earliest_open(
                    door_opening_time_seconds, 2 * door_opening_time_seconds):
                logger.info("Stopping (opened):" + str(wall_door))
                wall_door.stop()

            if times_today.now_in_period_seconds_after_earliest_open(
                    2 * door_opening_time_seconds, 3 * door_opening_time_seconds):
                logger.info("Opening door:" + str(near_door))
                near_door.open()
            elif times_today.now_in_period_seconds_after_earliest_open(
                    3 * door_opening_time_seconds, 4 * door_opening_time_seconds):
                logger.info("Stopping (opened):" + str(near_door))
                near_door.stop()

            # With door actuators sharing circuitry with food ones only close
            # or open one door at a time
            # TODO: same with open once we are opening doors again
            if times_today.now_in_period_minutes_after_latest_close(0, 5):
                logger.info("Closing wall (far) door")
                wall_door.close()
            if times_today.now_in_period_minutes_after_latest_close(5, 10):
                logger.info("Closing near door")
                near_door.close()

            wall_door.poll()
            near_door.poll()

            # for door in doors:
            #     print(door.name())
            #     print("Is open:", door.is_fully_open())
            #     print("Is middle:", door.is_in_middle())
            #     print("Is closed:", door.is_closed())

            # Setting this timer high is an easy way to stall the loop when
            # the website is not being used
            json_in = json_sock.read(timeout = 5)
            if json_in is not None:
                reply = json_response(json_in, doors = doors,
                        door_actions = door_actions,
                        times_today = times_today)
                logger.info("json_sock read in \"" + str(json_in) + "\"")
                if reply is not None:
                    logger.info("Replying with " + str(reply))
                    json_sock.write(reply)
                    logger.info("Done writing out reply")

            time.sleep(0.1)
    except Exception as e:
        logger.exception(e)
        raise
    finally:
        json_sock.close()

def json_response(json_in, **kwargs):
    if json_in is None:
        return None

    # At least for now
    doors = kwargs["doors"]
    door_actions = kwargs["door_actions"]
    times_today = kwargs["times_today"]
    # sunrise = times_today.sunrise
    # sunset = times_today.sunset

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

        # response["sunrise"] = str(sunrise)
        # response["sunset"] = str(sunset)
        # Quick hack for now, with html pre tags for unformatted
        response["times_today_str"] = "<pre>" + str(times_today) + "</pre>"
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
