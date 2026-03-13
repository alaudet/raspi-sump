"""Tests for the admin CSV import view."""

import io
import unittest
from unittest.mock import patch

from raspisump.web import create_app


class TestCsvImportView(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _auth(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True

    def test_import_page_redirects_when_not_authenticated(self):
        response = self.client.get("/admin/import")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_import_page_returns_200_when_authenticated(self):
        self._auth()
        response = self.client.get("/admin/import")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Import CSV", response.data)
        self.assertIn(b"csvfiles", response.data)

    def test_post_with_no_files_returns_error(self):
        self._auth()
        response = self.client.post("/admin/import", data={"unit": "metric"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"No files selected", response.data)

    def test_post_with_valid_csv_shows_result(self):
        self._auth()
        csv_content = b"14:00:00,55.3\n14:01:00,55.1\n"
        with patch(
            "raspisump.web.views.csvimport.log.import_csv_files",
            return_value=(2, 0, []),
        ):
            response = self.client.post(
                "/admin/import",
                data={
                    "unit": "metric",
                    "csvfiles": (io.BytesIO(csv_content), "waterlevel-20260313.csv"),
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Inserted", response.data)
        self.assertIn(b"Skipped", response.data)

    def test_post_unit_mismatch_shows_error(self):
        self._auth()
        csv_content = b"14:00:00,55.3\n"
        with patch(
            "raspisump.web.views.csvimport.log.import_csv_files",
            side_effect=ValueError("Unit mismatch: database contains 'cm' readings"),
        ):
            response = self.client.post(
                "/admin/import",
                data={
                    "unit": "imperial",
                    "csvfiles": (io.BytesIO(csv_content), "waterlevel-20260313.csv"),
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Unit mismatch", response.data)

    def test_post_with_parse_errors_shows_error_list(self):
        self._auth()
        csv_content = b"badline\n14:00:00,55.3\n"
        with patch(
            "raspisump.web.views.csvimport.log.import_csv_files",
            return_value=(1, 0, ["waterlevel-20260313.csv:1: no comma found"]),
        ):
            response = self.client.post(
                "/admin/import",
                data={
                    "unit": "metric",
                    "csvfiles": (io.BytesIO(csv_content), "waterlevel-20260313.csv"),
                },
                content_type="multipart/form-data",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"no comma found", response.data)


if __name__ == "__main__":
    unittest.main()
