#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import time
import os
from raspisump import todaychart

user = os.getlogin()

def main():
    """Initiate todaychart.py module to graph sump pit activity."""
    csv_file = "/home/" + user + "/raspi-sump/csv/waterlevel-{}.csv".format(
        time.strftime("%Y%m%d")
    )
    filename = "/home/" + user + "/raspi-sump/charts/today.png"
    todaychart.graph(csv_file, filename)


if __name__ == "__main__":
    main()
