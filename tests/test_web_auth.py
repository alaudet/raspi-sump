"""Tests for raspisump.web.auth — password verification paths."""

import sys
import unittest
from unittest.mock import MagicMock, patch


# argon2 is provided by python3-argon2 on the Pi. On dev machines without
# it, stub the imports so auth.py can be imported.
#
# The mismatch/verification classes MUST be the real argon2 ones on the Pi
# so that check_password's except clause actually catches them (subclass
# identity matters). InvalidHashError varies between argon2 versions, so
# it's always a local class — used only to simulate "unexpected exception"
# in the catch-all log test.
try:
    from argon2.exceptions import (
        VerificationError as _VerificationError,
        VerifyMismatchError as _VerifyMismatchError,
    )
except ImportError:
    class _VerifyMismatchError(Exception):
        pass

    class _VerificationError(Exception):
        pass

    _fake_argon2 = MagicMock()
    _fake_argon2.PasswordHasher = MagicMock()
    _fake_exceptions = MagicMock()
    _fake_exceptions.VerifyMismatchError = _VerifyMismatchError
    _fake_exceptions.VerificationError = _VerificationError
    sys.modules.setdefault("argon2", _fake_argon2)
    sys.modules.setdefault("argon2.exceptions", _fake_exceptions)


class _InvalidHashError(Exception):
    """Local stand-in for a malformed-hash exception — shape doesn't matter
    because check_password's catch-all except Exception handles it."""
    pass


from raspisump.web import auth  # noqa: E402


class TestCheckPasswordUnexpectedError(unittest.TestCase):
    """L-4: a malformed hash (or any unexpected error in argon2) must be
    logged so the admin can diagnose a lockout, not silently swallowed."""

    def _hasher_raising(self, exc):
        """Return a PasswordHasher-like mock whose verify() raises exc."""
        ph = MagicMock()
        ph.verify.side_effect = exc
        hasher_cls = MagicMock(return_value=ph)
        return hasher_cls

    def test_malformed_hash_logs_error_and_returns_false(self):
        with (
            patch.object(auth, "get_admin_password", return_value="$argon2id$garbled"),
            patch("argon2.PasswordHasher",
                  self._hasher_raising(_InvalidHashError("Invalid hash"))),
            patch("raspisump.log.log_event") as mock_log,
        ):
            result = auth.check_password("anything")

        self.assertFalse(result)
        mock_log.assert_called_once()
        category, message = mock_log.call_args[0]
        self.assertEqual(category, "error_log")
        self.assertIn("Admin password verification error", message)
        self.assertIn("InvalidHashError", message)
        self.assertIn("Invalid hash", message)
        self.assertIn("credentials.conf", message)

    def test_wrong_password_does_not_log(self):
        """A normal mismatch is not an error — no log noise."""
        with (
            patch.object(auth, "get_admin_password", return_value="$argon2id$realhash"),
            patch("argon2.PasswordHasher",
                  self._hasher_raising(_VerifyMismatchError())),
            patch("raspisump.log.log_event") as mock_log,
        ):
            result = auth.check_password("wrong")

        self.assertFalse(result)
        mock_log.assert_not_called()

    def test_verification_error_does_not_log(self):
        """argon2.VerificationError (malformed verify call) is handled but not logged —
        this path is for the narrow argon2-internal mismatch family, not data corruption."""
        with (
            patch.object(auth, "get_admin_password", return_value="$argon2id$realhash"),
            patch("argon2.PasswordHasher",
                  self._hasher_raising(_VerificationError())),
            patch("raspisump.log.log_event") as mock_log,
        ):
            result = auth.check_password("anything")

        self.assertFalse(result)
        mock_log.assert_not_called()


if __name__ == "__main__":
    unittest.main()
