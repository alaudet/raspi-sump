"""Historical readings view."""

from flask import Blueprint, render_template, request

from raspisump.web.stats import day_stats

bp = Blueprint("history", __name__)


@bp.route("/history/")
def index():
    date = request.args.get("date")
    stats = None
    error = None

    if date:
        stats = day_stats(date)
        if stats is None:
            error = f"No readings found for {date}."

    return render_template(
        "history.html",
        date=date,
        stats=stats,
        error=error,
    )
