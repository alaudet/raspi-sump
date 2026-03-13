"""Tests for web stats aggregation queries."""

import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch


class TestDayStats(unittest.TestCase):

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE readings (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                ts          TEXT NOT NULL,
                water_depth REAL NOT NULL,
                unit        TEXT NOT NULL
            )
        """)
        conn.executemany(
            "INSERT INTO readings (ts, water_depth, unit) VALUES (?, ?, ?)",
            [
                ("2026-03-13 08:00:00", 12.5, "cm"),
                ("2026-03-13 09:00:00", 15.0, "cm"),
                ("2026-03-13 10:00:00", 10.0, "cm"),
                ("2026-03-13 11:00:00", 13.5, "cm"),
            ],
        )
        conn.commit()
        conn.close()

    def tearDown(self):
        os.unlink(self.db_path)

    def _day_stats(self, date=None):
        from raspisump.web.stats import day_stats
        with patch("raspisump.web.stats.DB_PATH", self.db_path):
            return day_stats(date)

    def test_returns_correct_min(self):
        stats = self._day_stats("2026-03-13")
        self.assertEqual(stats["min"], 10.0)

    def test_returns_correct_max(self):
        stats = self._day_stats("2026-03-13")
        self.assertEqual(stats["max"], 15.0)

    def test_returns_correct_count(self):
        stats = self._day_stats("2026-03-13")
        self.assertEqual(stats["count"], 4)

    def test_returns_last_reading(self):
        stats = self._day_stats("2026-03-13")
        self.assertEqual(stats["last"], 13.5)
        self.assertEqual(stats["last_ts"], "2026-03-13 11:00:00")

    def test_returns_unit(self):
        stats = self._day_stats("2026-03-13")
        self.assertEqual(stats["unit"], "cm")

    def test_returns_none_for_empty_date(self):
        stats = self._day_stats("2026-01-01")
        self.assertIsNone(stats)


if __name__ == "__main__":
    unittest.main()
