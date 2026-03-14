"""Admin configuration editor view."""

from flask import Blueprint, Response, render_template, request

from raspisump.web.auth import login_required
from raspisump.web.config_helpers import (
    FIELD_SCHEMA,
    _CONF_PATH,
    load_current_values,
    validate_config_form,
    write_config_values,
)

bp = Blueprint("config", __name__)


def _form_values_from_post(form_data) -> dict:
    """Return nested dict of submitted form values for re-rendering on error."""
    result = {}
    for section, _label, fields in FIELD_SCHEMA:
        result[section] = {}
        for key, _label2, _widget, _opts, _help in fields:
            result[section][key] = form_data.get(f"{section}__{key}", "")
    return result


@bp.route("/admin/config", methods=["GET"])
@login_required
def index():
    try:
        current = load_current_values()
    except OSError:
        current = {}
    return render_template("admin/config.html", schema=FIELD_SCHEMA,
                           current=current, errors=None, success=False)


@bp.route("/admin/config", methods=["POST"])
@login_required
def save():
    changes, errors = validate_config_form(request.form)
    if errors:
        current = _form_values_from_post(request.form)
        return render_template("admin/config.html", schema=FIELD_SCHEMA,
                               current=current, errors=errors, success=False)
    try:
        write_config_values(changes)
        current = load_current_values()
    except PermissionError:
        current = _form_values_from_post(request.form)
        return render_template("admin/config.html", schema=FIELD_SCHEMA,
                               current=current,
                               errors=["Permission denied writing to raspisump.conf. "
                                       "Check that the file is owned by the raspisump user."],
                               success=False)
    except OSError as e:
        current = _form_values_from_post(request.form)
        return render_template("admin/config.html", schema=FIELD_SCHEMA,
                               current=current, errors=[f"Error writing config: {e}"],
                               success=False)
    return render_template("admin/config.html", schema=FIELD_SCHEMA,
                           current=current, errors=None, success=True)


@bp.route("/admin/config/raw")
@login_required
def raw():
    try:
        with open(_CONF_PATH, "r") as f:
            content = f.read()
        return Response(content, mimetype="text/plain")
    except OSError as e:
        return f"Error reading config file: {e}", 500
