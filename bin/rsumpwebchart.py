#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# http://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- http://www.linuxnorth.org/raspi-sump/license.html

import time
from raspisump import webchart


def main():
    '''Pass variables to webchart.py'''
    year = time.strftime('%Y')
    month = time.strftime('%m')
    today = time.strftime('%Y%m%d')
    homedir = '/home/pi/raspi-sump/'
    webchart.create_folders(year, month, homedir)
    webchart.create_chart(homedir)
    webchart.copy_chart(year, month, today, homedir)

if __name__ == '__main__':
    main()
