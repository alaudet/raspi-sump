"""Tests for the admin interface views."""

import importlib
import subprocess
import unittest
from unittest.mock import MagicMock, patch

from raspisump.web.system import control_service

try:
    importlib.import_module("flask")
    from raspisump.web import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

_FAKE_SERVICES = [
    ("raspisump.service", {
        "ActiveState": "active", "SubState": "running",
        "LoadState": "loaded", "UnitFileState": "enabled",
        "MainPID": 42, "ExecMainStartTimestamp": "Fri 2026-03-13 10:00:00 UTC",
    }),
    ("rsumpweb.service", {
        "ActiveState": "active", "SubState": "running",
        "LoadState": "loaded", "UnitFileState": "enabled",
        "MainPID": 43, "ExecMainStartTimestamp": "Fri 2026-03-13 10:00:01 UTC",
    }),
    ("rsumpwebchart.timer", {
        "ActiveState": "active", "SubState": "waiting",
        "LoadState": "loaded", "UnitFileState": "enabled",
        "MainPID": 0, "ExecMainStartTimestamp": "",
    }),
]


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestAdminAuth(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _patch_password(self, password="changeme"):
        return patch("raspisump.web.auth.get_admin_password", return_value=password)

    def _patch_services(self):
        return patch(
            "raspisump.web.views.admin.all_service_statuses",
            return_value=_FAKE_SERVICES,
        )

    def test_admin_redirects_to_login_when_not_authenticated(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_login_page_returns_200(self):
        response = self.client.get("/admin/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin Login", response.data)

    def test_login_already_authenticated_redirects_to_admin(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True
        response = self.client.get("/admin/login")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/", response.headers["Location"])

    def test_login_success_sets_session_and_redirects(self):
        with self._patch_password("changeme"):
            response = self.client.post(
                "/admin/login", data={"password": "changeme"}, follow_redirects=False
            )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/", response.headers["Location"])
        with self.client.session_transaction() as sess:
            self.assertTrue(sess.get("admin_logged_in"))

    def test_login_failure_returns_401_with_error(self):
        with self._patch_password("changeme"):
            response = self.client.post(
                "/admin/login", data={"password": "wrongpassword"}
            )
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Invalid password", response.data)

    def test_logout_clears_session_and_redirects_home(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True
        response = self.client.get("/admin/logout", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.headers["Location"])
        with self.client.session_transaction() as sess:
            self.assertFalse(sess.get("admin_logged_in"))

    def test_admin_accessible_when_authenticated(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True
        with self._patch_services():
            response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin", response.data)

    def test_admin_shows_service_status_table(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True
        with self._patch_services():
            response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"raspisump.service", response.data)
        self.assertIn(b"active", response.data)
        self.assertIn(b"Service Status", response.data)


class TestControlService(unittest.TestCase):

    def _mock_run(self, returncode=0, stderr=""):
        m = MagicMock()
        m.returncode = returncode
        m.stderr = stderr
        return m

    def test_valid_restart_returns_success(self):
        with patch("raspisump.web.system.subprocess.run",
                   return_value=self._mock_run(0)) as mock_run:
            ok, msg = control_service("raspisump.service", "restart")
        self.assertTrue(ok)
        self.assertIn("restart", msg)
        mock_run.assert_called_once()

    def test_valid_stop_returns_success(self):
        with patch("raspisump.web.system.subprocess.run",
                   return_value=self._mock_run(0)):
            ok, msg = control_service("raspisump.service", "stop")
        self.assertTrue(ok)

    def test_invalid_unit_returns_error(self):
        ok, msg = control_service("bad.service", "restart")
        self.assertFalse(ok)
        self.assertIn("bad.service", msg)

    def test_invalid_action_returns_error(self):
        ok, msg = control_service("raspisump.service", "enable")
        self.assertFalse(ok)
        self.assertIn("enable", msg)

    def test_nonzero_exit_returns_error(self):
        with patch("raspisump.web.system.subprocess.run",
                   return_value=self._mock_run(1, "Failed to restart unit")):
            ok, msg = control_service("raspisump.service", "restart")
        self.assertFalse(ok)
        self.assertIn("Failed to restart unit", msg)

    def test_timeout_returns_error(self):
        with patch("raspisump.web.system.subprocess.run",
                   side_effect=subprocess.TimeoutExpired(["sudo"], 15)):
            ok, msg = control_service("raspisump.service", "restart")
        self.assertFalse(ok)
        self.assertIn("timed out", msg)

    def test_os_error_returns_error(self):
        with patch("raspisump.web.system.subprocess.run",
                   side_effect=OSError("sudo not found")):
            ok, msg = control_service("raspisump.service", "restart")
        self.assertFalse(ok)
        self.assertIn("sudo not found", msg)


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestServiceActionView(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _auth(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True

    def _patch_control(self, success=True, message="raspisump.service restarted successfully."):
        return patch("raspisump.web.views.admin.control_service",
                     return_value=(success, message))

    def test_service_action_redirects_when_not_authenticated(self):
        response = self.client.post("/admin/service",
                                    data={"unit": "raspisump.service", "action": "restart"})
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_valid_action_redirects_to_admin(self):
        self._auth()
        with self._patch_control(True, "raspisump.service restarted successfully."):
            response = self.client.post("/admin/service",
                                        data={"unit": "raspisump.service", "action": "restart"},
                                        follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/", response.headers["Location"])

    def test_success_flash_appears_on_redirect(self):
        self._auth()
        with self._patch_control(True, "raspisump.service restarted successfully."):
            response = self.client.post("/admin/service",
                                        data={"unit": "raspisump.service", "action": "restart"},
                                        follow_redirects=True)
        self.assertIn(b"restarted successfully", response.data)

    def test_error_flash_appears_on_redirect(self):
        self._auth()
        with self._patch_control(False, "Unknown unit: 'bad.service'"):
            response = self.client.post("/admin/service",
                                        data={"unit": "bad.service", "action": "restart"},
                                        follow_redirects=True)
        self.assertIn(b"Unknown unit", response.data)


if __name__ == "__main__":
    unittest.main()
