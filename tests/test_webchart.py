import os
import tempfile
from unittest import TestCase
from unittest.mock import patch

from raspisump import webchart


class TestWebChart(TestCase):
    def test_create_folders(self):
        """create_folders() creates the year/month directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("raspisump.webchart.CHARTS_DIR", tmpdir):
                webchart.create_folders("2026", "03")
            self.assertTrue(os.path.isdir(f"{tmpdir}/2026/03"))

    def test_copy_chart(self):
        """copy_chart() copies today.png to the year/month/day path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            src = os.path.join(tmpdir, "today.png")
            dest_dir = os.path.join(tmpdir, "2026", "03")
            os.makedirs(dest_dir)
            with open(src, "w") as f:
                f.write("fake png")
            with patch("raspisump.webchart.CHARTS_DIR", tmpdir):
                webchart.copy_chart("2026", "03", "11")
            self.assertTrue(os.path.exists(f"{tmpdir}/2026/03/11.png"))

    def test_create_chart_calls_graph(self):
        """create_chart() calls todaychart.graph with the correct output path."""
        with (
            patch("raspisump.webchart.todaychart.graph") as mock_graph,
            patch("raspisump.webchart.CHARTS_DIR", "/fake/charts"),
        ):
            webchart.create_chart()
        mock_graph.assert_called_once_with("/fake/charts/today.png")
