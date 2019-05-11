#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)

# Assumes active low
ON = GPIO.LOW
OFF = GPIO.HIGH

def move_door(door, pin1_state, pin2_state):
    GPIO.output(door[0], pin1_state)
    GPIO.output(door[1], pin2_state)

def open_door(door):
    return move_door(door, ON, OFF)

def close_door(door):
    return move_door(door, OFF, ON)

def stop_door(door):
    return move_door(door, OFF, OFF)

def setup_output_door(*, open_pin, close_pin):
    GPIO.setup(open_pin, GPIO.OUT, initial=OFF)
    GPIO.setup(close_pin, GPIO.OUT, initial=OFF)
    return (open_pin, close_pin)

def main():
    wall = setup_output_door(open_pin=7, close_pin=8)
    near = setup_output_door(open_pin=12, close_pin=13)
    # turn on camera
    camera_pin = 15
    GPIO.setup(camera_pin, GPIO.OUT, initial=GPIO.LOW)
    GPIO.output(camera_pin, GPIO.LOW)
    input("Wait for camera to load - press Enter when done")

    try:
        print("Opening doors")
        open_door(near)
        open_door(wall)
        input("Opening doors - press Enter when done")
        close_door(near)
        close_door(wall)
        input("Closing doors - press Enter when done")
        stop_door(wall)
        close_door(near)
        input("Closing near door more - Enter to stop")
        stop_door(near)
        input("Press Enter to cleanup and exit")
    finally:
        print("Cleaning up")
        GPIO.cleanup()

if __name__ == '__main__':
    main()
