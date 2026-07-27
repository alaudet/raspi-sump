"""Tests for the web UI favicon.

The asset checks run anywhere; the serving/linking checks need Flask and
are skipped automatically when it isn't installed (as on a dev machine).
"""

import os
import unittest
import xml.dom.minidom

# raspisump/static/favicon.svg — resolved relative to the package, not cwd.
_STATIC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "raspisump", "static",
)
_FAVICON = os.path.join(_STATIC_DIR, "favicon.svg")


class TestFaviconAsset(unittest.TestCase):
    """The icon file ships in the package and is a valid SVG."""

    def test_favicon_file_exists(self):
        self.assertTrue(os.path.isfile(_FAVICON), f"missing {_FAVICON}")

    def test_favicon_is_well_formed_svg(self):
        with open(_FAVICON, "rb") as f:
            dom = xml.dom.minidom.parseString(f.read())
        self.assertEqual(dom.documentElement.tagName, "svg")


# ---------------------------------------------------------------------------
# Serving / linking (require Flask — run on Pi only)
# ---------------------------------------------------------------------------

try:
    import importlib
    importlib.import_module("flask")
    from raspisump.web import create_app
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


@unittest.skipUnless(FLASK_AVAILABLE, "Flask not installed")
class TestFaviconServing(unittest.TestCase):
    """Flask serves the icon and every page links it from <head>.

    /admin/login is used because it extends base.html and needs no database.
    """

    def setUp(self):
        app = create_app()
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_favicon_served_with_svg_content_type(self):
        response = self.client.get("/static/favicon.svg")
        self.addCleanup(response.close)  # release the file handle send_file opened
        self.assertEqual(response.status_code, 200)
        self.assertIn("image/svg+xml", response.headers.get("Content-Type", ""))

    def test_page_links_favicon(self):
        response = self.client.get("/admin/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'rel="icon"', response.data)
        self.assertIn(b"/static/favicon.svg", response.data)


if __name__ == "__main__":
    unittest.main()
