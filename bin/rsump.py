#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import time

try:
    import ConfigParser as configparser # Python2
except ImportError:
    import configparser # Python3
from raspisump import reading

config = configparser.RawConfigParser()

config.read('/home/pi/raspi-sump/raspisump.conf')
reading_interval = config.getint('pit', 'reading_interval')

if reading_interval == 0:
    reading.water_depth()
else:
    while True:
        reading.water_depth()
        time.sleep(reading_interval)
