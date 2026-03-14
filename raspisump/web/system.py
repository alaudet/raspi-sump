"""Helpers for querying systemd service status and system configuration."""

import configparser
import subprocess

_CONF_PATH = "/etc/raspi-sump/raspisump.conf"


_PROPERTIES = [
    "ActiveState",
    "SubState",
    "LoadState",
    "UnitFileState",
    "MainPID",
    "ExecMainStartTimestamp",
]

SERVICES = [
    "raspisump.service",
    "rsumpweb.service",
    "rsumpwebchart.timer",
]

CONTROLLABLE_SERVICES = [
    "raspisump.service",
    "rsumpweb.service",
    "rsumpwebchart.timer",
]
_VALID_ACTIONS = ("start", "stop", "restart")


def get_service_status(service):
    """Return a dict of systemd properties for *service*.

    Returns None if systemctl is unavailable or the unit is not found.
    Keys: ActiveState, SubState, LoadState, UnitFileState, MainPID,
          ExecMainStartTimestamp.
    """
    try:
        result = subprocess.run(
            ["systemctl", "show", service,
             "--property=" + ",".join(_PROPERTIES),
             "--no-pager"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    props = {}
    for line in result.stdout.splitlines():
        if "=" in line:
            key, _, value = line.partition("=")
            props[key] = value

    if not props:
        return None

    # Normalise MainPID to int
    try:
        props["MainPID"] = int(props.get("MainPID", 0))
    except ValueError:
        props["MainPID"] = 0

    return props


def all_service_statuses():
    """Return a list of (service_name, props_dict_or_None) for SERVICES."""
    return [(svc, get_service_status(svc)) for svc in SERVICES]


def control_service(unit: str, action: str) -> tuple:
    """Run sudo systemctl <action> <unit>. Returns (success: bool, message: str)."""
    if unit not in CONTROLLABLE_SERVICES:
        return False, f"Unknown unit: {unit!r}"
    if action not in _VALID_ACTIONS:
        return False, f"Unknown action: {action!r}"
    try:
        result = subprocess.run(
            ["sudo", "/usr/bin/systemctl", action, unit],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return True, f"{unit} {action}ed successfully."
        return False, result.stderr.strip() or f"{action} failed (exit {result.returncode})"
    except subprocess.TimeoutExpired:
        return False, "systemctl timed out."
    except OSError as e:
        return False, str(e)


def get_raspisump_config():
    """Read raspisump.conf and return a list of (section, [(key, value)]) tuples.

    Reads only raspisump.conf — credentials.conf is never touched.
    Returns None if the file cannot be read.
    """
    cp = configparser.RawConfigParser()
    read = cp.read(_CONF_PATH)
    if not read:
        return None
    return [(section, list(cp.items(section))) for section in cp.sections()]
