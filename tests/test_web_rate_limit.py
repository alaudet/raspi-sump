"""Tests for H-2 login rate limiting."""

import importlib
import unittest
from unittest.mock import patch

from raspisump.web import auth

try:
    importlib.import_module("flask")
    from raspisump.web import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


class TestRateLimitHelpers(unittest.TestCase):
    """Unit tests for the helpers in raspisump.web.auth — no Flask required."""

    def setUp(self):
        auth._FAILED_ATTEMPTS.clear()

    def tearDown(self):
        auth._FAILED_ATTEMPTS.clear()

    def test_fresh_ip_is_not_rate_limited(self):
        self.assertFalse(auth.is_rate_limited("1.2.3.4"))

    def test_below_threshold_is_not_rate_limited(self):
        for _ in range(auth._MAX_FAILED_ATTEMPTS - 1):
            auth.record_failed_attempt("1.2.3.4")
        self.assertFalse(auth.is_rate_limited("1.2.3.4"))

    def test_at_threshold_is_rate_limited(self):
        with patch("raspisump.log.log_event"):
            for _ in range(auth._MAX_FAILED_ATTEMPTS):
                auth.record_failed_attempt("1.2.3.4")
        self.assertTrue(auth.is_rate_limited("1.2.3.4"))

    def test_other_ips_are_unaffected(self):
        with patch("raspisump.log.log_event"):
            for _ in range(auth._MAX_FAILED_ATTEMPTS):
                auth.record_failed_attempt("1.2.3.4")
        self.assertTrue(auth.is_rate_limited("1.2.3.4"))
        self.assertFalse(auth.is_rate_limited("5.6.7.8"))

    def test_clear_failed_attempts_resets_counter(self):
        with patch("raspisump.log.log_event"):
            for _ in range(auth._MAX_FAILED_ATTEMPTS):
                auth.record_failed_attempt("1.2.3.4")
        auth.clear_failed_attempts("1.2.3.4")
        self.assertFalse(auth.is_rate_limited("1.2.3.4"))

    def test_stale_attempts_are_pruned(self):
        # Simulate an old attempt outside the window
        now = 10_000.0
        old = now - auth._WINDOW_SECONDS - 1
        auth._FAILED_ATTEMPTS["1.2.3.4"] = [old] * auth._MAX_FAILED_ATTEMPTS
        with patch("time.monotonic", return_value=now):
            self.assertFalse(auth.is_rate_limited("1.2.3.4"))

    def test_threshold_crossing_logs_forensics_event_once(self):
        with patch("raspisump.log.log_event") as mock_log:
            for _ in range(auth._MAX_FAILED_ATTEMPTS + 3):
                auth.record_failed_attempt("1.2.3.4")
        # Only the attempt that hit _MAX exactly should log
        self.assertEqual(mock_log.call_count, 1)
        category, message = mock_log.call_args[0]
        self.assertEqual(category, "error_log")
        self.assertIn("1.2.3.4", message)
        self.assertIn(str(auth._MAX_FAILED_ATTEMPTS), message)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestClientIP(unittest.TestCase):
    """client_ip() should trust nginx's X-Real-IP header."""

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.app = app

    def test_x_real_ip_is_preferred(self):
        with self.app.test_request_context(headers={"X-Real-IP": "9.9.9.9"}):
            from flask import request
            self.assertEqual(auth.client_ip(request), "9.9.9.9")

    def test_falls_back_to_remote_addr(self):
        with self.app.test_request_context(environ_overrides={"REMOTE_ADDR": "127.0.0.1"}):
            from flask import request
            self.assertEqual(auth.client_ip(request), "127.0.0.1")


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestLoginRateLimit(unittest.TestCase):
    """End-to-end: /admin/login returns 429 once threshold is hit."""

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()
        auth._FAILED_ATTEMPTS.clear()

    def tearDown(self):
        auth._FAILED_ATTEMPTS.clear()

    def _post(self, password="wrong", headers=None):
        return self.client.post(
            "/admin/login",
            data={"password": password},
            headers=headers or {"X-Real-IP": "10.0.0.1"},
        )

    def test_invalid_password_returns_401(self):
        with patch("raspisump.web.views.admin.check_password", return_value=False):
            response = self._post()
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Invalid password", response.data)

    def test_rate_limit_returns_429_after_threshold(self):
        with (
            patch("raspisump.web.views.admin.check_password", return_value=False),
            patch("raspisump.log.log_event"),
        ):
            for _ in range(auth._MAX_FAILED_ATTEMPTS):
                self._post()
            response = self._post()
        self.assertEqual(response.status_code, 429)
        self.assertIn(b"Too many failed login attempts", response.data)

    def test_rate_limit_blocks_correct_password(self):
        """While locked out, even the correct password is rejected."""
        with (
            patch("raspisump.web.views.admin.check_password", return_value=False),
            patch("raspisump.log.log_event"),
        ):
            for _ in range(auth._MAX_FAILED_ATTEMPTS):
                self._post()
        with patch("raspisump.web.views.admin.check_password", return_value=True):
            response = self._post(password="correct")
        self.assertEqual(response.status_code, 429)
        # Session must not be set during lockout
        with self.client.session_transaction() as sess:
            self.assertFalse(sess.get("admin_logged_in"))

    def test_successful_login_clears_counter(self):
        with (
            patch("raspisump.web.views.admin.check_password", return_value=False),
            patch("raspisump.log.log_event"),
        ):
            for _ in range(auth._MAX_FAILED_ATTEMPTS - 1):
                self._post()
        with patch("raspisump.web.views.admin.check_password", return_value=True):
            response = self._post(password="correct")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(auth.is_rate_limited("10.0.0.1"))

    def test_rate_limit_is_per_ip(self):
        with (
            patch("raspisump.web.views.admin.check_password", return_value=False),
            patch("raspisump.log.log_event"),
        ):
            for _ in range(auth._MAX_FAILED_ATTEMPTS):
                self._post(headers={"X-Real-IP": "10.0.0.1"})
            # Different IP still gets the normal 401, not 429
            response = self._post(headers={"X-Real-IP": "10.0.0.2"})
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
