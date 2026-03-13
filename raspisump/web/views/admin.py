"""Admin interface views."""

from flask import Blueprint, redirect, render_template, request, session, url_for

from raspisump.web.auth import check_password, login_required
from raspisump.web.system import all_service_statuses, get_raspisump_config

bp = Blueprint("admin", __name__)


@bp.route("/admin/")
@login_required
def index():
    services = all_service_statuses()
    config = get_raspisump_config()
    return render_template("admin/index.html", services=services, config=config)


@bp.route("/admin/login", methods=["GET"])
def login_get():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.index"))
    return render_template("admin/login.html", error=None)


@bp.route("/admin/login", methods=["POST"])
def login_post():
    password = request.form.get("password", "")
    if check_password(password):
        session["admin_logged_in"] = True
        return redirect(url_for("admin.index"))
    return render_template("admin/login.html", error="Invalid password."), 401


@bp.route("/admin/logout")
@login_required
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("home.index"))
