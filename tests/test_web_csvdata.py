"""Tests for the combined admin CSV import / export view."""

import io
import unittest
import zipfile
from unittest.mock import patch

from raspisump.web import create_app


_SINGLE_DAY_ROWS = [
    ("2026-03-13 14:00:00", 55.3, "cm"),
    ("2026-03-13 14:01:00", 55.1, "cm"),
]

_MULTI_DAY_ROWS = [
    ("2026-03-12 08:00:00", 54.0, "cm"),
    ("2026-03-13 14:00:00", 55.3, "cm"),
    ("2026-03-13 14:01:00", 55.1, "cm"),
]


class TestCsvDataView(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _auth(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def test_page_redirects_when_not_authenticated(self):
        response = self.client.get("/admin/csv")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_page_returns_200_when_authenticated(self):
        self._auth()
        response = self.client.get("/admin/csv")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Import", response.data)
        self.assertIn(b"Export", response.data)

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def test_import_with_no_files_returns_error(self):
        self._auth()
        response = self.client.post("/admin/csv",
                                    data={"action": "import", "unit": "metric"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No files selected", response.data)

    def test_import_with_valid_csv_shows_result(self):
        self._auth()
        csv_content = b"14:00:00,55.3\n14:01:00,55.1\n"
        with patch("raspisump.web.views.csvdata.log.import_csv_files",
                   return_value=(2, 0, [])):
            response = self.client.post(
                "/admin/csv",
                data={
                    "action": "import",
                    "unit": "metric",
                    "csvfiles": (io.BytesIO(csv_content), "waterlevel-20260313.csv"),
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Inserted", response.data)
        self.assertIn(b"Skipped", response.data)

    def test_import_unit_mismatch_shows_error(self):
        self._auth()
        csv_content = b"14:00:00,55.3\n"
        with patch("raspisump.web.views.csvdata.log.import_csv_files",
                   side_effect=ValueError("Unit mismatch: database contains 'cm'")):
            response = self.client.post(
                "/admin/csv",
                data={
                    "action": "import",
                    "unit": "imperial",
                    "csvfiles": (io.BytesIO(csv_content), "waterlevel-20260313.csv"),
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Unit mismatch", response.data)

    def test_import_parse_errors_shown(self):
        self._auth()
        csv_content = b"badline\n14:00:00,55.3\n"
        with patch("raspisump.web.views.csvdata.log.import_csv_files",
                   return_value=(1, 0, ["waterlevel-20260313.csv:1: no comma found"])):
            response = self.client.post(
                "/admin/csv",
                data={
                    "action": "import",
                    "unit": "metric",
                    "csvfiles": (io.BytesIO(csv_content), "waterlevel-20260313.csv"),
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"no comma found", response.data)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def test_export_without_start_date_shows_error(self):
        self._auth()
        response = self.client.post("/admin/csv", data={"action": "export"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Start date is required", response.data)

    def test_export_no_data_shows_error(self):
        self._auth()
        with patch("raspisump.web.views.csvdata.log.query_readings_range",
                   return_value=[]):
            response = self.client.post("/admin/csv",
                                        data={"action": "export",
                                              "start_date": "2026-03-13"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No readings found", response.data)

    def test_export_single_day_returns_csv(self):
        self._auth()
        with patch("raspisump.web.views.csvdata.log.query_readings_range",
                   return_value=_SINGLE_DAY_ROWS):
            response = self.client.post("/admin/csv",
                                        data={"action": "export",
                                              "start_date": "2026-03-13"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.content_type)
        self.assertIn(b"14:00:00,55.3\n", response.data)

    def test_export_single_day_csv_filename(self):
        self._auth()
        with patch("raspisump.web.views.csvdata.log.query_readings_range",
                   return_value=_SINGLE_DAY_ROWS):
            response = self.client.post("/admin/csv",
                                        data={"action": "export",
                                              "start_date": "2026-03-13"})
        disposition = response.headers.get("Content-Disposition", "")
        self.assertIn("waterlevel-20260313.csv", disposition)

    def test_export_multi_day_returns_zip(self):
        self._auth()
        with patch("raspisump.web.views.csvdata.log.query_readings_range",
                   return_value=_MULTI_DAY_ROWS):
            response = self.client.post(
                "/admin/csv",
                data={"action": "export",
                      "start_date": "2026-03-12", "end_date": "2026-03-13"},
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("zip", response.content_type)

    def test_export_multi_day_zip_contains_per_day_files(self):
        self._auth()
        with patch("raspisump.web.views.csvdata.log.query_readings_range",
                   return_value=_MULTI_DAY_ROWS):
            response = self.client.post(
                "/admin/csv",
                data={"action": "export",
                      "start_date": "2026-03-12", "end_date": "2026-03-13"},
            )
        zf = zipfile.ZipFile(io.BytesIO(response.data))
        self.assertIn("waterlevel-20260312.csv", zf.namelist())
        self.assertIn("waterlevel-20260313.csv", zf.namelist())

    def test_export_time_range_passed_for_single_day(self):
        self._auth()
        with patch("raspisump.web.views.csvdata.log.query_readings_range",
                   return_value=_SINGLE_DAY_ROWS) as mock_fn:
            self.client.post(
                "/admin/csv",
                data={"action": "export", "start_date": "2026-03-13",
                      "start_time": "14:00", "end_time": "14:30"},
            )
        mock_fn.assert_called_once_with("2026-03-13", "2026-03-13", "14:00", "14:30")

    def test_export_time_range_ignored_for_multi_day(self):
        self._auth()
        with patch("raspisump.web.views.csvdata.log.query_readings_range",
                   return_value=_MULTI_DAY_ROWS) as mock_fn:
            self.client.post(
                "/admin/csv",
                data={"action": "export",
                      "start_date": "2026-03-12", "end_date": "2026-03-13",
                      "start_time": "08:00", "end_time": "14:00"},
            )
        mock_fn.assert_called_once_with("2026-03-12", "2026-03-13", None, None)


if __name__ == "__main__":
    unittest.main()
