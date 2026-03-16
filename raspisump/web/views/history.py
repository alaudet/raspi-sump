"""Historical readings view."""

from datetime import date as dt_date, datetime, timedelta

from flask import Blueprint, render_template, request

from raspisump.web.stats import day_stats

bp = Blueprint("history", __name__)


@bp.route("/history/")
def index():
    date     = request.args.get("date")
    days_str = request.args.get("days")
    start    = request.args.get("start")
    end      = request.args.get("end")

    mode   = None
    stats  = None
    error  = None
    dates  = []
    days   = None
    cycles = None

    if date:
        mode  = "day"
        stats = day_stats(date)
        if stats is None:
            error = f"No readings found for {date}."
        else:
            try:
                from raspisump.config_values import config, cycle_detection_enabled
                if cycle_detection_enabled():
                    from raspisump.log import detect_cycles, query_readings
                    alert_when = config.get("pit", "alert_when", fallback="high")
                    readings = query_readings(date=date)
                    cycles = len(detect_cycles(readings, alert_when))
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning("cycle detection error: %s", e)

    elif days_str:
        mode = "multiday"
        try:
            days = max(1, min(30, int(days_str)))
        except ValueError:
            days = 7
        today = dt_date.today()
        dates = [
            (today - timedelta(days=i)).isoformat()
            for i in range(days - 1, -1, -1)
        ]

    elif start and end:
        mode = "range"
        try:
            dt_start = datetime.strptime(start, "%Y-%m-%dT%H:%M")
            dt_end   = datetime.strptime(end,   "%Y-%m-%dT%H:%M")
            if dt_end <= dt_start:
                error = "End must be after start."
                mode  = None
            elif (dt_end - dt_start).days > 30:
                error = "Range cannot exceed 30 days."
                mode  = None
        except ValueError:
            error = "Invalid date/time format."
            mode  = None

    return render_template(
        "history.html",
        mode=mode,
        date=date,
        stats=stats,
        cycles=cycles,
        error=error,
        dates=dates,
        days=days,
        start=start,
        end=end,
    )
