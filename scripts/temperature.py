#!/usr/bin/env python3

import glob
import os
import subprocess
import sys
import time

import my_logger
import utils

# FIXME: better name
def check_boot_config():
    with open("/boot/config.txt", "r") as f:
        if not any(line.startswith("dtoverlay=w1-gpio")
                for line in f.read().splitlines()):
            raise RuntimeError("/boot/config.txt doesn't contain "
                    "\"dtoverlay=w1-gpio\" line")

def _init():
    utils.import_gpio()
    check_boot_config()
    os.system("modprobe w1-gpio")
    os.system("modprobe w1-therm")
    # TODO:
    # Check exit codes of these, should both be 0
    # Assert that /sys/bus/w1/devices/28*/w1_slave exists
    # Rewrite this as class
    # CANDO: change Popen from spawning a process every time
    # to a thread that waits and gets signalled somehow to read it and get
    # result but need timeout in case that thread hangs and then need
    # to be able to kick it out from that hanging

_init()

def main(argv):
    base_dir = "/sys/bus/w1/devices/"
    device_folder = glob.glob(base_dir + "28*")[0]
    device_file = device_folder + "/w1_slave"
    cmd = ["cat", "/sys/bus/w1/devices/28-0316a4bd7aff/w1_slave"]
    cmd = ["cat", "/var/www/html/scripts/camera.py"]
    #res = run_cmd(cmd)
    #res = read_temp_raw("/sys/bus/w1/devices/28-0316a4bd7aff/w1_slave")
    res = read_temp_raw("/var/www/html/scripts/a.out")
    #print("[" + res + "]") #print(res.stdout)
    pass

def read_temp(device_file):
    # Retry if doesn't work
    for _ in range(5):
        try:
            return parse_temp_from_raw(device_file)
        except RuntimeError as e:
            eprint(str(e))
        time.sleep(0.5)
    # If it hasn't worked by now, try again - if it throws this time
    # we'll let it be raised as something may have really gone wrong
    return parse_temp_from_raw(device_file)

def parse_temp_from_raw(device_file):
    lines = read_temp_raw(device_file)
    if lines and len(lines) > 1 and \
            lines[0].endswith("YES") and "t=" in lines[1]:
        temp_string_pos = lines[1].index("t=") + 2
        return float(lines[1][temp_string_pos:]) / 1000.0
    return float("nan")

# Runs a list as a shell cmd, throws RuntimeError containing the error string
# if the cmd fails
def run_cmd(cmd):
    result = subprocess.run(cmd, timeout = 2, shell = True,
            stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return result

def read_temp_raw(device_file):
    cmd = ["cat", device_file]
    cmd = ["sleep", "5"]
    cmd = ["ping", "1.1.2.2", "-c", "1"]
    cmd = ["/var/www/html/scripts/a.out"]
    try:
        subp = subprocess.Popen(cmd, shell = True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines = True)
        out, err = subp.communicate(timeout = 3)
    except subprocess.TimeoutExpired as e:
        raise

    if subp.returncode != 0:
        raise 
        print(dir(subp))
        print("err:" + err)
    else:
        print("output:" + out)

os.system("modprobe w1-gpio")
os.system("modprobe w1-therm")
#os.system("dtoverlay w1-gpio gpiopin=10 pullup=0")

# In addition to tutorial stuff and these and editting /boot/config.txt
# Prerequisite:
# Add "dtoverlay w1-gpio" into /boot/config.txt and reboot
# Can use "sudo dtoverlay w1-gpio gpiopin=10 pullup=0" to mask pin to also use gpio 10
# and adding 
# Had to use to set pin 19 on board, 10 outside
# sudo dtoverlay w1-gpio gpiopin=10 pullup=0
# Now using default pin - inboard 7

base_dir = "/sys/bus/w1/devices/"
device_folder = glob.glob(base_dir + "28*")[0]
device_file = device_folder + "/w1_slave"

def mayn(argv):
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
        assert on_temp <= off_temp

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

