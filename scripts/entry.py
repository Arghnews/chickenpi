#!/usr/bin/env python3

import sys

from pins import InputPin, OutputPin
from door import Door
from camera import Camera
import cleanexit

def main(argv):
    print("Hello world!")
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

if __name__ == "__main__":
    sys.exit(main(sys.argv))
