import os
from datetime import datetime
from unittest import TestCase

from raspisump import log


class TestLoggingFunctions(TestCase):
    def setUp(self):
        self.test_user = os.getlogin()

    def test_log_event(self):
        """Test that notifications work correctly"""
        logfile = "test_log.csv"
        notification = "Test notification"

        log.log_event(logfile, notification)

        expected_logfile = f"/home/{self.test_user}/raspi-sump/logs/{logfile}"
        with open(expected_logfile) as f:
            log_content = f.read()

        expected_line = (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S,") + notification + "\n"
        )
        self.assertIn(expected_line, log_content)
        os.remove(expected_logfile)

    def test_log_reading(self):
        """Test that waterlevel readings work correctly"""
        water_depth = 10.5
        logreading = "test-waterlevel"
        log.log_reading(logreading, water_depth)

        expected_filename = f"/home/{self.test_user}/raspi-sump/csv/{logreading}-{datetime.now().strftime('%Y%m%d')}.csv"
        with open(expected_filename) as f:
            csv_content = f.read()

        expected_line = datetime.now().strftime("%H:%M:%S,") + str(water_depth) + "\n"
        self.assertIn(expected_line, csv_content)
        os.remove(expected_filename)
