"""Tests for raspisump.alerts notification dispatching."""

import sys
from unittest import TestCase
from unittest.mock import MagicMock, patch

sys.modules.setdefault("mastodon", MagicMock())

# alerts.py reads configs at import time via config_values.configuration().
# Stub it so the module imports cleanly without real config files on disk.
import raspisump.config_values as _cv  # noqa: E402
_FAKE_CONFIGS = {
    "alert_type": 1,
    "alert_interval": 15,
    "alert_when": "high",
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
    import raspisump.alerts as alerts  # noqa: E402


class TestDetermineIfAlertFirstRun(TestCase):
    """First-ever alert (no alert_log file) must respect alert_type.

    Regression for B-1: previously the no-alert-log branch unconditionally
    called smtp_alerts(), so a Mastodon-only user would miss their very
    first over-threshold alert.
    """

    def _run(self, alert_type):
        with patch.dict(alerts.configs, {"alert_type": alert_type, "alert_interval": 15}), \
             patch("raspisump.alerts.os.path.isfile", return_value=False), \
             patch("raspisump.alerts.smtp_alerts") as mock_smtp, \
             patch("raspisump.alerts.mastodon_alerts") as mock_mastodon, \
             patch("raspisump.alerts.log.log_event") as mock_log_event:
            alerts.determine_if_alert(42.0)
        return mock_smtp, mock_mastodon, mock_log_event

    def test_first_alert_smtp_when_alert_type_1(self):
        mock_smtp, mock_mastodon, mock_log_event = self._run(alert_type=1)
        mock_smtp.assert_called_once_with(42.0)
        mock_mastodon.assert_not_called()
        mock_log_event.assert_called_once_with("alert_log", "Email SMS Alert Sent")

    def test_first_alert_mastodon_when_alert_type_2(self):
        mock_smtp, mock_mastodon, mock_log_event = self._run(alert_type=2)
        mock_mastodon.assert_called_once_with(42.0)
        mock_smtp.assert_not_called()
        mock_log_event.assert_called_once_with("alert_log", "Mastodon Alert Sent")

    def test_first_alert_no_dispatch_when_alert_type_unknown(self):
        mock_smtp, mock_mastodon, mock_log_event = self._run(alert_type=0)
        mock_smtp.assert_not_called()
        mock_mastodon.assert_not_called()
        mock_log_event.assert_not_called()
