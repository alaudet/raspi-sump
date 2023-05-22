#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import time
import os
from raspisump import webchart

user = os.getlogin()

def main():
    '''Pass variables to webchart.py'''
    year = time.strftime('%Y')
    month = time.strftime('%m')
    today = time.strftime('%Y%m%d')
    homedir = '/home/' + user + "/raspi-sump/"
    webchart.create_folders(year, month, homedir)
    webchart.create_chart(homedir)
    webchart.copy_chart(year, month, today, homedir)

if __name__ == '__main__':
    main()
