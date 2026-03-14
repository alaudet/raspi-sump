"""Home page view — today's chart."""

import time

from flask import Blueprint, render_template

from raspisump.web.stats import day_stats

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    today = time.strftime("%Y-%m-%d")
    stats = day_stats()
    return render_template("home.html", today=today, stats=stats)
