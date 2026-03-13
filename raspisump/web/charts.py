"""On-demand historical chart generation for the Flask web interface.

Today's chart is handled by the rsumpwebchart timer and never regenerated here.
Past dates are generated once and cached permanently (file presence check).
"""

import os

from raspisump.webchart import CHARTS_DIR


def chart_url_for_date(date_str):
    """Return the nginx-relative URL for a date's chart, generating it if needed.

    Returns None if no readings exist for that date.
    """
    from raspisump.web.stats import day_stats
    if day_stats(date_str) is None:
        return None

    year = date_str[:4]
    month = date_str[5:7]
    day_compact = date_str.replace("-", "")
    chart_path = os.path.join(CHARTS_DIR, year, month, f"{day_compact}.png")

    if not os.path.exists(chart_path):
        os.makedirs(os.path.dirname(chart_path), mode=0o775, exist_ok=True)
        from raspisump import todaychart
        todaychart.graph(chart_path, date=date_str)

    mtime = int(os.path.getmtime(chart_path))
    return f"/charts/{year}/{month}/{day_compact}.png?t={mtime}"
