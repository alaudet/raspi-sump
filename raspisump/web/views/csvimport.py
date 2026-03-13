"""Admin CSV import view."""

import os
import tempfile

from flask import Blueprint, render_template, request

from raspisump import log
from raspisump.web.auth import login_required

bp = Blueprint("csvimport", __name__)

_UNIT_LABELS = {"metric": "cm", "imperial": "inches"}


@bp.route("/admin/import", methods=["GET"])
@login_required
def index():
    return render_template("admin/import.html", result=None)


@bp.route("/admin/import", methods=["POST"])
@login_required
def do_import():
    unit = request.form.get("unit", "metric")
    unit_label = _UNIT_LABELS.get(unit, "cm")
    files = request.files.getlist("csvfiles")

    if not files or all(f.filename == "" for f in files):
        return render_template(
            "admin/import.html",
            result={"error": "No files selected."},
        )

    result = None
    with tempfile.TemporaryDirectory() as tmpdir:
        paths = []
        for f in files:
            if f.filename == "":
                continue
            dest = os.path.join(tmpdir, os.path.basename(f.filename))
            f.save(dest)
            paths.append(dest)

        try:
            inserted, skipped, errors = log.import_csv_files(paths, unit_label)
            result = {
                "inserted": inserted,
                "skipped": skipped,
                "errors": errors,
                "unit_label": unit_label,
            }
        except ValueError as e:
            result = {"error": str(e)}
        except OSError as e:
            result = {"error": f"File error: {e}"}

    return render_template("admin/import.html", result=result)
