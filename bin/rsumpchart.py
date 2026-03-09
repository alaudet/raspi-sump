#!/usr/bin/env python

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import time
from raspisump import todaychart


def main():
    """Initiate todaychart.py module to graph sump pit activity."""
    csv_file = f"/var/lib/raspi-sump/csv/waterlevel-{time.strftime('%Y%m%d')}.csv"
    filename = "/var/lib/raspi-sump/charts/today.png"
    todaychart.graph(csv_file, filename)


if __name__ == "__main__":
    print("Creating one time chart reading in the charts directory - today.png")
    main()
