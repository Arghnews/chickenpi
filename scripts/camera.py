#!/usr/bin/env python3

import pins
import time

#i = pins.InputPin(37)
#print(i)

#camera = pins.OutputPin(15)
#camera.set(True)

#input("waiting for input to switch off")

in_low = pins.InputPin(3)
in_high = pins.InputPin(5)

print(in_low)
print(in_high)

# Class that may be used to check if an amount of time has elapsed
class ElapsedTimer:
    def __init__(self, seconds):
        self._seconds = seconds
        self._running = False
    def reset(self):
        self._time = time.monotonic()
        self._running = True
    def elapsed(self):
        assert(self.running(), "May only check if a running timer has "
                "elapsed")
        elapsed = time.monotonic() - self._time >= self._seconds
        if elapsed:
            self.stop()
        return elapsed
    def running(self):
        return _running
    def stop(self):
        self._running = False

# Class should prevent the state where both the output_open and output_close
# are on at once. This is effectively the same as both being off at once
# ie. the door doesn't move but should be avoided.
# Got to be slightly more careful with a timeout - we can't trust the
# microswitches that provide input as to where the door is - sometimes
# small debris means door final open position is just short of fully open
# and same for closed. Also remember that the manual switches in the coop
# itself exist and so don't want the poll function to permanently clear
# the state else these will be cleared too.
class Door:
    def __init__(self, *, input_bottom, input_top, output_open, output_close):
        self._input_bottom = input_bottom
        self._input_top = input_top
        self._output_open = output_open
        self._output_close = output_close
        self._timer = ElapsedTimer(80)

    # State/input observers
    def is_fully_open(self):
        return self._input_bottom and self._input_top
    def is_in_middle(self):
        return not self._input_bottom and self._input_top
    def is_closed(self):
        return not self._input_bottom and not self._input_top

    # Output/action observers
    def is_opening(self):
        return self._output_open
    def is_closing(self):
        return self._output_close

    # Actions
    def stop(self):
        self._output_open.set(False)
        self._output_close.set(False)
    def open(self):
        self.stop()
        self._output_open.set(True)
        self._timer.reset()
    def close(self):
        self.stop()
        self._output_close.set(True)
        self._timer.reset()

    def poll(self):
        if self.is_closed() and self.is_closing() \
                or self.is_open() and self.is_opening():
            self.stop()
            if _timer.running():
                timer.stop()
        
        if timer.running() and self._timer.elapsed():
            self.stop()
            timer.stop()



