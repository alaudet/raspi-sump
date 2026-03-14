"""JSON API — readings data for uPlot charts."""

import configparser
import time

from flask import Blueprint, jsonify, request

from raspisump.log import query_readings

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
