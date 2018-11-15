#!/usr/bin/env python3

import os
import sys
import signal

# Clean exit
# Call this so that if a signal is caught to exit the program will do so
# normally thereby calling any functions registered using atexit
def catch_signals_exit_cleanly():
    signal.signal(signal.SIGINT, _exit_wrapper)
    signal.signal(signal.SIGTERM, _exit_wrapper)

def _exit_wrapper(signum, frame):
    print("Received signal:" + str(signum) + " - exiting normally")
    # Exit normally (running any registered cleanup functions)
    sys.exit()

# Error print from https://stackoverflow.com/a/14981125
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

# Require su privileges else exit
def exit_if_not_root():
    if os.geteuid() != 0:
        eprint("Must be run as root - exiting")
        sys.exit(1)

def import_gpio():
    exit_if_not_root()
    # Probably bad practice but seems cool for this
    # Sets the key GPIO to RPi.GPIO in global namespace
    import RPi.GPIO
    globals()["GPIO"] = RPi.GPIO
    GPIO.setmode(GPIO.BOARD)

