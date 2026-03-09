"""Create charts for viewing on Raspberry Pi Web Server."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.htmlimport os

import os
import shutil
import time
from raspisump import todaychart

CHARTS_DIR = "/var/lib/raspi-sump/charts"
CSV_DIR = "/var/lib/raspi-sump/csv"


def create_folders(year, month):
    """Create year/month subdirectories under the charts folder if needed"""
    os.makedirs(f"{CHARTS_DIR}/{year}/{month}", exist_ok=True)


def create_chart():
    """Create a chart of sump pit activity and save to web folder"""
    csv_file = f"{CSV_DIR}/waterlevel-{time.strftime('%Y%m%d')}.csv"
    filename = f"{CHARTS_DIR}/today.png"
    todaychart.graph(csv_file, filename)


def copy_chart(year, month, today):
    """Copy today.png to year/month/day folder for web viewing"""
    shutil.copy(f"{CHARTS_DIR}/today.png", f"{CHARTS_DIR}/{year}/{month}/{today}.png")
