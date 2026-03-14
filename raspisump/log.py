"""Log waterlevel readings, restarts and alerts."""

# Raspi-sump, a sump pump monitoring system.
# Al Audet
# https://www.linuxnorth.org/raspi-sump/
#
# All configuration changes should be done in raspisump.conf
# Apache-2.0 License -- https://www.linuxnorth.org/raspi-sump/license.html

import os
import re
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


def query_readings(date: str = None, last: int = None) -> list:
    """Return readings from the database.

    date : "YYYY-MM-DD" — all readings for that calendar day (default: today)
    last : int          — the N most recent readings (overrides date)

    Returns a list of (ts, water_depth, unit) tuples in chronological order.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        if last is not None:
            rows = conn.execute(
                "SELECT ts, water_depth, unit FROM readings"
                " ORDER BY id DESC LIMIT ?",
                (last,),
            ).fetchall()
            return list(reversed(rows))
        target = date if date is not None else time.strftime("%Y-%m-%d")
        return conn.execute(
            "SELECT ts, water_depth, unit FROM readings"
            " WHERE ts LIKE ? ORDER BY ts",
            (f"{target}%",),
        ).fetchall()
    finally:
        conn.close()


def import_csv_files(paths: list, unit_label: str) -> tuple:
    """Import readings from a list of CSV files into the database.

    Each CSV line must be: YYYY-MM-DD HH:MM:SS,depth
    (the format written by raspi-sump 1.x)

    unit_label : display label to store — "cm" or "inches"

    Returns (inserted, skipped, errors) where:
      inserted : number of rows added
      skipped  : number of rows whose timestamp already existed in the db
      errors   : list of human-readable parse error strings
    """
    old_umask = os.umask(0o002)
    try:
        conn = sqlite3.connect(DB_PATH)
    finally:
        os.umask(old_umask)

    try:
        _init_db(conn)

        # Detect unit mismatch: if the database already contains readings,
        # check whether they use a different unit than what is being imported.
        # Mixing metric and imperial in one database produces nonsensical charts.
        existing_unit_row = conn.execute(
            "SELECT unit FROM readings LIMIT 1"
        ).fetchone()
        if existing_unit_row and existing_unit_row[0] != unit_label:
            db_unit = existing_unit_row[0]
            correct_flag = "metric" if db_unit == "cm" else "imperial"
            raise ValueError(
                f"Unit mismatch: database contains '{db_unit}' readings but "
                f"you are importing '{unit_label}'. "
                f"Use --unit {correct_flag} to match the existing data."
            )

        # Load existing timestamps once to detect duplicates without
        # issuing a SELECT per row.
        existing_ts = {
            r[0]
            for r in conn.execute("SELECT ts FROM readings").fetchall()
        }

        to_insert = []
        skipped = 0
        errors = []

        for path in paths:
            # Date comes from the filename: waterlevel-YYYYMMDD.csv
            # Each line only contains HH:MM:SS,depth — no date.
            m = re.search(r"waterlevel-(\d{4})(\d{2})(\d{2})\.csv$", path)
            if not m:
                errors.append(
                    f"{path}: filename does not match waterlevel-YYYYMMDD.csv"
                )
                continue
            date_prefix = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

            with open(path, "r") as f:
                for lineno, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    time_str, sep, depth_str = line.partition(",")
                    if not sep:
                        errors.append(f"{path}:{lineno}: no comma found")
                        continue
                    ts = f"{date_prefix} {time_str.strip()}"
                    depth_str = depth_str.strip()
                    try:
                        depth = float(depth_str)
                    except ValueError:
                        errors.append(
                            f"{path}:{lineno}: cannot parse depth {depth_str!r}"
                        )
                        continue
                    if ts in existing_ts:
                        skipped += 1
                        continue
                    to_insert.append((ts, depth, unit_label))
                    existing_ts.add(ts)  # prevent duplicates within the batch

        conn.executemany(
            "INSERT INTO readings (ts, water_depth, unit) VALUES (?, ?, ?)",
            to_insert,
        )
        conn.commit()
        return len(to_insert), skipped, errors

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def query_readings_range(
    start_date: str,
    end_date: str = None,
    start_time: str = None,
    end_time: str = None,
) -> list:
    """Return readings across a date range with optional time-of-day filtering.

    start_date, end_date : "YYYY-MM-DD"  (end_date defaults to start_date)
    start_time, end_time : "HH:MM"       (optional; only meaningful for single-day exports)

    Returns a list of (ts, water_depth, unit) tuples in chronological order.
    """
    if end_date is None:
        end_date = start_date
    start_ts = f"{start_date} {start_time}:00" if start_time else f"{start_date} 00:00:00"
    end_ts = f"{end_date} {end_time}:59" if end_time else f"{end_date} 23:59:59"
    conn = sqlite3.connect(DB_PATH)
    try:
        return conn.execute(
            "SELECT ts, water_depth, unit FROM readings"
            " WHERE ts >= ? AND ts <= ? ORDER BY ts",
            (start_ts, end_ts),
        ).fetchall()
    finally:
        conn.close()


def log_reading(water_depth: float, unit: str) -> None:
    """Log a sensor reading to the SQLite database."""
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    unit_label = _UNIT_LABELS.get(unit, unit)
    old_umask = os.umask(0o002)
    try:
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
    finally:
        os.umask(old_umask)
