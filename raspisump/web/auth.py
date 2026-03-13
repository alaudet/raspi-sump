"""Admin authentication helpers."""

from functools import wraps

from flask import redirect, session, url_for


def get_admin_password():
    """Return the admin password from credentials.conf.

    Uses a fallback of 'changeme' if the [web] section is missing
    (e.g. on an install that hasn't been upgraded yet).
    """
    from raspisump.config_values import config
    return config.get("web", "admin_password", fallback="changeme")


def check_password(candidate):
    """Return True if candidate matches the configured admin password."""
    return candidate == get_admin_password()


def login_required(f):
    """Decorator: redirect to login page if admin session is not set."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login_get"))
        return f(*args, **kwargs)
    return decorated
