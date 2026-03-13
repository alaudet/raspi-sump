"""Tests for the admin interface views."""

import unittest
from unittest.mock import patch

from raspisump.web import create_app

_FAKE_CONFIG = [
    ("pit", [("unit", "metric"), ("pit_depth", "72")]),
    ("gpio_pins", [("trig_pin", "17"), ("echo_pin", "27")]),
]

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

    def _patch_config(self):
        return patch(
            "raspisump.web.views.admin.get_raspisump_config",
            return_value=_FAKE_CONFIG,
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
        with self._patch_services(), self._patch_config():
            response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin", response.data)

    def test_admin_shows_service_status_table(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True
        with self._patch_services(), self._patch_config():
            response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"raspisump.service", response.data)
        self.assertIn(b"active", response.data)
        self.assertIn(b"Service Status", response.data)

    def test_admin_shows_config_section(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True
        with self._patch_services(), self._patch_config():
            response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Configuration", response.data)
        self.assertIn(b"pit", response.data)
        self.assertIn(b"metric", response.data)


if __name__ == "__main__":
    unittest.main()
