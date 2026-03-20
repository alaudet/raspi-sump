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


class TestDetectCycles(TestCase):

    def _make_sump_readings(self, cycles=2, baseline=70.0, trough=35.0, pts_per_phase=10):
        """Generate synthetic sump pit readings with a given number of cycles.

        Each cycle: baseline → falls to trough → recovers to baseline.
        """
        rows = []
        ts_counter = 0

        def _ts(n):
            h, m = divmod(n, 60)
            return f"2026-03-15 {h:02d}:{m:02d}:00"

        # Start at baseline
        rows.append((_ts(ts_counter), baseline, "cm"))
        ts_counter += 1

        for _ in range(cycles):
            # Fall to trough
            step = (baseline - trough) / pts_per_phase
            for i in range(1, pts_per_phase + 1):
                rows.append((_ts(ts_counter), baseline - step * i, "cm"))
                ts_counter += 1
            # Rise back to baseline
            for i in range(1, pts_per_phase + 1):
                rows.append((_ts(ts_counter), trough + step * i, "cm"))
                ts_counter += 1
            rows.append((_ts(ts_counter), baseline, "cm"))
            ts_counter += 1

        return rows

    def test_detects_correct_cycle_count(self):
        for n in (1, 2, 3, 5):
            with self.subTest(cycles=n):
                rows = self._make_sump_readings(cycles=n)
                result = log.detect_cycles(rows, alert_when="high")
                self.assertEqual(len(result), n)

    def test_returns_tuples_of_timestamps(self):
        rows = self._make_sump_readings(cycles=1)
        cycles = log.detect_cycles(rows, alert_when="high")
        self.assertEqual(len(cycles), 1)
        arm_ts, reset_ts = cycles[0]
        self.assertIsInstance(arm_ts, str)
        self.assertIsInstance(reset_ts, str)
        self.assertLess(arm_ts, reset_ts)

    def test_flat_readings_return_no_cycles(self):
        rows = [("2026-03-15 00:00:00", 70.0, "cm")] * 20
        result = log.detect_cycles(rows, alert_when="high")
        self.assertEqual(result, [])

    def test_too_few_readings_return_no_cycles(self):
        rows = [("2026-03-15 00:00:00", 70.0, "cm")] * 3
        result = log.detect_cycles(rows, alert_when="high")
        self.assertEqual(result, [])

    def test_insufficient_variation_returns_no_cycles(self):
        # Less than 1 unit of variation — below the minimum span
        rows = [("2026-03-15 00:00:00", 70.0 + (i % 3) * 0.3, "cm") for i in range(20)]
        result = log.detect_cycles(rows, alert_when="high")
        self.assertEqual(result, [])

    def test_in_progress_cycle_counted(self):
        """A cycle that is armed but not yet reset should appear with reset_ts=None."""
        # Two complete cycles + one that never recovers
        rows = self._make_sump_readings(cycles=2)
        # Append a drop that never recovers to baseline
        last_ts = rows[-1][0]
        h, m = int(last_ts[11:13]), int(last_ts[14:16])
        def _next_ts():
            nonlocal h, m
            m += 1
            if m >= 60:
                m = 0
                h += 1
            return f"2026-03-15 {h:02d}:{m:02d}:00"

        trough = 35.0
        for _ in range(5):
            rows.append((_next_ts(), trough, "cm"))

        result = log.detect_cycles(rows, alert_when="high")
        self.assertEqual(len(result), 3)
        arm_ts, reset_ts = result[-1]
        self.assertIsInstance(arm_ts, str)
        self.assertIsNone(reset_ts)

    def test_cistern_mode_detects_cycles(self):
        """For alert_when='low', direction is inverted (depth increases when water drops)."""
        rows = []
        ts_counter = 0

        def _ts(n):
            h, m = divmod(n, 60)
            return f"2026-03-15 {h:02d}:{m:02d}:00"

        baseline = 20.0   # full cistern — sensor close to water
        empty = 80.0      # empty cistern — sensor far from water
        pts = 10
        step = (empty - baseline) / pts

        rows.append((_ts(ts_counter), baseline, "cm"))
        ts_counter += 1
        for _ in range(2):
            for i in range(1, pts + 1):
                rows.append((_ts(ts_counter), baseline + step * i, "cm"))
                ts_counter += 1
            for i in range(1, pts + 1):
                rows.append((_ts(ts_counter), empty - step * i, "cm"))
                ts_counter += 1
            rows.append((_ts(ts_counter), baseline, "cm"))
            ts_counter += 1

        result = log.detect_cycles(rows, alert_when="low")
        self.assertEqual(len(result), 2)


class TestQueryReadingsRange(TestCase):
    def setUp(self):
        self.rows = [
            ("2026-03-10 08:00:00", 10.5, "cm"),
            ("2026-03-10 09:00:00", 11.0, "cm"),
            ("2026-03-11 08:00:00", 9.5, "cm"),
            ("2026-03-11 14:30:00", 12.0, "cm"),
        ]
        self.db_path = _make_db(self.rows)

    def tearDown(self):
        os.unlink(self.db_path)

    def test_single_day_returns_only_that_day(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings_range("2026-03-10")
        self.assertEqual(len(rows), 2)
        for ts, _, _ in rows:
            self.assertTrue(ts.startswith("2026-03-10"))

    def test_date_range_returns_all_matching(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings_range("2026-03-10", "2026-03-11")
        self.assertEqual(len(rows), 4)

    def test_time_range_filters_within_day(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings_range("2026-03-11", start_time="14:00", end_time="23:59")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "2026-03-11 14:30:00")

    def test_start_time_only_excludes_earlier(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings_range("2026-03-10", start_time="09:00")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], "2026-03-10 09:00:00")

    def test_no_results_returns_empty_list(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings_range("2099-01-01")
        self.assertEqual(rows, [])

    def test_results_in_chronological_order(self):
        with patch("raspisump.log.DB_PATH", self.db_path):
            rows = log.query_readings_range("2026-03-10", "2026-03-11")
        timestamps = [r[0] for r in rows]
        self.assertEqual(timestamps, sorted(timestamps))
