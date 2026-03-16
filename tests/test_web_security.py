"""Tests for the admin Security page."""

import importlib
import unittest
from unittest.mock import patch

try:
    importlib.import_module("flask")
    importlib.import_module("argon2")
    from raspisump.web import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

_BLANK_CREDS = {
    "web": {"admin_password": "admin"},
    "credentials": {
        "username": "", "password": "", "client_id": "", "client_secret": "",
        "access_token": "", "api_base_url": "", "handle": "",
    },
}

_ALL_FIELDS = {
    "web__admin_password": "newpassword",
    "credentials__username": "",
    "credentials__password": "",
    "credentials__client_id": "",
    "credentials__client_secret": "",
    "credentials__access_token": "",
    "credentials__api_base_url": "",
    "credentials__handle": "",
}


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestSecurityPage(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _auth(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True

    def test_security_page_requires_login(self):
        response = self.client.get("/admin/security")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_security_page_returns_200_when_authenticated(self):
        self._auth()
        with patch("raspisump.web.views.security.load_credentials",
                   return_value=_BLANK_CREDS):
            response = self.client.get("/admin/security")
        self.assertEqual(response.status_code, 200)

    def test_password_saved_as_argon2_hash(self):
        self._auth()
        with patch("raspisump.web.views.security.load_credentials",
                   return_value=_BLANK_CREDS), \
             patch("raspisump.web.views.security.write_credentials") as mock_write:
            self.client.post("/admin/security", data=_ALL_FIELDS)
        written = mock_write.call_args[0][0]
        saved_password = written[("web", "admin_password")]
        self.assertTrue(saved_password.startswith("$argon2"),
                        f"Expected argon2 hash, got: {saved_password!r}")

    def test_empty_password_returns_error(self):
        self._auth()
        data = dict(_ALL_FIELDS)
        data["web__admin_password"] = ""
        with patch("raspisump.web.views.security.load_credentials",
                   return_value=_BLANK_CREDS):
            response = self.client.post("/admin/security", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"must not be empty", response.data)


if __name__ == "__main__":
    unittest.main()
