import os
import sqlite3
import tempfile
from unittest import TestCase
from unittest.mock import patch

from raspisump import log


def _make_db():
    """Create an empty temp database and return its path."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    f.close()
    return f.name


def _make_csv(date, lines):
    """Write lines to a properly-named waterlevel-YYYYMMDD.csv temp file.

    date  : "YYYYMMDD" string used in the filename
    lines : list of "HH:MM:SS,depth" strings (the actual CSV format)
    """
    # suffix ignored — we rename to match the expected filename pattern
    d = tempfile.mkdtemp()
    path = os.path.join(d, f"waterlevel-{date}.csv")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def _row_count(db_path):
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM readings").fetchone()[0]
    conn.close()
    return count


def _all_rows(db_path):
    conn = sqlite3.connect(db_path)
    rows = conn.execute(
        "SELECT ts, water_depth, unit FROM readings ORDER BY ts"
    ).fetchall()
    conn.close()
    return rows


class TestImportCsvFiles(TestCase):
    def setUp(self):
        self.db_path = _make_db()
        self.csv_path = None

    def tearDown(self):
        os.unlink(self.db_path)
        if self.csv_path and os.path.exists(self.csv_path):
            os.unlink(self.csv_path)
            os.rmdir(os.path.dirname(self.csv_path))

    def _import(self, date, lines, unit_label="cm"):
        self.csv_path = _make_csv(date, lines)
        with patch("raspisump.log.DB_PATH", self.db_path):
            return log.import_csv_files([self.csv_path], unit_label)

    def test_basic_import(self):
        inserted, skipped, errors = self._import("20260101", [
            "08:00:00,10.5",
            "08:05:00,11.0",
            "08:10:00,9.5",
        ])
        self.assertEqual(inserted, 3)
        self.assertEqual(skipped, 0)
        self.assertEqual(errors, [])
        self.assertEqual(_row_count(self.db_path), 3)

    def test_timestamp_built_from_filename_and_time(self):
        """Full ts stored as YYYY-MM-DD HH:MM:SS using date from filename."""
        self._import("20260207", ["23:39:35,6.0"])
        rows = _all_rows(self.db_path)
        self.assertEqual(rows[0][0], "2026-02-07 23:39:35")

    def test_unit_label_stored(self):
        self._import("20260101", ["08:00:00,10.5"], unit_label="cm")
        rows = _all_rows(self.db_path)
        self.assertEqual(rows[0][2], "cm")

    def test_imperial_unit_label(self):
        self._import("20260101", ["08:00:00,10.5"], unit_label="inches")
        rows = _all_rows(self.db_path)
        self.assertEqual(rows[0][2], "inches")

    def test_duplicate_timestamps_skipped(self):
        lines = ["08:00:00,10.5", "08:05:00,11.0"]
        # First import
        self.csv_path = _make_csv("20260101", lines)
        with patch("raspisump.log.DB_PATH", self.db_path):
            log.import_csv_files([self.csv_path], "cm")
        os.unlink(self.csv_path)
        os.rmdir(os.path.dirname(self.csv_path))

        # Second import of the same file — both rows should be skipped
        self.csv_path = _make_csv("20260101", lines)
        with patch("raspisump.log.DB_PATH", self.db_path):
            inserted, skipped, errors = log.import_csv_files(
                [self.csv_path], "cm"
            )
        self.assertEqual(inserted, 0)
        self.assertEqual(skipped, 2)
        self.assertEqual(_row_count(self.db_path), 2)

    def test_duplicate_within_batch_not_inserted_twice(self):
        lines = ["08:00:00,10.5", "08:00:00,10.5"]  # same time twice
        inserted, skipped, errors = self._import("20260101", lines)
        self.assertEqual(inserted, 1)
        self.assertEqual(skipped, 1)

    def test_bad_depth_reported_as_error(self):
        lines = ["08:00:00,10.5", "08:05:00,BAD"]
        inserted, skipped, errors = self._import("20260101", lines)
        self.assertEqual(inserted, 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("BAD", errors[0])

    def test_missing_comma_reported_as_error(self):
        lines = ["08:00:00 10.5"]  # space instead of comma
        inserted, skipped, errors = self._import("20260101", lines)
        self.assertEqual(inserted, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("no comma", errors[0])

    def test_blank_lines_ignored(self):
        lines = ["08:00:00,10.5", "", "08:05:00,11.0", ""]
        inserted, skipped, errors = self._import("20260101", lines)
        self.assertEqual(inserted, 2)
        self.assertEqual(errors, [])

    def test_invalid_filename_reported_as_error(self):
        """A file not matching waterlevel-YYYYMMDD.csv is reported and skipped."""
        d = tempfile.mkdtemp()
        bad_path = os.path.join(d, "readings.csv")
        with open(bad_path, "w") as f:
            f.write("08:00:00,10.5\n")
        try:
            with patch("raspisump.log.DB_PATH", self.db_path):
                inserted, skipped, errors = log.import_csv_files(
                    [bad_path], "cm"
                )
        finally:
            os.unlink(bad_path)
            os.rmdir(d)
        self.assertEqual(inserted, 0)
        self.assertEqual(len(errors), 1)
        self.assertIn("filename", errors[0])

    def test_unreadable_csv_raises_oserror(self):
        """An unreadable CSV file raises OSError which propagates to the caller."""
        self.csv_path = _make_csv("20260101", ["08:00:00,10.5"])
        os.chmod(self.csv_path, 0o000)
        try:
            with patch("raspisump.log.DB_PATH", self.db_path):
                with self.assertRaises(PermissionError):
                    log.import_csv_files([self.csv_path], "cm")
        finally:
            os.chmod(self.csv_path, 0o644)

    def test_multiple_files(self):
        csv1 = _make_csv("20260101", ["08:00:00,10.5", "08:05:00,11.0"])
        csv2 = _make_csv("20260102", ["08:00:00,9.5", "08:05:00,8.0"])
        try:
            with patch("raspisump.log.DB_PATH", self.db_path):
                inserted, skipped, errors = log.import_csv_files(
                    [csv1, csv2], "cm"
                )
        finally:
            for p in [csv1, csv2]:
                os.unlink(p)
                os.rmdir(os.path.dirname(p))
        self.assertEqual(inserted, 4)
        self.assertEqual(skipped, 0)
        self.assertEqual(errors, [])

    def test_unit_mismatch_raises_value_error(self):
        """Importing imperial data into a metric database raises ValueError."""
        seed_csv = _make_csv("20260101", ["08:00:00,10.5"])
        try:
            with patch("raspisump.log.DB_PATH", self.db_path):
                log.import_csv_files([seed_csv], "cm")
        finally:
            os.unlink(seed_csv)
            os.rmdir(os.path.dirname(seed_csv))

        self.csv_path = _make_csv("20260102", ["08:00:00,4.1"])
        with patch("raspisump.log.DB_PATH", self.db_path):
            with self.assertRaises(ValueError) as ctx:
                log.import_csv_files([self.csv_path], "inches")
        self.assertIn("mismatch", str(ctx.exception))
        self.assertIn("cm", str(ctx.exception))
        self.assertIn("inches", str(ctx.exception))
        self.assertEqual(_row_count(self.db_path), 1)
