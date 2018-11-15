#!/usr/bin/env python3

import time

# Class that may be used to check if an amount of time has elapsed
# Ie. what should is_done do when called on a stopped DoneTimer?
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

class DoneTimer:
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
