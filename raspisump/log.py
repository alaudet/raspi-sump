"""Log waterlevel readings, restarts and alerts."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# Apache-2.0 License -- https://www.linuxnorth.org/raspi-sump/license.html

import os
import sqlite3
import time

DB_PATH = "/var/lib/raspi-sump/raspisump.db"

_UNIT_LABELS = {"metric": "cm", "imperial": "inches"}


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


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          TEXT    NOT NULL,
            water_depth REAL    NOT NULL,
            unit        TEXT    NOT NULL
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON readings (ts)")


def log_reading(water_depth: float, unit: str) -> None:
    """Log a sensor reading to the SQLite database."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    unit_label = _UNIT_LABELS.get(unit, unit)
    conn = sqlite3.connect(DB_PATH)
    try:
        _init_db(conn)
        conn.execute(
            "INSERT INTO readings (ts, water_depth, unit) VALUES (?, ?, ?)",
            (ts, water_depth, unit_label),
        )
        conn.commit()
    finally:
        conn.close()
