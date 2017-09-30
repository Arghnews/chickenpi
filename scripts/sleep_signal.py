#!/usr/bin/env python3

import signal
import time
import os

truism = False

def funky(signum, frame):
    truism = True
    print("Received!!!!",signum,frame)

signal.signal(signal.SIGTERM, funky)

print(os.getpid())

print("I am going to sleep....")
time.sleep(1000)
print("I am rudely awakened")
