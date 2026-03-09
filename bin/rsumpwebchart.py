#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import time
from raspisump import webchart


def main():
    """Pass variables to webchart.py"""
    year = time.strftime("%Y")
    month = time.strftime("%m")
    today = time.strftime("%Y%m%d")
    webchart.create_folders(year, month)
    webchart.create_chart()
    webchart.copy_chart(year, month, today)


if __name__ == "__main__":
    main()
