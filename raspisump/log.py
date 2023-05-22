'''Log waterlevel readings, restarts and alerts.'''

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
    _logfile = "/home/" + user + "/raspi-sump/logs/{}".format(logfile)
    with open(_logfile, 'a') as f:
        f.write(time.strftime("%Y-%m-%d %H:%M:%S,")),
        f.write(notification + "\n"),


def log_reading(water_depth):
    '''Log time and water depth reading.'''
    filename = "/home/" + user + "/raspi-sump/csv/waterlevel-{}.csv".format(
        time.strftime("%Y%m%d"))
    with open(filename, 'a') as f:
        f.write(time.strftime("%H:%M:%S,")),
        f.write(str(water_depth) + "\n"),

