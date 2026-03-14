"""Admin Security page — edit credentials.conf."""

from flask import Blueprint, render_template, request

from raspisump.web.auth import login_required
from raspisump.web.credentials_helpers import (
    CRED_SCHEMA,
    load_credentials,
    validate_credentials_form,
    write_credentials,
)

bp = Blueprint("security", __name__)


def _form_values_from_post(form_data) -> dict:
    """Return nested dict of submitted values for re-rendering on error."""
    result = {}
    for section, _label, fields in CRED_SCHEMA:
        result[section] = {}
        for key, _label2, _widget, _help in fields:
            result[section][key] = form_data.get(f"{section}__{key}", "")
    return result


@bp.route("/admin/security", methods=["GET"])
@login_required
def index():
    try:
        current = load_credentials()
    except OSError:
        current = {}
    return render_template("admin/security.html", schema=CRED_SCHEMA,
                           current=current, errors=None, success=False)


@bp.route("/admin/security", methods=["POST"])
@login_required
def save():
    changes, errors = validate_credentials_form(request.form)
    if errors:
        current = _form_values_from_post(request.form)
        return render_template("admin/security.html", schema=CRED_SCHEMA,
                               current=current, errors=errors, success=False)
    try:
        write_credentials(changes)
        current = load_credentials()
    except PermissionError:
        current = _form_values_from_post(request.form)
        return render_template("admin/security.html", schema=CRED_SCHEMA,
                               current=current,
                               errors=["Permission denied writing credentials.conf. "
                                       "Check that the file is group-writable by raspisump."],
                               success=False)
    except OSError as e:
        current = _form_values_from_post(request.form)
        return render_template("admin/security.html", schema=CRED_SCHEMA,
                               current=current,
                               errors=[f"Error writing credentials: {e}"],
                               success=False)
    return render_template("admin/security.html", schema=CRED_SCHEMA,
                           current=current, errors=None, success=True)
