import datetime
import os
import sqlite3
import tempfile
from unittest import TestCase
from unittest.mock import MagicMock, patch

from raspisump import todaychart


def _make_db():
    """Create a temp database with one reading for today and one for yesterday."""
    f = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = f.name
    f.close()
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE readings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          TEXT NOT NULL,
            water_depth REAL NOT NULL,
            unit        TEXT NOT NULL
        )
        """
    )
    today = datetime.date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    conn.execute(
        "INSERT INTO readings (ts, water_depth, unit) VALUES (?, ?, ?)",
        (f"{today} 10:00:00", 10.5, "cm"),
    )
    conn.execute(
        "INSERT INTO readings (ts, water_depth, unit) VALUES (?, ?, ?)",
        (f"{yesterday} 10:00:00", 8.0, "cm"),
    )
    conn.commit()
    conn.close()
    return db_path


class TestTodayChart(TestCase):
    def test_graph_filters_to_today(self):
        """graph() passes only today's readings to plt.plot."""
        db_path = _make_db()
        try:
            mock_configs = {"unit": "metric", "line_color": "0000FF"}
            with (
                patch("raspisump.todaychart.DB_PATH", db_path),
                patch("raspisump.todaychart.configs", mock_configs),
                patch("raspisump.todaychart.plt") as mock_plt,
            ):
                mock_plt.figure.return_value = MagicMock()
                mock_plt.gca.return_value = MagicMock()
                todaychart.graph("/tmp/test_chart.png")

            call_args = mock_plt.plot.call_args[0]
            self.assertEqual(len(call_args[0]), 1)
            self.assertAlmostEqual(call_args[1][0], 10.5)
        finally:
            os.unlink(db_path)

    def test_graph_saves_to_filename(self):
        """graph() saves the chart to the given filename."""
        db_path = _make_db()
        try:
            mock_configs = {"unit": "metric", "line_color": "0000FF"}
            with (
                patch("raspisump.todaychart.DB_PATH", db_path),
                patch("raspisump.todaychart.configs", mock_configs),
                patch("raspisump.todaychart.plt") as mock_plt,
            ):
                mock_plt.figure.return_value = MagicMock()
                mock_plt.gca.return_value = MagicMock()
                todaychart.graph("/tmp/test_chart.png")

            mock_plt.savefig.assert_called_once_with(
                "/tmp/test_chart.png", transparent=True, dpi=72
            )
        finally:
            os.unlink(db_path)
