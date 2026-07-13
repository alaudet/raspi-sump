"""Tests for rsumpsupport CLI function."""

import unittest
from unittest.mock import patch


_FAKE_CONFIGS = {
    "critical_water_level": 20,
    "pit_depth": 60,
    "reading_interval": 30,
    "temperature": 20,
    "trig_pin": 17,
    "echo_pin": 27,
    "unit": "metric",
    "alert_type": 1,
    "smtp_tls": 0,
    "smtp_ssl": 0,
    "alert_when": "high",
    "alert_interval": 5,
    "heartbeat": 0,
    "heartbeat_interval": 24,
    "cycle_detection": "no",
    "username": "",
    "password": "",
    "client_id": "",
    "client_secret": "",
    "access_token": "",
    "api_base_url": "",
    "handle": "",
    "email_to": "test@example.com",
    "email_from": "from@example.com",
    "smtp_authentication": 0,
    "smtp_server": "localhost",
}

_TODAY_ROWS = [("2026-03-19 08:00:00", 22.5, "cm")]


def _run_and_capture(today_rows=None, db_error=None, log_namespace="", commands=None):
    """Run rsumpsupport with all external calls mocked; return written content.

    *log_namespace* is what get_log_namespace() reports for the units;
    if *commands* is a list, every check_output command is appended to it.
    """
    from raspisump.cli import rsumpsupport

    if today_rows is None:
        today_rows = _TODAY_ROWS

    captured = {}
    real_open = open

    def fake_check_output(command, *args, **kwargs):
        if commands is not None:
            commands.append(command)
        return "mocked output"

    def fake_open(path, mode="r", *args, **kwargs):
        if "w" in str(mode):
            class _F:
                def write(self, data):
                    captured["content"] = data

                def __enter__(self):
                    return self

                def __exit__(self, *a):
                    pass

            return _F()
        return real_open(path, mode, *args, **kwargs)

    qr_kwargs = {"side_effect": db_error} if db_error else {"return_value": today_rows}

    with (
        patch("raspisump.config_values.configuration", return_value=_FAKE_CONFIGS),
        patch("subprocess.check_output", side_effect=fake_check_output),
        patch("raspisump.web.system.get_log_namespace", return_value=log_namespace),
        patch("raspisump.log.query_readings", **qr_kwargs),
        patch("builtins.open", side_effect=fake_open),
        patch("os.makedirs"),
        patch("time.strftime", return_value="2026-03-19"),
    ):
        rsumpsupport()

    return captured.get("content", "")


class TestRsumpsupportJournalNamespace(unittest.TestCase):
    """journalctl must target the units' journal namespace when one is set."""

    def _journal_commands(self, log_namespace):
        commands = []
        _run_and_capture(log_namespace=log_namespace, commands=commands)
        return [c for c in commands if c[0] == "journalctl"]

    def test_namespace_flag_present_when_units_use_one(self):
        commands = self._journal_commands("raspisump")
        self.assertTrue(commands)
        for command in commands:
            self.assertIn("--namespace=raspisump", command)

    def test_no_namespace_flag_on_default_journal(self):
        commands = self._journal_commands("")
        self.assertTrue(commands)
        for command in commands:
            self.assertNotIn("--namespace=raspisump", command)

    def test_both_units_queried(self):
        commands = self._journal_commands("raspisump")
        units = [c[c.index("-u") + 1] for c in commands]
        self.assertIn("raspisump.service", units)
        self.assertIn("rsumpweb.service", units)


class TestRsumpsupportContent(unittest.TestCase):

    def setUp(self):
        self.content = _run_and_capture()

    def test_contains_cycle_detection(self):
        self.assertIn("cycle_detection:", self.content)

    def test_contains_journal_raspisump(self):
        self.assertIn("Last 50 journal entries for raspisump.service", self.content)

    def test_contains_journal_rsumpweb(self):
        self.assertIn("Last 50 journal entries for rsumpweb.service", self.content)

    def test_contains_todays_readings(self):
        self.assertIn("Today's readings", self.content)
        self.assertIn("2026-03-19 08:00:00", self.content)
        self.assertIn("22.5", self.content)

    def test_no_readings_shows_fallback(self):
        content = _run_and_capture(today_rows=[])
        self.assertIn("No readings found for today", content)

    def test_contains_standard_fields(self):
        for field in ("critical_water_level", "pit_depth", "alert_when", "heartbeat"):
            self.assertIn(f"{field}:", self.content)

    def test_no_combined_journal_line(self):
        """Old combined journalctl -b line should be gone."""
        self.assertNotIn("raspisump.service -u rsumpweb.service -b", self.content)


class TestRsumpsupportDbError(unittest.TestCase):

    def setUp(self):
        import sqlite3
        self.content = _run_and_capture(
            db_error=sqlite3.OperationalError("no such table: readings")
        )

    def test_does_not_raise(self):
        """rsumpsupport must complete and write a file even when the DB is broken."""
        self.assertIsInstance(self.content, str)
        self.assertTrue(len(self.content) > 0)

    def test_db_error_captured_in_file(self):
        self.assertIn("ERROR: could not query readings database", self.content)

    def test_traceback_in_file(self):
        self.assertIn("no such table: readings", self.content)


if __name__ == "__main__":
    unittest.main()
