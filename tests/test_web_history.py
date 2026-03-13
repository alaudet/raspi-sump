"""Tests for the historical readings view."""

import unittest
from unittest.mock import patch

from raspisump.web import create_app

_MOCK_STATS = {
    "min": 10.0, "max": 15.0, "count": 48,
    "last": 12.5, "last_ts": "2026-02-07 23:59:39", "unit": "inches",
}


class TestHistoryPage(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_history_no_date_returns_200(self):
        response = self.client.get("/history/")
        self.assertEqual(response.status_code, 200)

    def test_history_no_date_shows_prompt(self):
        response = self.client.get("/history/")
        self.assertIn(b"Select a date", response.data)

    def test_history_with_data_shows_chart(self):
        with patch("raspisump.web.views.history.day_stats", return_value=_MOCK_STATS), \
             patch("raspisump.web.views.history.chart_url_for_date",
                   return_value="/charts/2026/02/20260207.png?t=1000"):
            response = self.client.get("/history/?date=2026-02-07")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"20260207.png", response.data)

    def test_history_with_data_shows_stats(self):
        with patch("raspisump.web.views.history.day_stats", return_value=_MOCK_STATS), \
             patch("raspisump.web.views.history.chart_url_for_date",
                   return_value="/charts/2026/02/20260207.png?t=1000"):
            response = self.client.get("/history/?date=2026-02-07")
        self.assertIn(b"10.0", response.data)   # min
        self.assertIn(b"15.0", response.data)   # max
        self.assertIn(b"48", response.data)      # count

    def test_history_no_data_shows_error(self):
        with patch("raspisump.web.views.history.day_stats", return_value=None):
            response = self.client.get("/history/?date=2020-01-01")
        self.assertIn(b"No readings found", response.data)


if __name__ == "__main__":
    unittest.main()
