"""Tests for the homepage view."""

import unittest
from unittest.mock import patch

from raspisump.web import create_app


class TestHomePage(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_home_returns_200(self):
        with patch("raspisump.web.views.home.os.path.exists", return_value=False):
            response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_shows_chart_when_file_exists(self):
        with patch("raspisump.web.views.home.os.path.exists", return_value=True), \
             patch("raspisump.web.views.home.os.path.getmtime", return_value=1700000000):
            response = self.client.get("/")
        self.assertIn(b"today.png", response.data)
        self.assertIn(b"?t=1700000000", response.data)

    def test_home_shows_missing_message_when_no_chart(self):
        with patch("raspisump.web.views.home.os.path.exists", return_value=False):
            response = self.client.get("/")
        self.assertIn(b"No chart available", response.data)

    def test_home_shows_today_date(self):
        with patch("raspisump.web.views.home.os.path.exists", return_value=False), \
             patch("raspisump.web.views.home.time.strftime", return_value="2026-03-13"):
            response = self.client.get("/")
        self.assertIn(b"2026-03-13", response.data)


if __name__ == "__main__":
    unittest.main()
