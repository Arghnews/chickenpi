#!/usr/bin/env python3

try:
    import RPi.GPIO as GPIO
    print("Successfully imported RPi.GPIO")
except RuntimeError:
    print("Error importing RPi.GPIO!  This is probably because you need superuser privileges.  You can achieve this by using 'sudo' to run your script")
    exit(1)

def main():
    GPIO.setmode(GPIO.BOARD)
    pin = 7
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)
    while 1:
        pass
    GPIO.cleanup()
if __name__ == '__main__':
    main()
