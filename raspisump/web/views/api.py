"""JSON API — readings data for uPlot charts and the Home Assistant integration."""

import configparser
import logging
import time
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

# _UNIT_LABELS is imported rather than duplicated: log.py owns the labels that
# actually get written to the readings database, and /api/status must report the
# same strings whether it learns the unit from a reading or from the config file.
from raspisump.log import _UNIT_LABELS, query_readings, query_readings_range

bp = Blueprint("api", __name__)

_RASPISUMP_CONF = "/etc/raspi-sump/raspisump.conf"

# Bumped only on a breaking change to the /api/status payload.  Clients (the
# Home Assistant integration) refuse to talk to a version they don't know.
STATUS_API_VERSION = 1


def _pit_config():
    """Return the [pit] settings needed by API clients, as a dict of Nones on failure.

    Deliberately re-reads raspisump.conf on every call rather than using
    raspisump.config_values, which parses the file once at import time: a config
    change made through the web UI would otherwise not be visible until
    rsumpweb restarts.
    """
    values = {
        "critical_level": None,
        "pit_depth": None,
        "alert_when": None,
        "reading_interval": None,
        "unit": None,
    }
    cp = configparser.RawConfigParser()
    try:
        cp.read(_RASPISUMP_CONF)
    except configparser.Error:
        return values

    for key, option, cast in (
        ("critical_level", "critical_water_level", float),
        ("pit_depth", "pit_depth", float),
        ("alert_when", "alert_when", str),
        ("reading_interval", "reading_interval", int),
        ("unit", "unit", _UNIT_LABELS.get),
    ):
        try:
            values[key] = cast(cp.get("pit", option))
        except (configparser.Error, ValueError):
            pass
    return values


def _critical_level():
    """Return critical_water_level float from raspisump.conf, or None."""
    return _pit_config()["critical_level"]


@bp.route("/api/readings")
def readings():
    date = request.args.get("date")
    if not date:
        date = time.strftime("%Y-%m-%d")

    rows = query_readings(date, last=None)

    if not rows:
        return jsonify({
            "date": date,
            "unit": None,
            "critical_level": None,
            "data": [[], []],
        })

    timestamps = []
    depths = []
    unit = rows[-1][2]

    for ts_str, depth, _unit in rows:
        # Parse "YYYY-MM-DD HH:MM:SS" → Unix seconds (local time)
        t = time.mktime(time.strptime(ts_str, "%Y-%m-%d %H:%M:%S"))
        timestamps.append(int(t))
        depths.append(depth)

    return jsonify({
        "date": date,
        "unit": unit,
        "critical_level": _critical_level(),
        "data": [timestamps, depths],
    })


@bp.route("/api/readings/range")
def readings_range():
    start = request.args.get("start", "")  # YYYY-MM-DDTHH:MM
    end   = request.args.get("end",   "")

    try:
        start_date, start_time = start.split("T")
        end_date,   end_time   = end.split("T")
    except (ValueError, AttributeError):
        return jsonify({"error": "start and end required (YYYY-MM-DDTHH:MM)"}), 400

    rows = query_readings_range(start_date, end_date, start_time, end_time)

    if not rows:
        return jsonify({
            "start": start, "end": end,
            "unit": None, "critical_level": None,
            "data": [[], []],
        })

    timestamps = [int(time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S"))) for ts, _, _ in rows]
    depths     = [d for _, d, _ in rows]

    return jsonify({
        "start": start,
        "end":   end,
        "unit":  rows[-1][2],
        "critical_level": _critical_level(),
        "data": [timestamps, depths],
    })


def _isoformat(ts_str):
    """Convert a "YYYY-MM-DD HH:MM:SS" reading timestamp to tz-aware ISO-8601.

    The chart endpoints emit naive local-time Unix seconds, which uPlot is happy
    with.  Home Assistant rejects naive datetimes for timestamp sensors, so the
    local timezone offset is attached here.
    """
    try:
        naive = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        return None
    return naive.astimezone().isoformat()


def _cycles_today():
    """Return today's detected pump cycle count, or None if disabled/unavailable."""
    try:
        from raspisump.config_values import config, cycle_detection_enabled
        if not cycle_detection_enabled():
            return None
        from raspisump.log import detect_cycles
        alert_when = config.get("pit", "alert_when", fallback="high")
        return len(detect_cycles(query_readings(), alert_when))
    except Exception as e:
        logging.getLogger(__name__).warning("cycle detection error: %s", e)
        return None


def _service_active():
    """Return True/False for raspisump.service, or None if systemd is unavailable."""
    try:
        from raspisump.web.system import get_service_status
        props = get_service_status("raspisump.service")
    except Exception as e:
        logging.getLogger(__name__).warning("service status error: %s", e)
        return None
    if not props:
        return None
    return props.get("ActiveState") == "active"


@bp.route("/api/status")
def status():
    """Current state summary — one small payload per poll.

    Built for the Home Assistant integration, but useful to any client that
    wants the latest reading without downloading a whole day of readings.
    Optional pieces degrade to null rather than failing the request.
    """
    try:
        from raspisump.web.stats import day_stats
        stats = day_stats()
    except Exception as e:
        logging.getLogger(__name__).warning("day stats error: %s", e)
        stats = None

    pit = _pit_config()

    return jsonify({
        "api_version": STATUS_API_VERSION,
        "version": current_app.config.get("VERSION"),
        "level": stats["last"] if stats else None,
        # Prefer the label recorded alongside the readings; fall back to the
        # configured unit so a freshly installed pit still describes itself.
        "unit": (stats["unit"] if stats else None) or pit["unit"],
        "last_ts": _isoformat(stats["last_ts"]) if stats else None,
        "critical_level": pit["critical_level"],
        "pit_depth": pit["pit_depth"],
        "alert_when": pit["alert_when"],
        "reading_interval": pit["reading_interval"],
        "day": {
            "min": stats["min"] if stats else None,
            "max": stats["max"] if stats else None,
            "count": stats["count"] if stats else 0,
        },
        "cycles_today": _cycles_today(),
        "service_active": _service_active(),
    })
