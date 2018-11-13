#!/usr/bin/env python3

from __future__ import print_function

import glob
import os
import subprocess
import sys
import time
import my_logger

def read_temp(device_file):
    # Retry if doesn't work
    for _ in range(5):
        lines = read_temp_raw(device_file)
        if lines and len(lines) > 1 and \
                lines[0].endswith("YES") and "t=" in lines[1]:
            temp_string_pos = lines[1].index("t=") + 2
            temp_string = float(lines[1][temp_string_pos:]) / 1000.0
            return temp_string
        time.sleep(1)
    return None

def read_temp_raw(device_file):
    cmd = ["cat", device_file]
    catdata = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = catdata.communicate()
    out_decode = out.decode("utf-8")
    lines = [line for line in out_decode.split("\n") if line]
    return lines

def eprint(*args, **kwargs):
    import sys
    print(*args, file=sys.stderr, **kwargs)

if os.geteuid() != 0:
    eprint("Must be run as root - exiting")
    sys.exit(1)

try:
    import RPi.GPIO as GPIO
    print("Successfully imported RPi.GPIO")
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
    exit(1)

GPIO.setmode(GPIO.BOARD)

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")
#os.system("dtoverlay w1-gpio gpiopin=10 pullup=0")

# In addition to tutorial stuff and these and editting /boot/config.txt
# and adding sudo dtoverlay w1-gpio gpiopin=10 pullup=0
# Had to use to set pin 19 on board, 10 outside
# sudo dtoverlay w1-gpio gpiopin=10 pullup=0
# Now using default pin - inboard 7

base_dir = "/sys/bus/w1/devices/"
device_folder = glob.glob(base_dir + "28*")[0]
device_file = device_folder + "/w1_slave"

def main(argv):
    logger = my_logger.get_console_and_file_logger("/home/pi/temperature.log")

    # Active low
    ON, OFF = GPIO.LOW, GPIO.HIGH

    heater = 40
    logger.info("Heater on pin " + str(heater))
    GPIO.setup(heater, GPIO.OUT, initial=OFF)

    on_temp = 1.0
    off_temp = 2.5
    logger.info("Temperature on/off thresholds in degrees C: " +
            str(on_temp) + "/" + str(off_temp))

    try:
        assert(on_temp <= off_temp)

        while 1:
            temp = read_temp(device_file)
            if not temp:
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

#def read_temp_raw():
#    with open(device_file, "r") as f:
#        return f.readlines()

