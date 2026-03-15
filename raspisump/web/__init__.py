"""Flask web application for raspi-sump."""

import importlib.metadata
import os
import secrets
from datetime import timedelta

_SECRET_KEY_PATH = "/etc/raspi-sump/secret_key"


def _load_secret_key():
    """Return a stable secret key, falling back to a random one in dev."""
    try:
        with open(_SECRET_KEY_PATH) as f:
            key = f.read().strip()
        if key:
            return key
    except OSError:
        pass
    return secrets.token_hex(32)


def create_app():
    """Create and configure the Flask application."""
    # Templates and static files live in the raspisump package root (one level up from web/)
    _pkg_root = os.path.dirname(os.path.dirname(__file__))

    from flask import Flask
    app = Flask(
        __name__,
        template_folder=os.path.join(_pkg_root, "templates"),
        static_folder=os.path.join(_pkg_root, "static"),
        static_url_path="/static",
    )

    app.secret_key = _load_secret_key()
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

    try:
        app.config["VERSION"] = importlib.metadata.version("raspisump")
    except importlib.metadata.PackageNotFoundError:
        app.config["VERSION"] = "dev"

    @app.context_processor
    def inject_globals():
        return {"version": app.config["VERSION"]}

    from raspisump.web.views.home import bp as home_bp
    from raspisump.web.views.history import bp as history_bp
    from raspisump.web.views.admin import bp as admin_bp
    from raspisump.web.views.backup import bp as backup_bp
    from raspisump.web.views.csvdata import bp as csvdata_bp
    from raspisump.web.views.config import bp as config_bp
    from raspisump.web.views.security import bp as security_bp
    from raspisump.web.views.support import bp as support_bp
    from raspisump.web.views.api import bp as api_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(csvdata_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(security_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(api_bp)

    return app


def serve():
    """Entry point: start the Flask app via waitress on a Unix socket."""
    app = create_app()
    try:
        import waitress
        waitress.serve(app, unix_socket="/run/raspi-sump/flask.sock",
                       unix_socket_perms="660", threads=8)
    except ImportError:
        # Fallback if waitress is not installed
        app.run(host="127.0.0.1", port=5000, use_reloader=False, threaded=True)
