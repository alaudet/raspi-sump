"""Web statistics queries — aggregation on top of the readings database.

Does not modify log.py; CLI tools are unaffected.
"""

import sqlite3
import time

from raspisump.log import DB_PATH


def day_stats(date=None):
    """Return aggregated stats for a given date (YYYY-MM-DD), or today if None.

    Returns a dict with keys: min, max, count, last, last_ts, unit.
    Returns None if no readings exist for that date.
    """
    target = date if date is not None else time.strftime("%Y-%m-%d")
    pattern = f"{target}%"

    conn = sqlite3.connect(DB_PATH)
    try:
        row = conn.execute(
            """
            SELECT
                MIN(water_depth),
                MAX(water_depth),
                COUNT(*),
                (SELECT water_depth FROM readings WHERE ts LIKE ? ORDER BY ts DESC LIMIT 1),
                (SELECT ts          FROM readings WHERE ts LIKE ? ORDER BY ts DESC LIMIT 1),
                (SELECT unit        FROM readings WHERE ts LIKE ? LIMIT 1)
            FROM readings
            WHERE ts LIKE ?
            """,
            (pattern, pattern, pattern, pattern),
        ).fetchone()
    finally:
        conn.close()

    if row is None or row[2] == 0:
        return None

    return {
        "min":     row[0],
        "max":     row[1],
        "count":   row[2],
        "last":    row[3],
        "last_ts": row[4],
        "unit":    row[5],
    }
