"""Home page view — today's chart."""

import os
import time

from flask import Blueprint, render_template

bp = Blueprint("home", __name__)

# Patchable in tests
CHARTS_DIR = "/var/lib/raspi-sump/charts"


@bp.route("/")
def index():
    chart_path = os.path.join(CHARTS_DIR, "today.png")
    if os.path.exists(chart_path):
        mtime = int(os.path.getmtime(chart_path))
        chart_url = f"/charts/today.png?t={mtime}"
    else:
        chart_url = None

    today = time.strftime("%Y-%m-%d")
    return render_template("home.html", chart_url=chart_url, today=today)
