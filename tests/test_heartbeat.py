"""Tests for raspisump.heartbeat dispatching."""

import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

sys.modules.setdefault("mastodon", MagicMock())

# heartbeat.py reads configs at import time via config_values.configuration().
# Stub it so the module imports cleanly without real config files on disk.
import raspisump.config_values as _cv  # noqa: E402
_FAKE_CONFIGS = {
    "alert_type": 1,
    "heartbeat_interval": 1440,
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
    import raspisump.heartbeat as heartbeat  # noqa: E402


class TestDetermineIfHeartbeatInvalidAlertType(TestCase):
    """Regression for B-3: heartbeat must signal misconfiguration when
    alert_type is neither 1 nor 2, instead of silently doing nothing."""

    def setUp(self):
        # Reset the module-level "already warned" flag between tests.
        heartbeat._invalid_alert_type_logged = False

    def _run(self, alert_type):
        with patch.dict(heartbeat.configs, {"alert_type": alert_type}), \
             patch("raspisump.heartbeat.heartbeat_alerts") as mock_smtp, \
             patch("raspisump.heartbeat.mastodon_heartbeat_alerts") as mock_mastodon, \
             patch("raspisump.heartbeat.log.log_event") as mock_log_event, \
             patch("raspisump.heartbeat.os.path.isfile", return_value=False):
            heartbeat.determine_if_heartbeat()
        return mock_smtp, mock_mastodon, mock_log_event

    def test_invalid_alert_type_zero_logs_error_and_skips(self):
        mock_smtp, mock_mastodon, mock_log_event = self._run(alert_type=0)
        mock_smtp.assert_not_called()
        mock_mastodon.assert_not_called()
        mock_log_event.assert_called_once()
        args = mock_log_event.call_args[0]
        self.assertEqual(args[0], "error_log")
        self.assertIn("alert_type", args[1])
        self.assertIn("invalid", args[1].lower())

    def test_invalid_alert_type_three_logs_error_and_skips(self):
        mock_smtp, mock_mastodon, mock_log_event = self._run(alert_type=3)
        mock_smtp.assert_not_called()
        mock_mastodon.assert_not_called()
        mock_log_event.assert_called_once()
        self.assertEqual(mock_log_event.call_args[0][0], "error_log")

    def test_invalid_alert_type_logs_only_once_per_process(self):
        """Avoid spamming error_log when called every reading cycle."""
        with patch.dict(heartbeat.configs, {"alert_type": 0}), \
             patch("raspisump.heartbeat.log.log_event") as mock_log_event, \
             patch("raspisump.heartbeat.os.path.isfile", return_value=False):
            heartbeat.determine_if_heartbeat()
            heartbeat.determine_if_heartbeat()
            heartbeat.determine_if_heartbeat()
        self.assertEqual(mock_log_event.call_count, 1)

    def test_valid_alert_type_does_not_trigger_error_branch(self):
        mock_smtp, mock_mastodon, mock_log_event = self._run(alert_type=1)
        mock_smtp.assert_called_once()
        # log_event was called for "Heartbeat Email Sent", not for the error.
        for call in mock_log_event.call_args_list:
            self.assertNotEqual(call.args[0], "error_log")
