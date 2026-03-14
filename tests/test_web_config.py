"""Tests for the admin configuration editor view and helpers."""

import configparser
import os
import tempfile
import unittest
from unittest.mock import patch

from raspisump.web.config_helpers import (
    load_current_values,
    validate_config_form,
    write_config_values,
)


# ---------------------------------------------------------------------------
# Minimal config file used by all helper tests
# ---------------------------------------------------------------------------

_SAMPLE_CONF = """\
# This is a comment — must be preserved
[gpio_pins]

# Trig comment
trig_pin = 17

# Echo comment
echo_pin = 27

[pit]
unit = metric
critical_water_level = 35
pit_depth = 72
reading_interval = 60
temperature = 20
alert_when = high

[charts]
line_color = FB921D

[email]
alert_interval = 5
alert_type = 1
smtp_authentication = 0
smtp_tls = 0
smtp_ssl = 0
smtp_server = localhost:25
email_to =
email_from =
heartbeat = 0
heartbeat_interval = 10079
"""


def _write_temp_conf(content: str) -> str:
    """Write content to a temp file and return its path."""
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".conf", delete=False)
    f.write(content)
    f.close()
    return f.name


class TestLoadCurrentValues(unittest.TestCase):

    def setUp(self):
        self.path = _write_temp_conf(_SAMPLE_CONF)

    def tearDown(self):
        os.unlink(self.path)

    def test_returns_nested_dict(self):
        vals = load_current_values(self.path)
        self.assertIsInstance(vals, dict)
        self.assertIn("gpio_pins", vals)
        self.assertIn("pit", vals)

    def test_correct_values(self):
        vals = load_current_values(self.path)
        self.assertEqual(vals["gpio_pins"]["trig_pin"], "17")
        self.assertEqual(vals["pit"]["unit"], "metric")
        self.assertEqual(vals["email"]["heartbeat_interval"], "10079")

    def test_missing_file_returns_empty(self):
        vals = load_current_values("/nonexistent/path.conf")
        self.assertEqual(vals, {})


class TestValidateConfigForm(unittest.TestCase):

    def _make_form(self, overrides=None):
        """Build a valid form dict, apply any overrides."""
        data = {
            "gpio_pins__trig_pin": "17",
            "gpio_pins__echo_pin": "27",
            "pit__unit": "metric",
            "pit__critical_water_level": "35",
            "pit__pit_depth": "72",
            "pit__reading_interval": "60",
            "pit__temperature": "20",
            "pit__alert_when": "high",
            "charts__line_color": "FB921D",
            "email__alert_interval": "5",
            "email__alert_type": "1",
            "email__smtp_authentication": "0",
            "email__smtp_tls": "0",
            "email__smtp_ssl": "0",
            "email__smtp_server": "localhost:25",
            "email__email_to": "",
            "email__email_from": "",
            "email__heartbeat": "0",
            "email__heartbeat_interval": "10079",
        }
        if overrides:
            data.update(overrides)
        return data

    def test_valid_form_returns_no_errors(self):
        _, errors = validate_config_form(self._make_form())
        self.assertEqual(errors, [])

    def test_valid_form_returns_all_changes(self):
        changes, _ = validate_config_form(self._make_form())
        self.assertIn(("gpio_pins", "trig_pin"), changes)
        self.assertIn(("email", "heartbeat_interval"), changes)

    def test_invalid_integer_returns_error(self):
        _, errors = validate_config_form(self._make_form({"gpio_pins__trig_pin": "abc"}))
        self.assertTrue(any("Trig Pin" in e for e in errors))

    def test_invalid_float_returns_error(self):
        _, errors = validate_config_form(
            self._make_form({"pit__critical_water_level": "notanumber"})
        )
        self.assertTrue(any("Critical Water Level" in e for e in errors))

    def test_invalid_select_returns_error(self):
        _, errors = validate_config_form(self._make_form({"pit__unit": "celsius"}))
        self.assertTrue(any("Unit of Measure" in e for e in errors))

    def test_valid_select_passes(self):
        _, errors = validate_config_form(self._make_form({"pit__unit": "imperial"}))
        self.assertEqual(errors, [])

    def test_zero_reading_interval_is_valid(self):
        _, errors = validate_config_form(self._make_form({"pit__reading_interval": "0"}))
        self.assertEqual(errors, [])

    def test_multiple_errors_reported(self):
        bad = self._make_form({
            "gpio_pins__trig_pin": "x",
            "gpio_pins__echo_pin": "y",
        })
        _, errors = validate_config_form(bad)
        self.assertEqual(len(errors), 2)


class TestWriteConfigValues(unittest.TestCase):

    def setUp(self):
        self.path = _write_temp_conf(_SAMPLE_CONF)

    def tearDown(self):
        os.unlink(self.path)

    def test_comments_preserved(self):
        write_config_values({("gpio_pins", "trig_pin"): "18"}, self.path)
        with open(self.path) as f:
            content = f.read()
        self.assertIn("# This is a comment", content)
        self.assertIn("# Trig comment", content)
        self.assertIn("# Echo comment", content)

    def test_value_updated(self):
        write_config_values({("gpio_pins", "trig_pin"): "18"}, self.path)
        cp = configparser.RawConfigParser()
        cp.read(self.path)
        self.assertEqual(cp.get("gpio_pins", "trig_pin"), "18")

    def test_unchanged_values_intact(self):
        write_config_values({("gpio_pins", "trig_pin"): "18"}, self.path)
        cp = configparser.RawConfigParser()
        cp.read(self.path)
        self.assertEqual(cp.get("gpio_pins", "echo_pin"), "27")
        self.assertEqual(cp.get("pit", "unit"), "metric")

    def test_multiple_changes(self):
        write_config_values(
            {("gpio_pins", "trig_pin"): "18",
             ("pit", "unit"): "imperial",
             ("email", "heartbeat"): "1"},
            self.path,
        )
        cp = configparser.RawConfigParser()
        cp.read(self.path)
        self.assertEqual(cp.get("gpio_pins", "trig_pin"), "18")
        self.assertEqual(cp.get("pit", "unit"), "imperial")
        self.assertEqual(cp.get("email", "heartbeat"), "1")

    def test_blank_value_written(self):
        write_config_values({("email", "email_to"): ""}, self.path)
        cp = configparser.RawConfigParser()
        cp.read(self.path)
        self.assertEqual(cp.get("email", "email_to"), "")

    def test_section_headers_preserved(self):
        write_config_values({("pit", "unit"): "imperial"}, self.path)
        with open(self.path) as f:
            content = f.read()
        self.assertIn("[gpio_pins]", content)
        self.assertIn("[pit]", content)
        self.assertIn("[charts]", content)
        self.assertIn("[email]", content)


# ---------------------------------------------------------------------------
# View tests (require Flask — run on Pi only)
# ---------------------------------------------------------------------------

try:
    import importlib
    importlib.import_module("flask")
    from raspisump.web import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestConfigView(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()
        self.conf_path = _write_temp_conf(_SAMPLE_CONF)

    def tearDown(self):
        os.unlink(self.conf_path)

    def _auth(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True

    def test_config_page_redirects_when_not_authenticated(self):
        response = self.client.get("/admin/config")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def _patch_conf(self):
        """Return a context manager that patches _CONF_PATH in both modules."""
        from contextlib import ExitStack
        stack = ExitStack()
        stack.enter_context(
            patch("raspisump.web.config_helpers._CONF_PATH", self.conf_path))
        stack.enter_context(
            patch("raspisump.web.views.config._CONF_PATH", self.conf_path))
        return stack

    def test_config_page_returns_200(self):
        self._auth()
        with self._patch_conf():
            response = self.client.get("/admin/config")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Configuration", response.data)
        self.assertIn(b"trig_pin", response.data)

    def test_config_raw_returns_text(self):
        self._auth()
        with self._patch_conf():
            response = self.client.get("/admin/config/raw")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/plain", response.content_type)
        self.assertIn(b"trig_pin", response.data)

    def test_config_post_valid_saves_and_shows_success(self):
        self._auth()
        form = {
            "gpio_pins__trig_pin": "18",
            "gpio_pins__echo_pin": "27",
            "pit__unit": "metric",
            "pit__critical_water_level": "35",
            "pit__pit_depth": "72",
            "pit__reading_interval": "60",
            "pit__temperature": "20",
            "pit__alert_when": "high",
            "charts__line_color": "FB921D",
            "email__alert_interval": "5",
            "email__alert_type": "1",
            "email__smtp_authentication": "0",
            "email__smtp_tls": "0",
            "email__smtp_ssl": "0",
            "email__smtp_server": "localhost:25",
            "email__email_to": "",
            "email__email_from": "",
            "email__heartbeat": "0",
            "email__heartbeat_interval": "10079",
        }
        with self._patch_conf():
            response = self.client.post("/admin/config", data=form)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Configuration saved", response.data)

    def test_config_post_invalid_shows_errors(self):
        self._auth()
        form = {"gpio_pins__trig_pin": "notanumber"}
        with self._patch_conf():
            response = self.client.post("/admin/config", data=form)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Trig Pin", response.data)


if __name__ == "__main__":
    unittest.main()
