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

if reading_interval == 0:
    try:
        reading.water_depth()
    except RuntimeError:
        print(
            "ERROR -- Cannot Access gpio pins.  Make sure user is part of the gpio group."
        )
        log.log_event(
            "error_log",
            "GPIO ERROR -- Cannot Access gpio pins.  Make sure user is part of the gpio group.",
        )
else:
    while True:
        try:
            reading.water_depth()
            time.sleep(reading_interval)
        except RuntimeError:
            print(
                "ERROR -- Cannot Access gpio pins.  Make sure user is part of the gpio group."
            )
            log.log_event(
                "error_log",
                "GPIO ERROR -- Cannot Access gpio pins.  Make sure user is part of the gpio group.",
            )
            exit(0)
