import os
from unittest import TestCase
import raspisump.reading as reading
import raspisump.alerts as alerts
import raspisump.heartbeat as heartbeat
import raspisump.config_values as config_values

user = os.getlogin()

configs = config_values.configuration()


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

    def test_config_dict(self):
        """Test that the config is returned as a dict with the expected length"""
        self.assertIsInstance(configs, dict)
        self.assertEqual(len(configs), 20)

    def test_key_existence(self):
        """Test that all keys are present in the dict"""
        keys_to_check = [
            "critical_water_level",
            "pit_depth",
            "reading_interval",
            "temperature",
            "trig_pin",
            "echo_pin",
            "unit",
            "email_to",
            "email_from",
            "smtp_authentication",
            "smtp_tls",
            "smtp_server",
            "username",
            "password",
            "alert_when",
            "alert_interval",
            "smtp_ssl",
            "heartbeat",
            "heartbeat_interval",
            "line_color",
        ]

        for key in keys_to_check:
            self.assertIn(key, configs.keys())

    def test_dict_value_types(self):
        """Test proper value types in returned dict"""
        expected_values = {
            "critical_water_level": int,
            "pit_depth": int,
            "reading_interval": int,
            "temperature": int,
            "trig_pin": int,
            "echo_pin": int,
            "unit": str,
            "email_to": str,
            "email_from": str,
            "smtp_authentication": int,
            "smtp_tls": int,
            "smtp_server": str,
            "username": str,
            "password": str,
            "alert_when": str,
            "alert_interval": int,
            "smtp_ssl": int,
            "heartbeat": int,
            "heartbeat_interval": int,
            "line_color": str,
        }

        for key, expected_type in expected_values.items():
            self.assertIsInstance(configs[key], expected_type)
