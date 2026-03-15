"""JSON API — readings data for uPlot charts."""

import configparser
import time

from flask import Blueprint, jsonify, request

from raspisump.log import query_readings, query_readings_range

bp = Blueprint("api", __name__)

_RASPISUMP_CONF = "/etc/raspi-sump/raspisump.conf"


def _critical_level():
    """Return critical_water_level float from raspisump.conf, or None."""
    cp = configparser.RawConfigParser()
    cp.read(_RASPISUMP_CONF)
    try:
        return float(cp.get("pit", "critical_water_level"))
    except (configparser.Error, ValueError):
        return None


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
    unit = rows[0][2]

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
        "unit":  rows[0][2],
        "critical_level": _critical_level(),
        "data": [timestamps, depths],
    })
