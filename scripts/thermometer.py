#!/usr/bin/env python3

import glob
import os
import subprocess
import sys
import time

import utils

class Thermometer:

    def __init__(self,
            base_dir = "/sys/bus/w1/devices/",
            device_glob = "28*",
            device_filename = "w1_slave"):
        assert file_has_line_starting_with("/boot/config.txt",
                "dtoverlay=w1-gpio")
        if not file_has_line_starting_with("/proc/modules", "w1_gpio"):
            subprocess.run(["sudo", "modprobe", "w1_gpio"], check = True)
        if not file_has_line_starting_with("/proc/modules", "w1_therm"):
            subprocess.run(["sudo", "modprobe", "w1_therm"], check = True)
        device_dir = glob.glob(os.path.join(base_dir, device_glob))
        if not device_dir or len(device_dir) > 1:
            raise RuntimeError("Expected one temperature probe dir in " +
                    base_dir)
        device_filepath = os.path.join(device_dir[0], device_filename)
        if not os.path.isfile(device_filepath):
            raise RuntimeError("Cannot find temperature probe file " +
                    device_filepath)
        self._temperature_file = device_filepath

    def read_temperature(self):
        return read_temp(self._temperature_file)

    # Dislike print being able to throw
    # Could fix with caching last temp - complexity
    # Using non-throwing variant that returns None - meh
    # Will see - if this ever actually throws then may
    # come back and implement non-throwing variant
    #def __str__(self):

def file_has_line_starting_with(filepath, prefix):
    with open(filepath, "r") as f:
        return any(line.startswith(prefix)
                for line in f.read().splitlines())

# Returns temp float in celsius or raises exception
def read_temp(device_file):
    # Retry if doesn't work
    for _ in range(4):
        try:
            return parse_temp_from_raw(device_file)
        except Exception as e:
            utils.eprint(str(e))
        time.sleep(0.5)
    # If it hasn't worked by now, try again - if it throws this time
    # we'll let it be raised as something may have really gone wrong
    return parse_temp_from_raw(device_file)

# Either returns float or raises exception
def parse_temp_from_raw(device_file):
    lines = read_temp_raw(device_file).splitlines()
    if lines and len(lines) > 1 and \
            lines[0].endswith("YES") and "t=" in lines[1]:
        temp_string_pos = lines[1].find("t=")
        if temp_string_pos != -1:
            return float(lines[1][temp_string_pos + 2:]) / 1000.0
    raise RuntimeError("Could not parse temp from output: \"" +
            "\n".join(lines) + "\"")

# Either returns output string or raises exception
def read_temp_raw(device_file):
    cmd = ["cat", device_file]
    error = None
    try:
        subp = subprocess.Popen(cmd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines = True)
        stdout, stderr = subp.communicate(timeout = 3)
    except subprocess.TimeoutExpired as e:
        error = e

    error_message = None
    if error:
        error_message = str(error)
    elif stderr or subp.returncode != 0:
        error_message = "Error, command \"" + " ".join(cmd) + \
                "\" exited with exit status " + str(subp.returncode) + \
                " and error message: \"" + stderr + "\""

    if error_message:
        raise RuntimeError(error_message)

    return stdout.rstrip()

def main(argv):
    t = Thermometer()
    print(t.read_temperature())

if __name__ == "__main__":
    sys.exit(main(sys.argv))


