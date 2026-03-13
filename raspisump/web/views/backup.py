"""Admin backup / export view."""

import io
import time
import zipfile

from flask import Blueprint, send_file

from raspisump.web.auth import login_required

bp = Blueprint("backup", __name__)

_DB_PATH = "/var/lib/raspi-sump/raspisump.db"
_CONF_PATH = "/etc/raspi-sump/raspisump.conf"

_EXPORT_FILES = [
    (_DB_PATH, "raspisump.db"),
    (_CONF_PATH, "raspisump.conf"),
]


def build_backup_zip():
    """Return a BytesIO containing a zip of the db and config."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for src_path, arc_name in _EXPORT_FILES:
            try:
                zf.write(src_path, arc_name)
            except OSError:
                pass  # file missing or unreadable — skip silently
    buf.seek(0)
    return buf


@bp.route("/admin/backup/download")
@login_required
def download():
    buf = build_backup_zip()
    date_str = time.strftime("%Y-%m-%d")
    filename = f"raspisump-backup-{date_str}.zip"
    return send_file(
        buf,
        mimetype="application/zip",
        as_attachment=True,
        download_name=filename,
    )
