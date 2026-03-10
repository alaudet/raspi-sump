"""Create charts for viewing on Raspberry Pi Web Server."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import os
import shutil
import time
from raspisump import todaychart

CHARTS_DIR = "/var/lib/raspi-sump/charts"
CSV_DIR = "/var/lib/raspi-sump/csv"


def create_folders(year, month):
    """Create year/month subdirectories under the charts folder if needed"""
    old_umask = os.umask(0o002)
    try:
        os.makedirs(f"{CHARTS_DIR}/{year}/{month}", mode=0o770, exist_ok=True)
    finally:
        os.umask(old_umask)


def create_chart():
    """Create a chart of sump pit activity and save to web folder"""
    csv_file = f"{CSV_DIR}/waterlevel-{time.strftime('%Y%m%d')}.csv"
    filename = f"{CHARTS_DIR}/today.png"
    old_umask = os.umask(0o002)
    try:
        todaychart.graph(csv_file, filename)
    finally:
        os.umask(old_umask)


def copy_chart(year, month, today):
    """Copy today.png to year/month/day folder for web viewing"""
    shutil.copy(f"{CHARTS_DIR}/today.png", f"{CHARTS_DIR}/{year}/{month}/{today}.png")
