"""Home page view — today's chart."""

import time

from flask import Blueprint, render_template

from raspisump.web.stats import day_stats

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    today = time.strftime("%Y-%m-%d")
    stats = day_stats()
    cycles = None
    try:
        from raspisump.config_values import config, cycle_detection_enabled
        if cycle_detection_enabled():
            from raspisump.log import detect_cycles, query_readings
            alert_when = config.get("pit", "alert_when", fallback="high")
            readings = query_readings()
            cycles = len(detect_cycles(readings, alert_when))
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("cycle detection error: %s", e)
    return render_template("home.html", today=today, stats=stats, cycles=cycles)
