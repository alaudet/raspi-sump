import os
import sqlite3
import tempfile
from unittest import TestCase
from unittest.mock import patch, mock_open

from raspisump import log


class TestLoggingFunctions(TestCase):
    def test_log_event(self):
        """Test that log_event writes timestamp and notification to the correct path."""
        logfile = "test_log"
        notification = "Test notification"
        m = mock_open()

        with patch("builtins.open", m):
            log.log_event(logfile, notification)

        m.assert_called_once_with(f"/var/log/raspi-sump/{logfile}", "a")
        written = "".join(call.args[0] for call in m().write.call_args_list)
        self.assertIn(notification, written)
        self.assertRegex(written, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},")

    def test_log_reading(self):
        """Test that log_reading inserts a row into the SQLite database."""
        water_depth = 10.5
        unit = "metric"
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        try:
            with patch("raspisump.log.DB_PATH", db_path):
                log.log_reading(water_depth, unit)
            conn = sqlite3.connect(db_path)
            row = conn.execute(
                "SELECT water_depth, unit FROM readings ORDER BY id DESC LIMIT 1"
            ).fetchone()
            conn.close()
        finally:
            os.unlink(db_path)
        self.assertEqual(row[0], water_depth)
        self.assertEqual(row[1], "cm")
