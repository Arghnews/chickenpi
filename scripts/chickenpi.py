#!/usr/bin/env python3

import signal # catch kill 15 SIGTERM
import time # for sleeping, camera timer
import enum # door positions
#from listen import net # my net
import listen # my simple networking script
from functools import partial

try:
    import RPi.GPIO as GPIO
    print("Successfully imported RPi.GPIO")
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
    exit(1)


class Position(enum.Enum):
    Open = 0
    Closed = 1
    Middle = 2
    Unknown = 3
    # Returns the var name
    def __str__(self):
        return self.name.lower()

class Door:
    # Startup sleep time - if init all at the same time
    # can cause strange behaviour
    Sleep_Time = 20.0 / 1000.0 # x / 1000.0, x in ms
    def __init__(
            self,
            in_low,
            in_up,
            d_open,
            d_close,
            active_low=True,
            movement_time_s=100):

        pins = [in_low,in_up,d_open,d_close]
        if len(pins) > len(set(pins)):
            raise RuntimeError("Input/output pins are not all different")

        self.in_low = in_low
        self.in_up = in_up

        self.d_open = d_open
        self.d_close = d_close

        # just for outputs
        self.active_low = active_low
        self.On = GPIO.LOW if self.active_low else GPIO.HIGH
        self.Off = GPIO.HIGH if self.active_low else GPIO.LOW

        # door takes 60 seconds to open/shut
        self.movement_time_s = movement_time_s

        self.last_action = 0

        # input channels
        GPIO.setup(self.in_low, GPIO.IN)
        time.sleep(Door.Sleep_Time)
        GPIO.setup(self.in_up, GPIO.IN)
        time.sleep(Door.Sleep_Time)

        # output channels
        GPIO.setup(self.d_open, GPIO.OUT, initial=self.Off)
        time.sleep(Door.Sleep_Time)
        GPIO.setup(self.d_close, GPIO.OUT, initial=self.Off)
        time.sleep(Door.Sleep_Time)
        print("Done constructing")

    def check_position(self):

        # door at bottom, both low
        # door in middle, bottom high and upper low
        # door at top, both high
        lower = GPIO.input(self.in_low)
        upper = GPIO.input(self.in_up)
        pos = Position.Unknown

        if not lower and not upper:
            pos = Position.Closed
        elif lower and upper:
            pos = Position.Open
        elif lower and not upper:
            pos = Position.Middle
        return pos

    def is_opening(self):
        return GPIO.input(self.d_open) == self.On

    def is_closing(self):
        return GPIO.input(self.d_close) == self.On

    # door should be polled frequently to send stop signals
    # after a time. Eg. "Open" action happens, 60 seconds later
    # want to initiate a stop signal so not opening forever
    def poll_me(self):
        if self.last_action == 0:
            pass
        else:
            time_now = int(time.time()) # epoch time in s
            if self.last_action + self.movement_time_s < time_now:
                print("Resetting")
                self.action_stop(False)
                self.last_action = 0

    def log_action(self):
        self.last_action = int(time.time())

    def action_open(self):
        # stop closing
        GPIO.output(self.d_close, self.Off)

        GPIO.output(self.d_open, self.On)
        self.log_action()

    def action_close(self):
        # stop opening
        GPIO.output(self.d_open, self.Off)

        GPIO.output(self.d_close, self.On)
        self.log_action()

    # stop moving the door
    def action_stop(self,log=True):
        GPIO.output([self.d_open,self.d_close], self.Off)
        if log:
            self.log_action()

    # return list of actions
    def actions(self):
        return ["open","close","stop","check_position"]

class Camera:

    # for now (quick job) always active low = on
    def __init__(self,pin,seconds_on=900):
        self.pin = pin
        self.seconds_on = seconds_on
        self.timer = 0
        # start off initially
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)

    # should be called to switch on camera
    def on(self):
        self.timer = int(time.time()) + self.seconds_on
        GPIO.output(self.pin, GPIO.LOW)

    # should be called every poll/regularly
    def poll(self):
        if self.timer == 0:
            return

        time_now = int(time.time()) # epoch
        if time_now > self.timer:
            self.timer = 0
            # switch off camera
            GPIO.output(self.pin, GPIO.HIGH)



# json_in -> json_out
def f(obj_in):
    keep_running = True

    # do stuff to json object
    print("In func f")
    for key, val in obj_in.items():
        print(key, val)

    obj_out = obj_in

    return obj_out, keep_running

def poll_func(doors, camera):
    #print("poll")
    camera.poll()
    for door_name, door in doors.items():
        door.poll_me()

def process_input(obj_in, doors, camera):
    obj_out = dict()
    continue_status = True

    # when we have a request, want to activate the camera
    camera.on()

    # processing of request for door stuff
    if "request" in obj_in:
        request = obj_in["request"]

        if request == "list_doors":
            response = []
            for door_name, door_obj in doors.items():
                door = dict()
                print("Adding door:",door_name)
                door["door_name"] = door_name
                door["door_actions"] = door_obj.actions()
                response.append(door.copy())
            obj_out["response"] = response
        elif request == "door_action":
            door = obj_in["door_name"]
            door_action = obj_in["door_action"]
            status = ""

            if not door in doors:
                status = "That door does not exist"
            else:
                def f():
                    nonlocal status
                    status = "performing action: " + door_action.rsplit(None, 1)[-1]
                if "open" in door_action:
                    doors[door].action_open()
                    f()
                elif "close" in door_action:
                    doors[door].action_close()
                    f()
                elif "stop" in door_action:
                    doors[door].action_stop()
                    f()
                elif "check_position" in door_action:
                    doors[door].check_position()
                    status = str(doors[door].check_position())
                
            obj_out["status"] = status

    return obj_out, continue_status

def close(signum, frame):
    print("CLOSING!")

def main():

    # not using BCM modes
    GPIO.setmode(GPIO.BOARD)
    # still up in the air?
    #GPIO.setmode(GPIO.BCM)

    #print(GPIO.RPI_INFO)
    #print(GPIO.RPI_INFO['P1_REVISION'])
    #print("GPIO version:",GPIO.VERSION)

    try:
        print("Main")

        # catch kill 15 signal
        signal.signal(signal.SIGTERM, close)

        doors = dict()
        doors["wall"] = Door(3,5,37,8)
        doors["near"] = Door(10,11,12,13)

        camera = Camera(15)
        poll = partial(poll_func, doors=doors, camera=camera)
        process = partial(process_input, doors=doors, camera=camera)
        # wait 0.1 seconds on select block
        # sleep 0.9 seconds each iter
        listen.net(poll,process,0.1,900.0/1000.0)

    except:
        raise
    finally:
        print("Cleaning up")
        GPIO.cleanup()
    print("Exiting")

if __name__ == '__main__':
    main()
