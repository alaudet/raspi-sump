"""Tests for the historical readings view."""

import unittest
from datetime import date as dt_date, timedelta
from unittest.mock import patch

from raspisump.web import create_app

_MOCK_STATS = {
    "min": 10.0, "max": 15.0, "count": 48,
    "last": 12.5, "last_ts": "2026-02-07 23:59:39", "unit": "inches",
}

_MOCK_ROWS = [
    ("2026-02-07 10:00:00", 12.0, "inches"),
    ("2026-02-07 10:30:00", 13.0, "inches"),
]


class TestHistoryPage(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_history_no_params_returns_200(self):
        response = self.client.get("/history/")
        self.assertEqual(response.status_code, 200)

    def test_history_no_params_shows_controls(self):
        response = self.client.get("/history/")
        self.assertIn(b"Last 7 days", response.data)
        self.assertIn(b"Last 30 days", response.data)
        self.assertIn(b"Custom Range", response.data)

    def test_history_single_day_shows_chart_container(self):
        with patch("raspisump.web.views.history.day_stats", return_value=_MOCK_STATS):
            response = self.client.get("/history/?date=2026-02-07")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"chart-history", response.data)

    def test_history_single_day_shows_stats(self):
        with patch("raspisump.web.views.history.day_stats", return_value=_MOCK_STATS):
            response = self.client.get("/history/?date=2026-02-07")
        self.assertIn(b"10.0", response.data)   # min
        self.assertIn(b"15.0", response.data)   # max
        self.assertIn(b"48",   response.data)   # count

    def test_history_single_day_no_data_shows_error(self):
        with patch("raspisump.web.views.history.day_stats", return_value=None):
            response = self.client.get("/history/?date=2020-01-01")
        self.assertIn(b"No readings found", response.data)

    def test_history_multiday_renders_chart_per_day(self):
        response = self.client.get("/history/?days=3")
        self.assertEqual(response.status_code, 200)
        # Expect chart containers for the last 3 days
        today = dt_date.today()
        for i in range(3):
            d = (today - timedelta(days=i)).isoformat().encode()
            self.assertIn(d, response.data)

    def test_history_multiday_caps_at_30(self):
        response = self.client.get("/history/?days=99")
        self.assertEqual(response.status_code, 200)
        # Should render exactly 30 chart containers, not 99
        self.assertEqual(response.data.count(b"chart-container"), 30)

    def test_history_multiday_invalid_defaults_to_7(self):
        response = self.client.get("/history/?days=notanumber")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.count(b"chart-container"), 7)

    def test_history_range_renders_chart(self):
        response = self.client.get(
            "/history/?start=2026-02-07T08:00&end=2026-02-07T20:00"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"chart-range", response.data)

    def test_history_range_end_before_start_shows_error(self):
        response = self.client.get(
            "/history/?start=2026-02-07T20:00&end=2026-02-07T08:00"
        )
        self.assertIn(b"End must be after start", response.data)

    def test_history_range_exceeds_30_days_shows_error(self):
        response = self.client.get(
            "/history/?start=2026-01-01T00:00&end=2026-03-01T00:00"
        )
        self.assertIn(b"30 days", response.data)

    def test_history_range_invalid_format_shows_error(self):
        response = self.client.get("/history/?start=notadate&end=alsonotadate")
        self.assertIn(b"Invalid date", response.data)


class TestReadingsRangeApi(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_range_missing_params_returns_400(self):
        response = self.client.get("/api/readings/range")
        self.assertEqual(response.status_code, 400)

    def test_range_returns_data(self):
        with patch("raspisump.web.views.api.query_readings_range",
                   return_value=_MOCK_ROWS), \
             patch("raspisump.web.views.api._critical_level", return_value=35.0):
            response = self.client.get(
                "/api/readings/range?start=2026-02-07T08:00&end=2026-02-07T20:00"
            )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["data"][0]), 2)
        self.assertEqual(data["unit"], "inches")

    def test_range_no_data_returns_empty(self):
        with patch("raspisump.web.views.api.query_readings_range", return_value=[]), \
             patch("raspisump.web.views.api._critical_level", return_value=None):
            response = self.client.get(
                "/api/readings/range?start=2026-02-07T08:00&end=2026-02-07T20:00"
            )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["data"], [[], []])


if __name__ == "__main__":
    unittest.main()
