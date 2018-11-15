#!/usr/bin/env python3

from donetimer import DoneTimer
from pins import OutputPin

class Camera:
    def __init__(self, pin, timeout_sec = 900):
        assert type(pin) is OutputPin
        self._pin = pin
        self._default_timeout = timeout_sec
        self._timer = DoneTimer(timeout_sec)
    # Note passing a value for the parameter seconds left only applies until
    # this timer ends/the next time the camera is switched off or reset
    def on(self, timeout_sec = None):
        if timeout_sec is not None:
            self._timer = DoneTimer(timeout_sec)
        else:
            self._timer = DoneTimer(self._default_timeout)
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

