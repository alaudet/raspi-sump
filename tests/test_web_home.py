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
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_shows_chart_container(self):
        response = self.client.get("/")
        self.assertIn(b"chart-today", response.data)

    def test_home_shows_today_date(self):
        with patch("raspisump.web.views.home.time.strftime", return_value="2026-03-13"):
            response = self.client.get("/")
        self.assertIn(b"2026-03-13", response.data)


if __name__ == "__main__":
    unittest.main()
