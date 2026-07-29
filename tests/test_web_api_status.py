"""Tests for the /api/status endpoint."""

import unittest
from unittest.mock import patch

from raspisump.web import create_app


_STATS = {
    "min": 38.1,
    "max": 52.0,
    "count": 540,
    "last": 41.2,
    "last_ts": "2026-07-26 09:20:00",
    "unit": "cm",
}

_PIT = {
    "critical_level": 35.0,
    "pit_depth": 72.0,
    "alert_when": "high",
    "reading_interval": 60,
    "unit": "cm",
}

_EMPTY_PIT = {
    "critical_level": None,
    "pit_depth": None,
    "alert_when": None,
    "reading_interval": None,
    "unit": None,
}


class TestApiStatus(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _get(self, stats=_STATS, pit=_PIT, cycles=4, service=True):
        """Fetch /api/status with every external dependency patched out."""
        with patch("raspisump.web.stats.day_stats", return_value=stats), \
             patch("raspisump.web.views.api._pit_config", return_value=pit), \
             patch("raspisump.web.views.api._cycles_today", return_value=cycles), \
             patch("raspisump.web.views.api._service_active", return_value=service):
            return self.client.get("/api/status")

    def test_returns_200_and_api_version(self):
        response = self._get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["api_version"], 1)

    def test_reports_latest_reading(self):
        payload = self._get().get_json()
        self.assertEqual(payload["level"], 41.2)
        self.assertEqual(payload["unit"], "cm")

    def test_reports_pit_configuration(self):
        payload = self._get().get_json()
        self.assertEqual(payload["critical_level"], 35.0)
        self.assertEqual(payload["pit_depth"], 72.0)
        self.assertEqual(payload["alert_when"], "high")
        self.assertEqual(payload["reading_interval"], 60)

    def test_reports_day_stats(self):
        payload = self._get().get_json()
        self.assertEqual(payload["day"], {"min": 38.1, "max": 52.0, "count": 540})

    def test_last_ts_is_timezone_aware_iso8601(self):
        # Home Assistant rejects naive datetimes for timestamp sensors.
        last_ts = self._get().get_json()["last_ts"]
        self.assertTrue(last_ts.startswith("2026-07-26T09:20:00"))
        offset = last_ts[19:]
        self.assertTrue(
            offset.startswith(("+", "-")) or offset == "Z",
            f"expected a UTC offset, got {last_ts!r}",
        )

    def test_no_readings_returns_nulls_not_an_error(self):
        response = self._get(stats=None)
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertIsNone(payload["level"])
        self.assertIsNone(payload["last_ts"])
        self.assertEqual(payload["day"], {"min": None, "max": None, "count": 0})

    def test_unit_falls_back_to_config_when_no_readings(self):
        # A freshly installed pit has no readings yet, but clients still need to
        # know which unit to label their entities with.
        self.assertEqual(self._get(stats=None).get_json()["unit"], "cm")

    def test_unit_prefers_the_recorded_reading_label(self):
        pit = dict(_PIT, unit="inches")
        self.assertEqual(self._get(pit=pit).get_json()["unit"], "cm")

    def test_unit_is_null_when_unknowable(self):
        self.assertIsNone(self._get(stats=None, pit=_EMPTY_PIT).get_json()["unit"])

    def test_unreadable_config_returns_nulls(self):
        payload = self._get(pit=_EMPTY_PIT).get_json()
        self.assertIsNone(payload["critical_level"])
        self.assertIsNone(payload["pit_depth"])
        self.assertIsNone(payload["alert_when"])

    def test_cycle_detection_disabled_returns_null(self):
        self.assertIsNone(self._get(cycles=None).get_json()["cycles_today"])

    def test_systemctl_unavailable_returns_null(self):
        self.assertIsNone(self._get(service=None).get_json()["service_active"])

    def test_database_failure_does_not_500(self):
        with patch("raspisump.web.stats.day_stats", side_effect=OSError("no db")), \
             patch("raspisump.web.views.api._pit_config", return_value=_PIT), \
             patch("raspisump.web.views.api._cycles_today", return_value=None), \
             patch("raspisump.web.views.api._service_active", return_value=False):
            response = self.client.get("/api/status")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.get_json()["level"])


class TestPitConfig(unittest.TestCase):
    """_pit_config reads the file fresh on every call — see its docstring."""

    def test_missing_file_yields_all_none(self):
        from raspisump.web.views.api import _pit_config
        with patch("raspisump.web.views.api._RASPISUMP_CONF", "/nonexistent/raspisump.conf"):
            self.assertEqual(_pit_config(), _EMPTY_PIT)

    def test_parses_values_from_conf(self):
        import tempfile
        import os
        from raspisump.web.views.api import _pit_config
        fd, path = tempfile.mkstemp(suffix=".conf")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(
                    "[pit]\n"
                    "critical_water_level = 35\n"
                    "pit_depth = 72\n"
                    "alert_when = low\n"
                    "reading_interval = 30\n"
                    "unit = imperial\n"
                )
            with patch("raspisump.web.views.api._RASPISUMP_CONF", path):
                self.assertEqual(
                    _pit_config(),
                    {
                        "critical_level": 35.0,
                        "pit_depth": 72.0,
                        "alert_when": "low",
                        "reading_interval": 30,
                        "unit": "inches",
                    },
                )
        finally:
            os.unlink(path)

    def test_partial_conf_leaves_missing_keys_none(self):
        import tempfile
        import os
        from raspisump.web.views.api import _pit_config
        fd, path = tempfile.mkstemp(suffix=".conf")
        try:
            with os.fdopen(fd, "w") as f:
                f.write("[pit]\ncritical_water_level = 35\n")
            with patch("raspisump.web.views.api._RASPISUMP_CONF", path):
                values = _pit_config()
        finally:
            os.unlink(path)
        self.assertEqual(values["critical_level"], 35.0)
        self.assertIsNone(values["pit_depth"])
        self.assertIsNone(values["reading_interval"])


if __name__ == "__main__":
    unittest.main()
