"""About page view."""

from flask import Blueprint, render_template, current_app

from raspisump import RELEASE_DATE

bp = Blueprint("about", __name__)


@bp.route("/about/")
def about():
    return render_template(
        "about.html",
        release_date=RELEASE_DATE,
    )
