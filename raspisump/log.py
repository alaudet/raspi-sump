"""Log waterlevel readings, restarts and alerts."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import time
import os

user = os.getlogin()


def log_event(logfile, notification):
    """Write event notification to a logfile"""
    _logfile = f"/home/{user}/raspi-sump/logs/{logfile}"
    with open(_logfile, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S,')}")
        f.write(f"{notification}\n")


def log_reading(logfile, water_depth):
    """Log time and water depth reading."""
    filename = f"/home/{user}/raspi-sump/csv/{logfile}-{time.strftime('%Y%m%d')}.csv"
    with open(filename, "a") as f:
        f.write(f"{time.strftime('%H:%M:%S,')}")
        f.write(f"{water_depth}\n")
