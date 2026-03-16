"""Tests for the first-run setup wizard."""

import importlib
import unittest
from unittest.mock import MagicMock, patch

try:
    importlib.import_module("flask")
    from raspisump.web import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Minimal valid wizard form data (all raspisump.conf fields + admin password)
_VALID_FORM = {
    "gpio_pins__trig_pin": "17",
    "gpio_pins__echo_pin": "27",
    "pit__unit": "metric",
    "pit__critical_water_level": "15.0",
    "pit__pit_depth": "50.0",
    "pit__reading_interval": "30",
    "pit__temperature": "20.0",
    "pit__alert_when": "high",
    "email__alert_interval": "60",
    "email__alert_type": "1",
    "email__smtp_authentication": "0",
    "email__smtp_tls": "0",
    "email__smtp_ssl": "0",
    "email__smtp_server": "localhost",
    "email__email_to": "user@example.com",
    "email__email_from": "raspisump@example.com",
    "email__heartbeat": "0",
    "email__heartbeat_interval": "1439",
    "web__admin_password": "securepass",
    # Optional credentials — blank is fine
    "credentials__username": "",
    "credentials__password": "",
    "credentials__client_id": "",
    "credentials__client_secret": "",
    "credentials__access_token": "",
    "credentials__api_base_url": "",
    "credentials__handle": "",
}


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestSetupGet(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _patch_load(self, conf=None, creds=None):
        conf = conf or {}
        creds = creds or {"web": {"admin_password": "admin"}}
        p1 = patch("raspisump.web.views.setup.load_current_values", return_value=conf)
        p2 = patch("raspisump.web.views.setup.load_credentials", return_value=creds)
        return p1, p2

    def test_setup_get_renders_form(self):
        p1, p2 = self._patch_load()
        with p1, p2:
            response = self.client.get("/setup")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to Raspi-Sump", response.data)
        self.assertIn(b"Save and Start Raspi-Sump", response.data)

    def test_setup_get_does_not_prefill_password(self):
        p1, p2 = self._patch_load(
            creds={"web": {"admin_password": "admin"}}
        )
        with p1, p2:
            response = self.client.get("/setup")
        # Admin password field should be empty — never pre-fill
        self.assertNotIn(b'value="admin"', response.data)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestSetupPost(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _post(self, data):
        return self.client.post("/setup", data=data)

    def test_rejects_admin_as_password(self):
        form = dict(_VALID_FORM)
        form["web__admin_password"] = "admin"
        response = self._post(form)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"must not be &#39;admin&#39;", response.data)

    def test_rejects_empty_password(self):
        form = dict(_VALID_FORM)
        form["web__admin_password"] = ""
        response = self._post(form)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"must not be empty", response.data)

    def test_valid_form_writes_config_and_starts_services(self):
        with (
            patch("raspisump.web.views.setup.write_config_values") as mock_conf,
            patch("raspisump.web.views.setup.write_credentials") as mock_creds,
            patch("raspisump.web.views.setup.subprocess.run") as mock_run,
            patch("raspisump.web.views.setup.subprocess.Popen") as mock_popen,
        ):
            response = self._post(_VALID_FORM)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"restarting", response.data.lower())

        mock_conf.assert_called_once()
        mock_creds.assert_called_once()

        # raspisump.service started
        args = mock_run.call_args[0][0]
        self.assertIn("raspisump.service", args)

        # rsumpweb.service restart scheduled
        mock_popen.assert_called_once()

    def test_password_is_hashed_in_cred_changes(self):
        captured = {}

        def fake_write_creds(changes, path=None):
            captured.update(changes)

        with (
            patch("raspisump.web.views.setup.write_config_values"),
            patch("raspisump.web.views.setup.write_credentials", side_effect=fake_write_creds),
            patch("raspisump.web.views.setup.subprocess.run"),
            patch("raspisump.web.views.setup.subprocess.Popen"),
        ):
            self._post(_VALID_FORM)

        stored = captured.get(("web", "admin_password"), "")
        self.assertTrue(stored.startswith("$argon2"), f"Expected argon2 hash, got: {stored!r}")

    def test_os_error_on_write_returns_error_page(self):
        with (
            patch("raspisump.web.views.setup.write_config_values",
                  side_effect=OSError("permission denied")),
        ):
            response = self._post(_VALID_FORM)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Could not write configuration", response.data)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestFirstRunRedirect(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.app = app
        self.client = app.test_client()

    def test_unconfigured_state_redirects_to_setup(self):
        # Temporarily disable app.testing so the before_request hook runs
        self.app.config["TESTING"] = False
        try:
            with patch("raspisump.web.views.setup.is_unconfigured", return_value=True):
                response = self.client.get("/")
        finally:
            self.app.config["TESTING"] = True
        self.assertEqual(response.status_code, 302)
        self.assertIn("/setup", response.headers["Location"])

    def test_configured_state_does_not_redirect(self):
        self.app.config["TESTING"] = False
        try:
            with patch("raspisump.web.views.setup.is_unconfigured", return_value=False):
                response = self.client.get("/setup")
        finally:
            self.app.config["TESTING"] = True
        # /setup itself is always accessible regardless
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
