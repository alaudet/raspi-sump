"""Tests for the admin backup / export view."""

import io
import unittest
import zipfile
from unittest.mock import patch

from raspisump.web import create_app
from raspisump.web.views.backup import build_backup_zip, _EXPORT_FILES


class TestBuildBackupZip(unittest.TestCase):

    def test_returns_bytesio(self):
        with patch("raspisump.web.views.backup.zipfile.ZipFile.write"):
            buf = build_backup_zip()
        self.assertIsInstance(buf, io.BytesIO)

    def test_zip_includes_available_files(self):
        """Files that exist on disk should appear in the archive."""
        import tempfile, os

        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            f.write(b"fake db")
            db_path = f.name
        with tempfile.NamedTemporaryFile(suffix=".conf", delete=False) as f:
            f.write(b"fake conf")
            conf_path = f.name

        fake_files = [(db_path, "raspisump.db"), (conf_path, "raspisump.conf")]
        try:
            with patch("raspisump.web.views.backup._EXPORT_FILES", fake_files):
                buf = build_backup_zip()
            with zipfile.ZipFile(buf) as zf:
                names = zf.namelist()
            self.assertIn("raspisump.db", names)
            self.assertIn("raspisump.conf", names)
        finally:
            os.unlink(db_path)
            os.unlink(conf_path)

    def test_missing_files_skipped_silently(self):
        """Missing source files should not raise — they are omitted from the zip."""
        fake_files = [("/nonexistent/file.db", "file.db")]
        with patch("raspisump.web.views.backup._EXPORT_FILES", fake_files):
            buf = build_backup_zip()
        with zipfile.ZipFile(buf) as zf:
            self.assertEqual(zf.namelist(), [])

    def test_export_files_list_has_expected_entries(self):
        arc_names = [arc for _, arc in _EXPORT_FILES]
        self.assertIn("raspisump.db", arc_names)
        self.assertIn("raspisump.conf", arc_names)


class TestBackupDownloadView(unittest.TestCase):

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def _auth(self):
        with self.client.session_transaction() as sess:
            sess["admin_logged_in"] = True

    def _patch_zip(self):
        empty_buf = io.BytesIO()
        with zipfile.ZipFile(empty_buf, "w"):
            pass
        empty_buf.seek(0)
        return patch(
            "raspisump.web.views.backup.build_backup_zip",
            return_value=empty_buf,
        )

    def test_download_redirects_to_login_when_not_authenticated(self):
        response = self.client.get("/admin/backup/download")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login", response.headers["Location"])

    def test_download_returns_zip_when_authenticated(self):
        self._auth()
        with self._patch_zip():
            response = self.client.get("/admin/backup/download")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/zip", response.content_type)

    def test_download_filename_contains_date(self):
        self._auth()
        with self._patch_zip(), patch("raspisump.web.views.backup.time.strftime", return_value="2026-03-13"):
            response = self.client.get("/admin/backup/download")
        disposition = response.headers.get("Content-Disposition", "")
        self.assertIn("raspisump-backup-2026-03-13.zip", disposition)


if __name__ == "__main__":
    unittest.main()
