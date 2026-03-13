"""Tests for the admin interface views."""

import unittest
from unittest.mock import patch

from raspisump.web import create_app


class TestAdminAuth(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _patch_password(self, password="changeme"):
        return patch("raspisump.web.auth.get_admin_password", return_value=password)

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
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Admin", response.data)


if __name__ == "__main__":
    unittest.main()
