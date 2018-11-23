#!/usr/bin/env python3

import time
import sys

from pins import InputPin, OutputPin
from door import Door
from camera import Camera
from heater import Heater
from thermometer import Thermometer
from my_logger import get_console_and_file_logger
from donetimer import DoneTimer

import utils
utils.setup_gpio()
import RPi.GPIO as GPIO

def main(argv):

    # wall_door = Door("wall door",
    #         input_bottom = InputPin(3), input_top = InputPin(5),
    #         output_open = OutputPin(37), output_close = OutputPin(8))
    # near_door = Door("near door",
    #         input_bottom = InputPin(10), input_top = InputPin(11),
    #         output_open = OutputPin(12), output_close = OutputPin(13))

    # camera = Camera(OutputPin(15))

    logger = get_console_and_file_logger("/home/pi/temperature.log")

    try:
        heater = Heater(1.0, 4.0, pin = OutputPin(40),
                thermometer = Thermometer())
        record_temp_timer = DoneTimer(300)
        bool_to_str = lambda x: "on" if x else "off"
        while True:
            if heater.poll():
                logger.info("Heater now " + bool_to_str(heater.state()) +
                        " as temperature now " +
                        str(heater.read_temperature()))
            elif record_temp_timer.is_done()[0]:
                logger.info("Temperature (celsius): " +
                        str(heater.read_temperature()))
                record_temp_timer.reset()
            time.sleep(60)
    except Exception as e:
        logger.error(str(e))
        raise

    # input("Press key to close doors")
    # wall_door.close()
    # near_door.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))
