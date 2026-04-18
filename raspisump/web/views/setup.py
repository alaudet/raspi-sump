"""First-run setup wizard."""

import configparser
import subprocess

from flask import Blueprint, abort, render_template, request

from raspisump.web.auth import hash_password
from raspisump.web.config_helpers import (
    FIELD_SCHEMA,
    load_current_values,
    validate_config_form,
    write_config_values,
)
from raspisump.web.credentials_helpers import (
    CRED_PATH,
    CRED_SCHEMA,
    load_credentials,
    write_credentials,
)

bp = Blueprint("setup", __name__)


def is_unconfigured() -> bool:
    """Return True if admin_password is still the default 'admin' (reads conf fresh)."""
    cp = configparser.RawConfigParser()
    cp.read(CRED_PATH)
    return cp.get("web", "admin_password", fallback="admin") == "admin"


def _form_values_from_post(form_data):
    """Re-build current_conf / current_creds from submitted POST data for re-render."""
    current_conf = {}
    for section, _label, fields in FIELD_SCHEMA:
        current_conf[section] = {}
        for key, *_ in fields:
            current_conf[section][key] = form_data.get(f"{section}__{key}", "")
    current_creds = {}
    for section, _label, fields in CRED_SCHEMA:
        current_creds[section] = {}
        for key, *_ in fields:
            current_creds[section][key] = form_data.get(f"{section}__{key}", "")
    return current_conf, current_creds


def _validate_wizard_form(form_data):
    """Validate the combined wizard form.

    Returns (conf_changes, cred_changes, errors).
    """
    conf_changes, errors = validate_config_form(form_data)

    cred_changes = {}

    # Admin password — required, must not be 'admin'
    new_password = form_data.get("web__admin_password", "").strip()
    if not new_password:
        errors.append("Admin Password must not be empty.")
    elif new_password == "admin":
        errors.append("Admin Password must not be 'admin'. Please choose a secure password.")
    else:
        cred_changes[("web", "admin_password")] = hash_password(new_password)

    # Optional credentials fields (email / Mastodon)
    for section, _label, fields in CRED_SCHEMA:
        if section == "web":
            continue
        for key, _label2, _widget, _help in fields:
            raw = form_data.get(f"{section}__{key}", "").strip()
            cred_changes[(section, key)] = raw

    return conf_changes, cred_changes, errors


@bp.route("/setup", methods=["GET"])
def setup_get():
    if not is_unconfigured():
        abort(404)
    try:
        current_conf = load_current_values()
    except OSError:
        current_conf = {}
    try:
        current_creds = load_credentials()
    except OSError:
        current_creds = {}
    # Don't pre-fill the password field — leave blank for user to enter
    if "web" in current_creds:
        current_creds["web"]["admin_password"] = ""
    return render_template(
        "setup.html",
        conf_schema=FIELD_SCHEMA,
        cred_schema=CRED_SCHEMA,
        current_conf=current_conf,
        current_creds=current_creds,
        errors=None,
    )


@bp.route("/setup", methods=["POST"])
def setup_post():
    if not is_unconfigured():
        abort(404)
    conf_changes, cred_changes, errors = _validate_wizard_form(request.form)

    if errors:
        current_conf, current_creds = _form_values_from_post(request.form)
        # Don't echo back the submitted password
        if "web" in current_creds:
            current_creds["web"]["admin_password"] = ""
        return render_template(
            "setup.html",
            conf_schema=FIELD_SCHEMA,
            cred_schema=CRED_SCHEMA,
            current_conf=current_conf,
            current_creds=current_creds,
            errors=errors,
        )

    try:
        write_config_values(conf_changes)
        write_credentials(cred_changes)
    except OSError as e:
        return render_template(
            "setup.html",
            conf_schema=FIELD_SCHEMA,
            cred_schema=CRED_SCHEMA,
            current_conf={},
            current_creds={},
            errors=[f"Could not write configuration: {e}"],
        )

    # Start raspisump.service now that config is in place
    subprocess.run(
        ["sudo", "systemctl", "start", "raspisump.service"],
        capture_output=True,
    )

    # Delayed restart of rsumpweb so this HTTP response is delivered first
    subprocess.Popen(
        ["bash", "-c", "sleep 2 && sudo systemctl restart rsumpweb.service"],
    )

    return render_template("admin/restarting.html", redirect_to="/")
