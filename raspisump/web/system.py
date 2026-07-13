"""Helpers for querying systemd service status and system configuration."""

import configparser
import glob
import os
import subprocess

_LOG_DIR = "/var/log/raspi-sump"

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
]

CONTROLLABLE_SERVICES = [
    "raspisump.service",
    "rsumpweb.service",
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
    """Run systemctl <action> <unit>. Returns (success: bool, message: str).

    The web process runs unprivileged; systemd asks polkit to authorize the
    request, which the packaged rule grants for exactly these units and
    actions (see conf/polkit/49-raspisump.rules).
    """
    if unit not in CONTROLLABLE_SERVICES:
        return False, f"Unknown unit: {unit!r}"
    if action not in _VALID_ACTIONS:
        return False, f"Unknown action: {action!r}"
    try:
        result = subprocess.run(
            ["systemctl", action, unit],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0:
            return True, f"{unit} {action}ed successfully."
        stderr = result.stderr.strip()
        # "Access denied" = polkitd absent; "Interactive authentication
        # required" = polkitd running but no rule grants this request.
        if "Access denied" in stderr or "Interactive authentication required" in stderr:
            return False, (
                f"Not authorized to {action} {unit} — is the raspisump "
                f"polkit rule installed? ({stderr})"
            )
        return False, stderr or f"{action} failed (exit {result.returncode})"
    except subprocess.TimeoutExpired:
        return False, "systemctl timed out."
    except OSError as e:
        return False, str(e)


def get_log_namespace(unit: str) -> str:
    """Return the journal namespace (LogNamespace=) *unit* runs in, or "".

    Units running with systemd's LogNamespace= directive log to a dedicated
    journal namespace instead of the default journal, and journalctl only
    finds their entries when pointed at it with --namespace. An empty string
    means the unit logs to the default journal (also the case on systemd
    < 245, where the property does not exist).
    """
    try:
        result = subprocess.run(
            ["systemctl", "show", unit, "--property=LogNamespace", "--value"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip()


def get_journal_log(unit: str = "raspisump.service", lines: int = 20) -> list:
    """Return the last *lines* journal entries for *unit* as a list of strings.

    Reads from the unit's journal namespace when it has one, so entries are
    found whether or not the unit runs with LogNamespace=. Returns an empty
    list if journalctl is unavailable.
    """
    cmd = ["journalctl", "-u", unit, "-n", str(lines),
           "--no-pager", "--output=short"]
    namespace = get_log_namespace(unit)
    if namespace:
        cmd.insert(1, "--namespace=" + namespace)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.splitlines()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def get_logfile_contents(tail: int = 100) -> list:
    """Return a list of (filename, lines) for each file in the log directory.

    Each entry is (basename, list-of-strings). Returns at most *tail* lines per file.
    """
    result = []
    try:
        paths = sorted(glob.glob(os.path.join(_LOG_DIR, "*")))
    except OSError:
        return result
    for path in paths:
        if not os.path.isfile(path):
            continue
        try:
            with open(path) as f:
                lines = f.readlines()
            result.append((os.path.basename(path), lines[-tail:]))
        except OSError:
            result.append((os.path.basename(path), ["(unable to read)"]))
    return result


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
