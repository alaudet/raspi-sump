"""Create charts for viewing on Raspberry Pi Web Server."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.htmlimport os

import os
import subprocess
import time
from raspisump import todaychart


def create_folders(year, month, homedir):
    """Check if folders exist in charts folder and create them if they don't"""
    if not os.path.isdir(f"{homedir}charts/{year}/"):
        _year = f"mkdir {homedir}charts/{year}"
        create_year = _year.split(" ")
        subprocess.call(create_year)

    if not os.path.isdir(f"{homedir}charts/{year}/{month}/"):
        _month = f"mkdir {homedir}charts/{year}/{month}"
        create_month = _month.split(" ")
        subprocess.call(create_month)


def create_chart(homedir):
    """Create a chart of sump pit activity and save to web folder"""
    csv_file = f"{homedir}csv/waterlevel-{time.strftime('%Y%m%d')}.csv"
    filename = f"{homedir}charts/today.png"
    todaychart.graph(csv_file, filename)


def copy_chart(year, month, today, homedir):
    """Copy today.png to year/month/day folder for web viewing"""
    copy_cmd = (
        f"cp {homedir}charts/today.png {homedir}charts/{year}/{month}/{today}.png"
    )
    copy_file = copy_cmd.split(" ")
    subprocess.call(copy_file)
