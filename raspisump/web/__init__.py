"""Flask web application for raspi-sump."""

import importlib.metadata
import os
import secrets

from flask import Flask


def create_app():
    """Create and configure the Flask application."""
    # Templates and static files live in the raspisump package root (one level up from web/)
    _pkg_root = os.path.dirname(os.path.dirname(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(_pkg_root, "templates"),
        static_folder=os.path.join(_pkg_root, "static"),
        static_url_path="/static",
    )

    app.secret_key = secrets.token_hex(32)

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
    app.register_blueprint(home_bp)
    app.register_blueprint(history_bp)
    app.register_blueprint(admin_bp)

    return app


def serve():
    """Entry point: start the Flask app via waitress on a Unix socket."""
    app = create_app()
    try:
        import waitress
        waitress.serve(app, unix_socket="/run/raspi-sump/flask.sock",
                       unix_socket_perms="660")
    except ImportError:
        # Fallback if waitress is not installed
        app.run(host="127.0.0.1", port=5000, use_reloader=False, threaded=True)
