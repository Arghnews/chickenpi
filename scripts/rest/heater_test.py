#!/usr/bin/env python3

import signal # catch kill 15 SIGTERM
import time # for sleeping, camera timer
import enum # door positions
#from listen import net # my net
import listen # my simple networking script
from functools import partial

try:
    import RPi.GPIO as GPIO
    print("Successfully imported RPi.GPIO")
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
    exit(1)

class Door:
    Sleep_Time = 20.0 / 1000.0 # x / 1000.0, x in ms
    def __init__(
            self,
            in_low,
            in_up,
            d_open,
            d_close,
            active_low=True,
            movement_time_s=80):

        pins = [in_low,in_up,d_open,d_close]
        if len(pins) > len(set(pins)):
            raise RuntimeError("Input/output pins are not all different")

        self.in_low = in_low
        self.in_up = in_up

        self.d_open = d_open
        self.d_close = d_close

        # just for outputs
        self.active_low = active_low
        self.On = GPIO.LOW if self.active_low else GPIO.HIGH
        self.Off = GPIO.HIGH if self.active_low else GPIO.LOW

        # door takes 60 seconds to open/shut
        self.movement_time_s = movement_time_s

        self.last_action = 0

        # input channels
        GPIO.setup(self.in_low, GPIO.IN)
        time.sleep(Door.Sleep_Time)
        GPIO.setup(self.in_up, GPIO.IN)
        time.sleep(Door.Sleep_Time)

        # output channels
        GPIO.setup(self.d_open, GPIO.OUT, initial=self.Off)
        time.sleep(Door.Sleep_Time)
        GPIO.setup(self.d_close, GPIO.OUT, initial=self.Off)
        time.sleep(Door.Sleep_Time)
        print("Done constructing")

    def action_open(self):
        # stop closing
        GPIO.output(self.d_close, self.Off)

        GPIO.output(self.d_open, self.On)
        self.log_action()

class Camera:

    # for now (quick job) always active low = on
    def __init__(self,pin,seconds_on=900):
        self.pin = pin
        self.seconds_on = seconds_on
        self.timer = 0
        # start off initially
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)

    # should be called to switch on camera
    def on(self):
        self.timer = int(time.time()) + self.seconds_on
        GPIO.output(self.pin, GPIO.LOW)

    # should be called every poll/regularly
    def poll(self):
        if self.timer == 0:
            return

        time_now = int(time.time()) # epoch
        if time_now > self.timer:
            self.timer = 0
            # switch off camera
            GPIO.output(self.pin, GPIO.HIGH)
        


def main():
    GPIO.setmode(GPIO.BOARD)
    try:
        pin = 40
        GPIO.setup(pin, GPIO.OUT)
        #GPIO.output(pin, GPIO.LOW)
        GPIO.output(pin, GPIO.HIGH)
        while 1:
            pass
    except:
        raise
    finally:
        print("Cleaning up")
        GPIO.cleanup()
    print("Exiting")

if __name__ == '__main__':
    main()
