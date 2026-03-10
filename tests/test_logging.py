from datetime import datetime
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
        """Test that log_reading writes timestamp and water depth to the correct path."""
        water_depth = 10.5
        logreading = "test-waterlevel"
        m = mock_open()

        with patch("builtins.open", m):
            log.log_reading(logreading, water_depth)

        today = datetime.now().strftime("%Y%m%d")
        m.assert_called_once_with(
            f"/var/lib/raspi-sump/csv/{logreading}-{today}.csv", "a"
        )
        written = "".join(call.args[0] for call in m().write.call_args_list)
        self.assertIn(str(water_depth), written)
        self.assertRegex(written, r"\d{2}:\d{2}:\d{2},")
