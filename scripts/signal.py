#!/usr/bin/env python3

import signal
import time

truism = False

def funky(signum, frame):
    truism = True
    print("Received",signum,frame)

signal.signal(signal.SIGTERM, funky)

while 1:
    if truism:
        print("IT'S TRUE")
