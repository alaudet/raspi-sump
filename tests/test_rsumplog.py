import os
import sqlite3
import tempfile
from unittest import TestCase
from unittest.mock import patch

from raspisump import log


def _make_db(rows):
    """Create a temp SQLite db pre-populated with (ts, water_depth, unit) rows.

    Returns the db file path.  Caller is responsible for unlinking it.
    """
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    conn = sqlite3.connect(f.name)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          TEXT    NOT NULL,
            water_depth REAL    NOT NULL,
            unit        TEXT    NOT NULL
        )
        """
    )
    conn.executemany(
        "INSERT INTO readings (ts, water_depth, unit) VALUES (?, ?, ?)", rows
    )
    conn.commit()
    conn.close()
    return f.name


class TestQueryReadings(TestCase):
    def setUp(self):
        self.rows = [
            ("2026-03-10 08:00:00", 10.5, "cm"),
            ("2026-03-10 09:00:00", 11.0, "cm"),
            ("2026-03-11 08:00:00", 9.5, "cm"),
            ("2026-03-11 09:00:00", 12.0, "cm"),
            ("2026-03-11 10:00:00", 8.0, "cm"),
        ]
        self.db_path = _make_db(self.rows)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_today_returns_only_todays_rows(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings(date="2026-03-11")
        self.assertEqual(len(rows), 3)
        for ts, _, _ in rows:
            self.assertTrue(ts.startswith("2026-03-11"))

    def test_specific_date(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings(date="2026-03-10")
        self.assertEqual(len(rows), 2)

    def test_last_n_returns_most_recent(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings(last=2)
        self.assertEqual(len(rows), 2)
        # Should be the two most recent rows, in chronological order
        self.assertEqual(rows[0][0], "2026-03-11 09:00:00")
        self.assertEqual(rows[1][0], "2026-03-11 10:00:00")

    def test_last_n_chronological_order(self):
        """Rows returned by --last should be oldest-first, not newest-first."""
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings(last=5)
        timestamps = [r[0] for r in rows]
        self.assertEqual(timestamps, sorted(timestamps))

    def test_empty_date_returns_empty_list(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings(date="2099-01-01")
        self.assertEqual(rows, [])

    def test_row_shape(self):
        """Each row should be (ts: str, water_depth: float, unit: str)."""
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings(date="2026-03-10")
        ts, depth, unit = rows[0]
        self.assertIsInstance(ts, str)
        self.assertIsInstance(depth, float)
        self.assertIsInstance(unit, str)
