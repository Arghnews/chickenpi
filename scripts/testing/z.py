#!/usr/bin/env python3

import sys

# FIXME: better name
def gpio_enabled_in_boot_config():
    with open("/boot/config.txt", "r") as f:
        return any(line.startswith("dtoverlay=w1-gpio")
                for line in f.read().splitlines())

def main(argv):
    print(gpio_enabled_in_boot_config())
    print("Hello world!")

if __name__ == "__main__":
    sys.exit(main(sys.argv))
