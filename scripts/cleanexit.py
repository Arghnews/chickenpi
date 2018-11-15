#!/usr/bin/env python3

import signal
import sys

# Import this file at entry point so that if receive a kill signal
# can run cleanup with functions registered with atexit
# If no signal then they will be called at normal exit

def exit_wrapper(signum, frame):
    print("Received signal:" + str(signum) + " - exiting normally")
    # Exit normally running cleanup functions
    sys.exit()

signal.signal(signal.SIGINT, exit_wrapper)
signal.signal(signal.SIGTERM, exit_wrapper)
