#!/usr/bin/env python3

import sys

import utils

import RPi.GPIO as GPIO

from pins import OutputPin
from thermometer import Thermometer

# Thinking again - if this can throw anytime temp is read, that is annoying
# Have to see if ever throws in practice

class Heater:
    def __init__(self, lo_temp, hi_temp, *, pin, thermometer):
        assert type(pin) is OutputPin
        assert type(thermometer) is Thermometer
        assert lo_temp < hi_temp
        self._lo_temp = lo_temp
        self._hi_temp = hi_temp
        self._pin = pin
        self._thermometer = thermometer

        # In case we start with temp between lo and hi, turn on
        if self._lo_temp <= self.read_temperature() <= self._hi_temp:
            self.on()

    # Actions
    def on(self):
        self._pin.on()
    def off(self):
        self._pin.off()

    def state(self):
        return self._pin.state()
    # Dislike this wrapping... Heater(OutputPin)?
    def read_temperature(self):
        return self._thermometer.read_temperature()

    # Returns True if heater is turned on or off, else False
    # Reads temperature which may raise exception
    def poll(self):
        temp = self._thermometer.read_temperature()
        if temp < self._lo_temp and not self._pin:
            self._pin.on()
            return True
        elif temp > self._hi_temp and self._pin:
            self._pin.off()
            return True
        return False

if __name__ == "__main__":
    sys.exit(main(sys.argv))

