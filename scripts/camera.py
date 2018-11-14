#!/usr/bin/env python3

from pins import InputPin, OutputPin
import math
import time

# Class that may be used to check if an amount of time has elapsed
# TODO: seconds_left seems unclean, dislike the assert that can blow up
class ElapsedTimer:
    def __init__(self, seconds):
        self._seconds = seconds
        self._running = False
    def reset(self):
        self._time = time.monotonic()
        self._running = True

    def elapsed(self):
        assert self.is_running(), ("May only check if a running timer has "
                "elapsed")
        elapsed = time.monotonic() - self._time >= self._seconds
        if elapsed:
            self.stop()
        return elapsed
    def is_running(self):
        return self._running
    def stop(self):
        self._running = False
    def seconds_left(self):
        assert self.is_running()
        return max(self._seconds - int(time.monotonic() - self._time), 0)

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
    def __init__(self, name, *,
            input_bottom, input_top, output_open, output_close):
        self._name = name
        self._input_bottom = input_bottom
        self._input_top = input_top
        self._output_open = output_open
        self._output_close = output_close
        assert type(input_bottom) is InputPin
        assert type(input_top) is InputPin
        assert type(output_open) is OutputPin
        assert type(output_close) is OutputPin
        self._timer = ElapsedTimer(80)

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
        if self._timer.is_running():
            s += " " + str(self._timer.seconds_left()) + "s left till stopping"
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
        if self.is_closed() and self.is_closing() \
                or self.is_fully_open() and self.is_opening():
            self.stop()
            if self._timer.is_running():
                self._timer.stop()

        if self._timer.is_running() and self._timer.elapsed():
            self.stop()
            self._timer.stop()

class Camera:
    def __init__(self, pin, seconds_on=900):
        assert type(pin) is OutputPin
        self._pin = pin
        self._timer = ElapsedTimer(seconds_on)
    def on(self):
        self._timer.reset()
        self._pin.set(True)
    def off(self):
        self._timer.stop()
        self._pin.set(False)
    def poll(self):
        if self._timer.is_running() and self._timer.elapsed():
            self._timer.stop()
            self.off()
    def __str__(self):
        s = "Camera {(" + str(self._pin) + "), "
        if self._pin:
            s += "on for " + str(self._timer.seconds_left()) + "s more}"
        else:
            s += "off}"
        return s



wall_door = Door("wall door",
        input_bottom = InputPin(3), input_top = InputPin(5),
        output_open = OutputPin(37), output_close = OutputPin(8))
near_door = Door("near door",
        input_bottom = InputPin(10), input_top = InputPin(11),
        output_open = OutputPin(12), output_close = OutputPin(13))
camera = Camera(OutputPin(15))

print(wall_door)
wall_door.open()
print(wall_door)
wall_door.poll()
print(wall_door)
time.sleep(1)
wall_door.poll()
print(wall_door)
time.sleep(3)
print(wall_door)
wall_door.poll()
print(wall_door)

exit(0)
print("start")
print(wall_door.is_opening())
wall_door.stop()
ff = wall_door.is_fully_open()
print(type(ff))
print("wall door middle: " + str(wall_door.is_in_middle()))
exit(0)
print("wall door fully open: " + str(wall_door.is_fully_open()))
print("wall door closed: " + str(wall_door.is_closed()))
#near_door.stop()
print("opening")
wall_door.open()
#near_door.open()
print("----------------")
print(wall_door)
print("----------------")
#print(near_door)
input("Press to see door state and end")
print(wall_door)
#print(near_door)


