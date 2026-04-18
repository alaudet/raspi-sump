"""H-3 regression tests for session cookie hardening."""

import importlib
import unittest

try:
    importlib.import_module("flask")
    from raspisump.web import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestSessionLifetime(unittest.TestCase):
    """L-2: the 'remember me' session must not outlive 7 days."""

    def test_permanent_session_lifetime_is_seven_days(self):
        from datetime import timedelta
        app = create_app()
        self.assertEqual(
            app.config["PERMANENT_SESSION_LIFETIME"], timedelta(days=7)
        )


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestSessionCookieFlags(unittest.TestCase):
    """create_app() must harden the session cookie against network sniffing,
    JS access, and cross-site navigation."""

    def setUp(self):
        self.app = create_app()

    def test_secure_flag_is_set(self):
        self.assertTrue(self.app.config["SESSION_COOKIE_SECURE"])

    def test_httponly_flag_is_set(self):
        self.assertTrue(self.app.config["SESSION_COOKIE_HTTPONLY"])

    def test_samesite_is_strict(self):
        self.assertEqual(self.app.config["SESSION_COOKIE_SAMESITE"], "Strict")

    def test_login_response_sets_hardened_cookie(self):
        """End-to-end check: the Set-Cookie header on a login includes the
        Secure; HttpOnly; SameSite=Strict attributes."""
        from unittest.mock import patch

        self.app.config["TESTING"] = True
        client = self.app.test_client()
        # test_client defaults to http://; Flask will still emit Secure in the
        # Set-Cookie header when SESSION_COOKIE_SECURE=True, but the test
        # client will NOT actually store it. We only care about the header.
        with patch("raspisump.web.views.admin.check_password", return_value=True):
            response = client.post(
                "/admin/login",
                data={"password": "whatever"},
                base_url="https://localhost",  # emit Set-Cookie as if over TLS
            )
        set_cookie = response.headers.get("Set-Cookie", "")
        self.assertIn("Secure", set_cookie)
        self.assertIn("HttpOnly", set_cookie)
        self.assertIn("SameSite=Strict", set_cookie)


if __name__ == "__main__":
    unittest.main()
