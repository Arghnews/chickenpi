#!/usr/bin/env python3

import sys

from donetimer import DoneTimer
from pins import InputPin, OutputPin

# Class should prevent the state where both the output_open and output_close
# are on at once. This is effectively the same as both being off at once
# ie. the door doesn't move but should be avoided.
# Got to be slightly more careful with a timeout - we can't trust the
# microswitches that provide input as to where the door is - sometimes
# small debris means door final open position is just short of fully open
# and same for closed. Also remember that the manual switches in the coop
# itself exist and so don't want the poll function to permanently clear
# the state else these will be cleared too.

# Constructor using "dependency injection"
class Door:
    def __init__(self, name, *,
            input_bottom, input_top, output_open, output_close,
            movement_timeout_sec = 80):
        self._name = name
        self._input_bottom = input_bottom
        self._input_top = input_top
        self._output_open = output_open
        self._output_close = output_close
        assert type(input_bottom) is InputPin
        assert type(input_top) is InputPin
        assert type(output_open) is OutputPin
        assert type(output_close) is OutputPin
        self._timer = DoneTimer(movement_timeout_sec)

    def name(self):
        return self._name

    def __str__(self):
        s = ""
        s += "Door " + self._name + " is " + \
        {self.is_fully_open(): "fully open",
                self.is_in_middle(): "in the middle",
                self.is_closed(): "closed",}.get(True, "unknown") + \
                        " and " + \
        {self.is_opening(): "opening",
                self.is_closing(): "closing",
                self.is_stopped(): "stopped",}.get(
                        True, "stopped (both on)")
        done, seconds_left = self._timer.is_done_cached()
        if not done and not self._timer.is_stopped():
            s += " " + str(seconds_left) +  "s left till stopping"
        return s

    # State/input observers
    def is_fully_open(self):
        return bool(self._input_bottom and self._input_top)
    def is_in_middle(self):
        return bool(self._input_top and not self._input_bottom)
    def is_closed(self):
        return bool(not self._input_bottom and not self._input_top)

    # Output/action observers
    def is_opening(self):
        return bool(self._output_open)
    def is_closing(self):
        return bool(self._output_close)
    def is_stopped(self):
        return bool(not self.is_opening() and not self.is_closing())

    # Actions
    def stop(self):
        self._output_open.set(False)
        self._output_close.set(False)
        self._timer.stop()
    def open(self):
        self.stop()
        self._output_open.set(True)
        self._timer.reset()
    def close(self):
        self.stop()
        self._output_close.set(True)
        self._timer.reset()

    def poll(self):
        done, _ = self._timer.is_done()
        # Microswitches are complete bollocks lately - don't rely on knowing
        # where the doors are through them. Just close/open for the maximum
        # amount of time, every time.
        if done:
            self.stop()
        # if self.is_closed() and self.is_closing() \
        #         or self.is_fully_open() and self.is_opening() \
        #         or done and not self._timer.is_stopped():
        #     self.stop()

