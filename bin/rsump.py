#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import time
import os
from raspisump import reading, log, config_values

user = os.getlogin()
configs = config_values.configuration()
reading_interval = configs["reading_interval"]


def handle_gpio_error():
    error_message = "ERROR -- Cannot access gpio pins. Make sure the user is part of the gpio group."
    print(error_message)
    log.log_event("error_log", error_message)


def main():
    if reading_interval == 0:
        try:
            reading.water_depth()
        except RuntimeError:
            handle_gpio_error()
    else:
        while True:
            try:
                reading.water_depth()
                time.sleep(reading_interval)
            except RuntimeError:
                handle_gpio_error()
                exit(0)


if __name__ == "__main__":
    main()
