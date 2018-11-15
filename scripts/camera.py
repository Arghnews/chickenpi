#!/usr/bin/env python3

from pins import InputPin, OutputPin
import math
import time

# Class that may be used to check if an amount of time has elapsed
# Ie. what should is_done do when called on a stopped ElapsedTimer?
# Throw, return false? Should a timer that is done also be stopped?
# The next interesting question - want to prevent scenario where you
# ask is it done, it says no, you then print it and it's done as
# effectively there was a race in that time.
#
# # Example output with comments
# "Camera {(Outputpin: 15, state: False), off}"
# # camera turned on
# # "Camera {(Outputpin: 15, state: True), on for 1s more}"
# # camera then printed again 1 sec later
# # "Camera {(Outputpin: 15, state: True), off}"
#
# # conditional code for print has correctly seen that time is up
# and put it "off" rather than time left, but the state of the
# pin is still on as the "poll" function on the object owning the
# pin that would actually switch it off hasn't been called yet.
# Could argue this is a bug in the calling code, not this classes
# problem. Or that any functions called on the timer that observe it
# should reflect the latest state (but that leads to issues like this).
# I am taking the way that you can either call is_done or is_done_cached - 
# I dislike the name. If not cached, then it will use the state from last time,
# so that for simple if not done: then print stuff dependent on this we
# get consistency. Trying it for now
# Another option is [a]sync callbacks or threading but this seems to add more
# complexity for no benefit
class ElapsedTimer:
    def __init__(self, seconds):
        self._seconds = seconds
        self._stopped = True
    # Only entry point to (re)start timer
    def reset(self):
        self._time = time.monotonic()
        self._stopped = False
        self._time_now(True)

    def is_done(self):
        return self._is_done(True)
    def is_done_cached(self):
        return self._is_done(False)
    def stop(self):
        self._stopped = True
    def is_stopped(self):
        return self._stopped

    def _time_now(self, realtime):
        if realtime:
            self._last_time = time.monotonic()
        return self._last_time
    def _is_done(self, cached):
        if self.is_stopped():
            return False, None
        elapsed = int(self._time_now(cached) - self._time)
        done = elapsed >= self._seconds
        seconds_left = int(self._seconds - elapsed)
        return done, None if done else seconds_left 

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
        self._timer = ElapsedTimer(movement_timeout_sec)

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
        if self.is_closed() and self.is_closing() \
                or self.is_fully_open() and self.is_opening() \
                or done and not self._timer.is_stopped():
            self.stop()

class Camera:
    def __init__(self, pin, timeout_sec = 900):
        assert type(pin) is OutputPin
        self._pin = pin
        self._default_timeout = timeout_sec
        self._timer = ElapsedTimer(timeout_sec)
    # Note passing a value for the parameter seconds left only applies until
    # this timer ends/the next time the camera is switched off or reset
    def on(self, timeout_sec = None):
        if timeout_sec is not None:
            self._timer = ElapsedTimer(timeout_sec)
        else:
            self._timer = ElapsedTimer(self._default_timeout)
        self._timer.reset()
        self._pin.set(True)
    def off(self):
        self._timer.stop()
        self._pin.set(False)
    def poll(self):
        if self._timer.is_done()[0]:
            self.off()
    def __str__(self):
        s = "Camera {(" + str(self._pin) + "), "
        done, seconds_left = self._timer.is_done_cached()
        #if not done and not self._timer.is_stopped():
        if self._pin:
            s += "on for " + str(seconds_left) + "s more}"
        else:
            s += "off}"
        return s

wall_door = Door("wall door",
        input_bottom = InputPin(3), input_top = InputPin(5),
        output_open = OutputPin(37), output_close = OutputPin(8))
near_door = Door("near door",
        input_bottom = InputPin(10), input_top = InputPin(11),
        output_open = OutputPin(12), output_close = OutputPin(13))
camera = Camera(OutputPin(15),1)
print(camera)
camera.on()
print(camera)
time.sleep(2)
print(camera)

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


