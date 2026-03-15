"""Support page — generate support file and run alert test."""

import io
import os
from contextlib import redirect_stderr, redirect_stdout

from flask import Blueprint, render_template, request, send_file

from raspisump.web.auth import login_required

bp = Blueprint("support", __name__)


def _run_alerttest():
    """Run alert test notifications and return (success, output)."""
    buf = io.StringIO()
    try:
        from raspisump import emailtest
        with redirect_stdout(buf), redirect_stderr(buf):
            emailtest.test_notifications()
        output = buf.getvalue().strip()
        if not output:
            return False, "No alert type configured or nothing was sent."
        return "successfully" in output.lower(), output
    except Exception as e:
        return False, str(e)


@bp.route("/admin/support", methods=["GET", "POST"])
@login_required
def index():
    alert_result = None
    alert_success = None
    error = None

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "download":
            try:
                from raspisump.cli import rsumpsupport
                file_path = rsumpsupport()
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=os.path.basename(file_path),
                )
            except Exception as e:
                error = str(e)

        elif action == "alerttest":
            alert_success, alert_result = _run_alerttest()

    return render_template(
        "admin/support.html",
        alert_result=alert_result,
        alert_success=alert_success,
        error=error,
    )
