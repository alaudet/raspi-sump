"""Helpers for querying systemd service status."""

import subprocess


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
