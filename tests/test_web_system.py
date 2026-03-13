"""Tests for raspisump.web.system — service status helpers."""

import unittest
from unittest.mock import patch, MagicMock
import subprocess

from raspisump.web.system import get_service_status, all_service_statuses, SERVICES, get_raspisump_config


SAMPLE_OUTPUT = (
    "ActiveState=active\n"
    "SubState=running\n"
    "LoadState=loaded\n"
    "UnitFileState=enabled\n"
    "MainPID=1234\n"
    "ExecMainStartTimestamp=Fri 2026-03-13 10:00:00 UTC\n"
)


def _mock_run(stdout="", returncode=0):
    result = MagicMock()
    result.stdout = stdout
    result.returncode = returncode
    return result


class TestGetServiceStatus(unittest.TestCase):

    def _run(self, stdout):
        with patch("subprocess.run", return_value=_mock_run(stdout)):
            return get_service_status("raspisump.service")

    def test_returns_dict_on_success(self):
        props = self._run(SAMPLE_OUTPUT)
        self.assertIsNotNone(props)
        self.assertEqual(props["ActiveState"], "active")
        self.assertEqual(props["SubState"], "running")
        self.assertEqual(props["LoadState"], "loaded")
        self.assertEqual(props["UnitFileState"], "enabled")

    def test_main_pid_converted_to_int(self):
        props = self._run(SAMPLE_OUTPUT)
        self.assertEqual(props["MainPID"], 1234)

    def test_main_pid_zero_when_absent(self):
        props = self._run(
            "ActiveState=inactive\nSubState=dead\nLoadState=loaded\n"
            "UnitFileState=disabled\nMainPID=0\nExecMainStartTimestamp=\n"
        )
        self.assertEqual(props["MainPID"], 0)

    def test_returns_none_when_systemctl_missing(self):
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = get_service_status("raspisump.service")
        self.assertIsNone(result)

    def test_returns_none_on_timeout(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("systemctl", 5)):
            result = get_service_status("raspisump.service")
        self.assertIsNone(result)

    def test_returns_none_on_empty_output(self):
        props = self._run("")
        self.assertIsNone(props)


class TestAllServiceStatuses(unittest.TestCase):

    def test_returns_list_for_all_services(self):
        with patch("raspisump.web.system.get_service_status", return_value=None):
            results = all_service_statuses()
        self.assertEqual(len(results), len(SERVICES))
        names = [name for name, _ in results]
        for svc in SERVICES:
            self.assertIn(svc, names)

    def test_each_entry_is_name_props_tuple(self):
        fake_props = {"ActiveState": "active"}
        with patch("raspisump.web.system.get_service_status", return_value=fake_props):
            results = all_service_statuses()
        for name, props in results:
            self.assertIsInstance(name, str)
            self.assertEqual(props, fake_props)


_SAMPLE_CONF = """
[pit]
unit = metric
pit_depth = 72

[gpio_pins]
trig_pin = 17
echo_pin = 27
"""


class TestGetRaspisumpConfig(unittest.TestCase):

    def _read(self, content):
        """Patch configparser.RawConfigParser.read to load *content* instead."""
        def fake_read(self_cp, paths):
            self_cp.read_string(content)
            return paths
        with patch("raspisump.web.system.configparser.RawConfigParser.read", fake_read):
            return get_raspisump_config()

    def test_returns_list_of_section_tuples(self):
        result = self._read(_SAMPLE_CONF)
        self.assertIsNotNone(result)
        sections = [s for s, _ in result]
        self.assertIn("pit", sections)
        self.assertIn("gpio_pins", sections)

    def test_section_items_are_key_value_pairs(self):
        result = self._read(_SAMPLE_CONF)
        pit = dict(next(items for s, items in result if s == "pit"))
        self.assertEqual(pit["unit"], "metric")
        self.assertEqual(pit["pit_depth"], "72")

    def test_returns_none_when_file_missing(self):
        with patch("raspisump.web.system.configparser.RawConfigParser.read", return_value=[]):
            result = get_raspisump_config()
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
