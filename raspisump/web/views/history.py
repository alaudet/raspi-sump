"""Historical readings view."""

from flask import Blueprint, render_template, request

from raspisump.web.charts import chart_url_for_date
from raspisump.web.stats import day_stats

bp = Blueprint("history", __name__)


@bp.route("/history/")
def index():
    date = request.args.get("date")
    chart_url = None
    stats = None
    error = None

    if date:
        stats = day_stats(date)
        if stats is None:
            error = f"No readings found for {date}."
        else:
            chart_url = chart_url_for_date(date)

    return render_template(
        "history.html",
        date=date,
        chart_url=chart_url,
        stats=stats,
        error=error,
    )
