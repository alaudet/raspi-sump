"""Tests for auth.py — argon2 password hashing and check_password logic."""

import importlib
import unittest
from unittest.mock import patch

try:
    importlib.import_module("argon2")
    ARGON2_AVAILABLE = True
except ImportError:
    ARGON2_AVAILABLE = False


@unittest.skipUnless(ARGON2_AVAILABLE, "argon2-cffi not installed")
class TestHashPassword(unittest.TestCase):

    def test_returns_argon2_hash(self):
        from raspisump.web.auth import hash_password
        self.assertTrue(hash_password("testpassword").startswith("$argon2"))

    def test_different_calls_produce_different_hashes(self):
        from raspisump.web.auth import hash_password
        self.assertNotEqual(hash_password("same"), hash_password("same"))


@unittest.skipUnless(ARGON2_AVAILABLE, "argon2-cffi not installed")
class TestCheckPasswordPlaintext(unittest.TestCase):

    def test_match_returns_true(self):
        with patch("raspisump.web.auth.get_admin_password", return_value="secret"), \
             patch("raspisump.web.auth._write_hashed_password"):
            from raspisump.web.auth import check_password
            self.assertTrue(check_password("secret"))

    def test_mismatch_returns_false(self):
        with patch("raspisump.web.auth.get_admin_password", return_value="secret"):
            from raspisump.web.auth import check_password
            self.assertFalse(check_password("wrong"))

    def test_match_triggers_migration(self):
        with patch("raspisump.web.auth.get_admin_password", return_value="secret"), \
             patch("raspisump.web.auth._write_hashed_password") as mock_write:
            from raspisump.web.auth import check_password
            check_password("secret")
            mock_write.assert_called_once()
            written = mock_write.call_args[0][0]
            self.assertTrue(written.startswith("$argon2"))

    def test_mismatch_does_not_migrate(self):
        with patch("raspisump.web.auth.get_admin_password", return_value="secret"), \
             patch("raspisump.web.auth._write_hashed_password") as mock_write:
            from raspisump.web.auth import check_password
            check_password("wrong")
            mock_write.assert_not_called()


@unittest.skipUnless(ARGON2_AVAILABLE, "argon2-cffi not installed")
class TestCheckPasswordHashed(unittest.TestCase):

    def setUp(self):
        from raspisump.web.auth import hash_password
        self.hashed = hash_password("mypassword")

    def test_correct_password_returns_true(self):
        with patch("raspisump.web.auth.get_admin_password", return_value=self.hashed), \
             patch("raspisump.web.auth._write_hashed_password"):
            from raspisump.web.auth import check_password
            self.assertTrue(check_password("mypassword"))

    def test_wrong_password_returns_false(self):
        with patch("raspisump.web.auth.get_admin_password", return_value=self.hashed):
            from raspisump.web.auth import check_password
            self.assertFalse(check_password("wrongpassword"))


@unittest.skipUnless(ARGON2_AVAILABLE, "argon2-cffi not installed")
class TestWriteHashedPasswordSilentOnError(unittest.TestCase):

    def test_oserror_is_silently_ignored(self):
        from raspisump.web.auth import _write_hashed_password
        with patch("raspisump.web.credentials_helpers.write_credentials",
                   side_effect=OSError("no file")):
            # Should not raise
            _write_hashed_password("$argon2id$somehash")


if __name__ == "__main__":
    unittest.main()
