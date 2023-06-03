import os
import unittest
from datetime import datetime
from unittest import TestCase

# from unittest.mock import patch
from raspisump import log


class TestLoggingFunctions(TestCase):
    def setUp(self):
        self.test_user = os.getlogin()

    def test_log_event(self):
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
        # Clean up the test log file
        os.remove(expected_logfile)

    def test_log_reading(self):
        water_depth = 10.5

        log.log_reading(water_depth)

        expected_filename = f"/home/{self.test_user}/raspi-sump/csv/waterlevel-{datetime.now().strftime('%Y%m%d')}.csv"
        with open(expected_filename) as f:
            csv_content = f.read()

        expected_line = datetime.now().strftime("%H:%M:%S,") + str(water_depth) + "\n"
        self.assertIn(expected_line, csv_content)

        # Clean up the test CSV file
        os.remove(expected_filename)
