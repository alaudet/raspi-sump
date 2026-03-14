"""Admin interface views."""

import subprocess

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from raspisump.web.auth import check_password, login_required
from raspisump.web.system import all_service_statuses, control_service, get_journal_log

bp = Blueprint("admin", __name__)


@bp.route("/admin/")
@login_required
def index():
    services = all_service_statuses()
    journal_rsump = get_journal_log("raspisump.service", lines=20)
    journal_web = get_journal_log("rsumpweb.service", lines=20)
    return render_template("admin/index.html", services=services,
                           journal_rsump=journal_rsump, journal_web=journal_web)


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


@bp.route("/admin/service", methods=["POST"])
@login_required
def service_action():
    unit = request.form.get("unit", "")
    action = request.form.get("action", "")

    # Restarting rsumpweb kills the process serving this request.
    # Schedule the restart after a short delay so the response goes out first,
    # then show a reconnecting page that auto-reloads once the service is back.
    if unit == "rsumpweb.service" and action == "restart":
        subprocess.Popen(
            ["sh", "-c", "sleep 3 && sudo /usr/bin/systemctl restart rsumpweb.service"],
            close_fds=True,
            start_new_session=True,
        )
        return render_template("admin/restarting.html", redirect_to=url_for("admin.index"))

    success, message = control_service(unit, action)
    flash(message, "success" if success else "error")
    next_url = request.form.get("next", "")
    if next_url and next_url.startswith("/admin/"):
        return redirect(next_url)
    return redirect(url_for("admin.index"))


@bp.route("/admin/logout")
@login_required
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("home.index"))
