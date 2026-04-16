"""Tests for raspisump.emailtest dispatching."""

import io
import sys
from contextlib import redirect_stdout
from unittest import TestCase
from unittest.mock import MagicMock, patch

sys.modules.setdefault("mastodon", MagicMock())

# emailtest.py reads configs at import time via config_values.configuration().
# Stub it so the module imports cleanly without real config files on disk.
import raspisump.config_values as _cv  # noqa: E402
_FAKE_CONFIGS = {
    "alert_type": 1,
    "unit": "metric",
    "email_to": "to@example.com",
    "email_from": "from@example.com",
    "smtp_authentication": 0,
    "smtp_tls": 0,
    "smtp_ssl": 0,
    "smtp_server": "smtp.example.com",
    "username": "",
    "password": "",
    "client_id": "",
    "client_secret": "",
    "access_token": "",
    "api_base_url": "",
    "handle": "",
}
with patch.object(_cv, "configuration", return_value=dict(_FAKE_CONFIGS)):
    import raspisump.emailtest as emailtest  # noqa: E402


class TestNotificationsInvalidAlertType(TestCase):
    """When alert_type is neither 1 nor 2, test_notifications() must
    surface the misconfiguration to stdout (visible in CLI and captured
    by the web support view) and write an entry to error_log.

    Previously the else-branch was silent, so a user running `alerttest`
    with alert_type=0 or 3 saw no output and no log entry."""

    def _run(self, alert_type):
        buf = io.StringIO()
        with patch.dict(emailtest.configs, {"alert_type": alert_type}), \
             patch("raspisump.emailtest.test_email") as mock_email, \
             patch("raspisump.emailtest.test_mastodon") as mock_mastodon, \
             patch("raspisump.emailtest.log.log_event") as mock_log_event, \
             redirect_stdout(buf):
            emailtest.test_notifications()
        return buf.getvalue(), mock_email, mock_mastodon, mock_log_event

    def test_invalid_alert_type_zero_prints_and_logs(self):
        output, mock_email, mock_mastodon, mock_log_event = self._run(alert_type=0)
        mock_email.assert_not_called()
        mock_mastodon.assert_not_called()
        self.assertIn("alert_type", output)
        self.assertIn("invalid", output.lower())
        mock_log_event.assert_called_once()
        self.assertEqual(mock_log_event.call_args[0][0], "error_log")

    def test_invalid_alert_type_three_prints_and_logs(self):
        output, mock_email, mock_mastodon, mock_log_event = self._run(alert_type=3)
        mock_email.assert_not_called()
        mock_mastodon.assert_not_called()
        self.assertIn("alert_type", output)
        mock_log_event.assert_called_once()

    def test_valid_alert_type_1_dispatches_email(self):
        _, mock_email, mock_mastodon, mock_log_event = self._run(alert_type=1)
        mock_email.assert_called_once()
        mock_mastodon.assert_not_called()
        mock_log_event.assert_not_called()

    def test_valid_alert_type_2_dispatches_mastodon(self):
        _, mock_email, mock_mastodon, mock_log_event = self._run(alert_type=2)
        mock_mastodon.assert_called_once()
        mock_email.assert_not_called()
        mock_log_event.assert_not_called()
