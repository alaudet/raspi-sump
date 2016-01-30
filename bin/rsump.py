#!/usr/bin/python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import time
try:
    import ConfigParser
except ImportError:
    import configparser

import raspisump.reading as reading

try:
    config = ConfigParser.RawConfigParser()
except NameError:
    config = configparser.RawConfigParser()

config.read('/home/pi/raspi-sump/raspisump.conf')
reading_interval = config.getint('pit', 'reading_interval')

if reading_interval == 0:
    reading.water_reading()
else:
    while True:
        reading.water_reading()
        time.sleep(reading_interval)
