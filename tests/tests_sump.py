import os
from unittest import TestCase
import raspisump.reading as reading
import raspisump.alerts as alerts
import raspisump.heartbeat as heartbeat
import configparser  # Python3

config = configparser.RawConfigParser()
user = os.getlogin()
config.read(f"/home/{user}/raspi-sump/raspisump.conf")

configs = {
    "pit_depth": config.getint("pit", "pit_depth"),
    "unit": config.get("pit", "unit"),
}

try:
    configs["alert_when"] = config.get("pit", "alert_when")
except configparser.NoOptionError:
    configs["alert_when"] = "high"


class TestRaspisump(TestCase):
    def test_water_reading(self):
        """Test that a proper reading is being returned."""
        pit_depth = configs["pit_depth"]
        value = reading.water_reading()
        self.assertIsInstance(value, float)
        self.assertLessEqual(value, pit_depth)

    def test_unit_types(self):
        """Test that a proper unit type is being selected."""
        measurement = alerts.unit_types()
        self.assertIsInstance(measurement, str)
        self.assertIn(measurement, ["inches", "centimeters"])

    def test_email_content(self):
        """Test that the right email alert is being returned."""
        water_depth = 35
        email_contents = alerts.email_content(water_depth)
        self.assertIsInstance(email_contents, str)
        self.assertRegex(email_contents, r"^From:")
        self.assertRegex(email_contents, r"Low Water|Sump Pump")

    def test_heartbeat_content(self):
        """Test that the right email heartbeat is being returned."""
        heartbeat_email_contents = heartbeat.heartbeat_email_content()
        self.assertIsInstance(heartbeat_email_contents, str)
        self.assertRegex(heartbeat_email_contents, r"^From:")
        self.assertRegex(heartbeat_email_contents, r"Raspi")

    def test_heartbeat_last_row(self):
        """Test last heartbeat time is correct"""
        heartbeat_log = f"/home/{user}/raspi-sump/logs/heartbeat_log"
        if os.path.isfile(heartbeat_log):
            last_alert = heartbeat.get_last_alert_time()
            self.assertIsInstance(last_alert, str)
            self.assertEqual(len(last_alert), 19)

    def test_hostname_return(self):
        """Test that hostname is being returned for alert."""
        hostname = alerts.host_name()
        self.assertIsInstance(hostname, str)
