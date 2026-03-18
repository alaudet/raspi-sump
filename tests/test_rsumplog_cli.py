"""Tests for rsumplog CLI --time option."""

import os
import sqlite3
import tempfile
from io import StringIO
from unittest import TestCase
from unittest.mock import patch


def _make_db(rows):
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


def _run_rsumplog(argv, db_path):
    """Run rsumplog() with patched sys.argv and DB_PATH; return captured stdout."""
    from raspisump.cli import rsumplog
    buf = StringIO()
    with patch("sys.argv", ["rsumplog"] + argv), \
         patch("raspisump.log.DB_PATH", db_path), \
         patch("sys.stdout", buf):
        rsumplog()
    return buf.getvalue()


class TestRsumplogTimeOption(TestCase):

    def setUp(self):
        self.rows = [
            ("2026-03-10 08:00:00", 10.5, "cm"),
            ("2026-03-10 09:30:00", 11.0, "cm"),
            ("2026-03-10 13:00:00", 9.0,  "cm"),
            ("2026-03-10 15:45:00", 8.5,  "cm"),
            ("2026-03-10 22:00:00", 12.0, "cm"),
        ]
        self.db_path = _make_db(self.rows)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_time_range_filters_rows(self):
        out = _run_rsumplog(["--date", "2026-03-10", "--time", "9:00am", "4:00pm"], self.db_path)
        self.assertIn("09:30:00", out)
        self.assertIn("13:00:00", out)
        self.assertIn("15:45:00", out)
        self.assertNotIn("08:00:00", out)
        self.assertNotIn("22:00:00", out)

    def test_time_range_excludes_outside_rows(self):
        out = _run_rsumplog(["--date", "2026-03-10", "--time", "9:00am", "10:00am"], self.db_path)
        self.assertIn("09:30:00", out)
        self.assertNotIn("13:00:00", out)

    def test_time_24hr_format(self):
        out = _run_rsumplog(["--date", "2026-03-10", "--time", "13:00", "16:00"], self.db_path)
        self.assertIn("13:00:00", out)
        self.assertIn("15:45:00", out)
        self.assertNotIn("08:00:00", out)

    def test_time_midnight_12am(self):
        """12:00am should parse to 00:00 (midnight)."""
        rows = [("2026-03-10 00:15:00", 10.0, "cm")]
        db = _make_db(rows)
        try:
            out = _run_rsumplog(["--date", "2026-03-10", "--time", "12:00am", "1:00am"], db)
            self.assertIn("00:15:00", out)
        finally:
            os.unlink(db)

    def test_time_noon_12pm(self):
        """12:00pm should parse to 12:00 (noon)."""
        rows = [("2026-03-10 12:10:00", 10.0, "cm")]
        db = _make_db(rows)
        try:
            out = _run_rsumplog(["--date", "2026-03-10", "--time", "12:00pm", "1:00pm"], db)
            self.assertIn("12:10:00", out)
        finally:
            os.unlink(db)

    def test_time_defaults_to_today_without_date(self):
        """--time without --date should not raise a SystemExit — defaults to today."""
        try:
            _run_rsumplog(["--time", "9:00am", "11:00am"], self.db_path)
        except SystemExit:
            self.fail("--time without --date raised SystemExit unexpectedly")

    def test_time_no_readings_prints_not_found(self):
        out = _run_rsumplog(["--date", "2026-03-10", "--time", "3:00am", "4:00am"], self.db_path)
        self.assertIn("No readings found", out)

    def test_output_includes_date_time_label(self):
        out = _run_rsumplog(["--date", "2026-03-10", "--time", "9:00am", "4:00pm"], self.db_path)
        self.assertIn("2026-03-10", out)
        self.assertIn("09:00", out)
        self.assertIn("16:00", out)


class TestRsumplogTimeArgumentConflicts(TestCase):

    def setUp(self):
        self.db_path = _make_db([])

    def tearDown(self):
        os.unlink(self.db_path)

    def _expect_error(self, argv):
        from raspisump.cli import rsumplog
        with patch("sys.argv", ["rsumplog"] + argv), \
             patch("raspisump.log.DB_PATH", self.db_path):
            with self.assertRaises(SystemExit) as ctx:
                rsumplog()
        self.assertEqual(ctx.exception.code, 2)

    def test_time_with_last_raises_error(self):
        self._expect_error(["--last", "10", "--time", "9:00am", "5:00pm"])

    def test_time_with_cycles_raises_error(self):
        self._expect_error(["--cycles", "--time", "9:00am", "5:00pm"])

    def test_invalid_time_format_raises_error(self):
        self._expect_error(["--date", "2026-03-10", "--time", "notaTime", "5:00pm"])
