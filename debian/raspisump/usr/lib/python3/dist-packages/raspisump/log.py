"""Log waterlevel readings, restarts and alerts."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# MIT License -- https://www.linuxnorth.org/raspi-sump/license.html

import os
import time


def _open_shared(path):
    """Open a file for appending with mode 0664 regardless of process umask.

    Files in raspisump dirs are shared between the raspisump service user and
    any human user in the raspisump group.  Without this, a file first created
    by a human user would get group 'al' and mode 0644, preventing the service
    from appending to it later.
    """
    old_umask = os.umask(0o002)
    try:
        return open(path, "a")
    finally:
        os.umask(old_umask)


def log_event(logfile, notification):
    """Write event notification to a logfile"""
    _logfile = f"/var/log/raspi-sump/{logfile}"
    with _open_shared(_logfile) as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S,')}")
        f.write(f"{notification}\n")


def log_reading(logfile, water_depth):
    """Log time and water depth reading."""
    filename = f"/var/lib/raspi-sump/csv/{logfile}-{time.strftime('%Y%m%d')}.csv"
    with _open_shared(filename) as f:
        f.write(f"{time.strftime('%H:%M:%S,')}")
        f.write(f"{water_depth}\n")
