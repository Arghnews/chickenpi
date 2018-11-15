#!/usr/bin/env python3

import atexit
import sys
import time
from enum import Enum
from abc import ABC, abstractmethod

import utils

utils.import_gpio()

@atexit.register
def cleanup_gpio():
    print("Cleaning gpio pins")
    GPIO.cleanup()

# Only thing I'm not so keen on is initally the state is None
# which in comparisons can often seem like false/off... oh well

def is_one_of(t, *types):
    return any(map(lambda tt: t is tt, types))

class Pin(ABC):
    def __init__(self, number, active_state):
        assert is_one_of(active_state, GPIO.LOW, GPIO.HIGH)
        self._number = number
        if active_state == GPIO.LOW:
            self._On, self._Off = GPIO.LOW, GPIO.HIGH
        elif active_state == GPIO.HIGH:
            self._On, self._Off = GPIO.HIGH, GPIO.LOW
    def __bool__(self):
        return self.state()
    @abstractmethod
    def state(self):
        pass
    def __str__(self):
        return "pin: " + str(self._number) + ", state: " + str(self.state())

class InputPin(Pin):
    def __init__(self, number, *, active_state=GPIO.HIGH):
        super().__init__(number, active_state)
        GPIO.setup(self._number, GPIO.IN)
        time.sleep(0.1)
    def state(self):
        s = GPIO.input(self._number)
        #print("read on " + str(self._number) + " " + str(s))
        #print("as bool " + str(self.map_from_pin_state(s)))
        return self.map_from_pin_state(s)
    def map_from_pin_state(self, pin_state):
        # Should never get not a GPIO state as input
        assert is_one_of(pin_state, GPIO.LOW, GPIO.HIGH)
        return pin_state == self._On
    def __str__(self):
        return "Input" + str(super().__str__())

class OutputPin(Pin):
    def __init__(self, number, *, active_state=GPIO.LOW, initial=False):
        super().__init__(number, active_state)
        GPIO.setup(self._number, GPIO.OUT, initial=self.map_to_pin_state(initial))
        time.sleep(0.1)
        # Double set initial in setup and here to set the self._state variable
        self.set(initial)
    def map_to_pin_state(self, state):
        return self._On if state else self._Off
    def state(self):
        return self._state
    def set(self, state):
        assert type(state) is bool
        GPIO.output(self._number, self.map_to_pin_state(state))
        self._state = state
    def __str__(self):
        return "Output" + str(super().__str__())

