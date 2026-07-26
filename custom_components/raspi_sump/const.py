"""Constants for the Raspi-Sump integration."""

from __future__ import annotations

DOMAIN = "raspi_sump"

# Not in homeassistant.const, so defined here.
CONF_PATH = "path"

DEFAULT_PORT = 80
DEFAULT_SSL_PORT = 443
DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 10
MAX_SCAN_INTERVAL = 3600

# The only /api/status payload shape this integration knows how to read.
SUPPORTED_API_VERSION = 1

# Where the Lovelace card and its uPlot bundle are served from.
STATIC_URL = "/raspi_sump_static"
CARD_FILENAME = "raspi-sump-card.js"

WS_TYPE_READINGS = f"{DOMAIN}/readings"

# raspi-sump stores these labels alongside every reading (see raspisump/log.py).
UNIT_CM = "cm"
UNIT_INCHES = "inches"
