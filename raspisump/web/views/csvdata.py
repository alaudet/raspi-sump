"""Admin CSV import / export combined view."""

import io
import os
import tempfile
import zipfile
from collections import defaultdict

from flask import Blueprint, Response, render_template, request, send_file

from raspisump import log
from raspisump.web.auth import login_required

bp = Blueprint("csvdata", __name__)

_UNIT_LABELS = {"metric": "cm", "imperial": "inches"}


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

def _group_by_date(rows):
    by_date = defaultdict(list)
    for ts, depth, unit in rows:
        by_date[ts[:10]].append((ts[11:], depth))
    return dict(sorted(by_date.items()))


def _make_csv_content(entries):
    return "".join(f"{t},{d:g}\n" for t, d in entries)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@bp.route("/admin/csv", methods=["GET"])
@login_required
def index():
    return render_template("admin/csv.html", import_result=None, export_error=None)


@bp.route("/admin/csv", methods=["POST"])
@login_required
def do_action():
    action = request.form.get("action")
    if action == "import":
        return _handle_import()
    if action == "export":
        return _handle_export()
    return render_template("admin/csv.html", import_result=None,
                           export_error="Unknown action.")


def _handle_import():
    unit = request.form.get("unit", "metric")
    unit_label = _UNIT_LABELS.get(unit, "cm")
    files = request.files.getlist("csvfiles")

    if not files or all(f.filename == "" for f in files):
        return render_template("admin/csv.html",
                               import_result={"error": "No files selected."},
                               export_error=None)

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
            result = {"inserted": inserted, "skipped": skipped,
                      "errors": errors, "unit_label": unit_label}
        except ValueError as e:
            result = {"error": str(e)}
        except OSError as e:
            result = {"error": f"File error: {e}"}

    return render_template("admin/csv.html", import_result=result, export_error=None)


def _handle_export():
    start_date = request.form.get("start_date", "").strip()
    end_date = request.form.get("end_date", "").strip() or None
    start_time = request.form.get("start_time", "").strip() or None
    end_time = request.form.get("end_time", "").strip() or None

    if not start_date:
        return render_template("admin/csv.html", import_result=None,
                               export_error="Start date is required.")

    single_day = end_date is None or end_date == start_date
    if end_date is None:
        end_date = start_date
    if not single_day:
        start_time = end_time = None

    rows = log.query_readings_range(start_date, end_date, start_time, end_time)
    if not rows:
        return render_template("admin/csv.html", import_result=None,
                               export_error="No readings found for the selected range.")

    by_date = _group_by_date(rows)

    if len(by_date) == 1:
        date_str = next(iter(by_date))
        csv_content = _make_csv_content(by_date[date_str])
        nodash = date_str.replace("-", "")
        return Response(
            csv_content,
            mimetype="text/csv",
            headers={"Content-Disposition":
                     f"attachment; filename=waterlevel-{nodash}.csv"},
        )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for date_str, entries in by_date.items():
            nodash = date_str.replace("-", "")
            zf.writestr(f"waterlevel-{nodash}.csv", _make_csv_content(entries))
    buf.seek(0)
    zip_name = f"raspisump-export-{start_date}-to-{end_date}.zip"
    return send_file(buf, mimetype="application/zip",
                     as_attachment=True, download_name=zip_name)
