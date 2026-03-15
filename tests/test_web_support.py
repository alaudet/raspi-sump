"""Tests for the support page view."""

import importlib
import os
import tempfile
import unittest
from unittest.mock import patch

try:
    importlib.import_module("flask")
    from raspisump.web import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestSupportPage(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _auth(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True

    def test_support_redirects_when_not_authenticated(self):
        response = self.client.get("/admin/support")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_support_returns_200_when_authenticated(self):
        self._auth()
        response = self.client.get("/admin/support")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Support", response.data)

    def test_support_shows_download_and_alerttest_buttons(self):
        self._auth()
        response = self.client.get("/admin/support")
        self.assertIn(b"Generate", response.data)
        self.assertIn(b"Send Test Alert", response.data)

    def test_download_action_returns_file(self):
        self._auth()
        # Create a real temp file so send_file can serve it
        with tempfile.NamedTemporaryFile(
            suffix=".txt", delete=False, mode="w"
        ) as f:
            f.write("support data")
            tmp_path = f.name
        try:
            with patch(
                "raspisump.cli.rsumpsupport",
                return_value=tmp_path,
            ):
                response = self.client.post(
                    "/admin/support", data={"action": "download"}
                )
            self.assertEqual(response.status_code, 200)
            self.assertIn("attachment", response.headers.get("Content-Disposition", ""))
        finally:
            os.unlink(tmp_path)

    def test_download_action_shows_error_on_exception(self):
        self._auth()
        with patch(
            "raspisump.cli.rsumpsupport",
            side_effect=OSError("Permission denied"),
        ):
            response = self.client.post(
                "/admin/support", data={"action": "download"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Permission denied", response.data)

    def test_alerttest_shows_success(self):
        self._auth()
        with patch(
            "raspisump.web.views.support._run_alerttest",
            return_value=(True, "Email sent successfully"),
        ):
            response = self.client.post(
                "/admin/support", data={"action": "alerttest"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Success", response.data)
        self.assertIn(b"Email sent successfully", response.data)

    def test_alerttest_shows_failure(self):
        self._auth()
        with patch(
            "raspisump.web.views.support._run_alerttest",
            return_value=(False, "Connection refused"),
        ):
            response = self.client.post(
                "/admin/support", data={"action": "alerttest"}
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Failed", response.data)
        self.assertIn(b"Connection refused", response.data)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestRunAlerttest(unittest.TestCase):

    def test_success_detected_from_output(self):
        from raspisump.web.views.support import _run_alerttest

        def _fake_notify():
            print("Email sent successfully")

        with patch("raspisump.emailtest.test_notifications", side_effect=_fake_notify):
            success, output = _run_alerttest()

        self.assertTrue(success)
        self.assertIn("successfully", output)

    def test_failure_detected_from_output(self):
        from raspisump.web.views.support import _run_alerttest

        def _fake_notify():
            print("Connection timed out")

        with patch("raspisump.emailtest.test_notifications", side_effect=_fake_notify):
            success, output = _run_alerttest()

        self.assertFalse(success)

    def test_exception_returns_failure(self):
        from raspisump.web.views.support import _run_alerttest

        with patch(
            "raspisump.emailtest.test_notifications",
            side_effect=RuntimeError("SMTP error"),
        ):
            success, output = _run_alerttest()

        self.assertFalse(success)
        self.assertIn("SMTP error", output)

    def test_no_output_returns_failure(self):
        from raspisump.web.views.support import _run_alerttest

        with patch("raspisump.emailtest.test_notifications", return_value=None):
            success, output = _run_alerttest()

        self.assertFalse(success)


if __name__ == "__main__":
    unittest.main()
