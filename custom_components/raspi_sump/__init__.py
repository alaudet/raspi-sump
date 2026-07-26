"""The Raspi-Sump integration."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    CONF_SSL,
    CONF_VERIFY_SSL,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType
from homeassistant.loader import async_get_integration

from . import websocket
from .api import RaspiSumpClient
from .const import (
    CARD_FILENAME,
    CONF_PATH,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SSL_PORT,
    DOMAIN,
    STATIC_URL,
)
from .coordinator import RaspiSumpConfigEntry, RaspiSumpCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


def build_base_url(data: dict[str, Any]) -> str:
    """Return the root URL of the raspi-sump web UI described by *data*.

    The port is omitted when it is the default for the scheme, so the device
    page links to a tidy https://sump.example.com rather than :443.
    """
    ssl = data.get(CONF_SSL, False)
    scheme = "https" if ssl else "http"
    default_port = DEFAULT_SSL_PORT if ssl else DEFAULT_PORT
    port = data.get(CONF_PORT, default_port)

    url = f"{scheme}://{data[CONF_HOST]}"
    if port != default_port:
        url = f"{url}:{port}"
    if path := (data.get(CONF_PATH) or "").strip("/"):
        url = f"{url}/{path}"
    return url


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the pieces that are shared by every config entry."""
    await _async_register_frontend(hass)
    websocket.async_setup(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: RaspiSumpConfigEntry) -> bool:
    """Set up Raspi-Sump from a config entry."""
    session = async_get_clientsession(
        hass, verify_ssl=entry.data.get(CONF_VERIFY_SSL, True)
    )
    client = RaspiSumpClient(session, build_base_url(entry.data))

    coordinator = RaspiSumpCoordinator(
        hass,
        entry,
        client,
        entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
    )
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: RaspiSumpConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry so a changed scan interval takes effect."""
    await hass.config_entries.async_reload(entry.entry_id)


def _card_fingerprint(card_path: Path) -> str | None:
    """Return a short digest of the card file, or None if it cannot be read."""
    try:
        return hashlib.sha256(card_path.read_bytes()).hexdigest()[:12]
    except OSError:
        return None


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Serve the Lovelace card and load it, so no manual resource step is needed."""
    www_dir = Path(__file__).parent / "www"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(www_dir), True)]
    )

    # The static path sets long-lived cache headers, so the query string is the
    # only thing that tells a browser to re-fetch the card.  Deriving it from
    # the file's contents rather than the integration version means an edited
    # card is always picked up — a version-based token silently serves a stale
    # copy to every browser that already has one whenever the card changes
    # without a release, which is the normal case while developing.
    fingerprint = await hass.async_add_executor_job(
        _card_fingerprint, www_dir / CARD_FILENAME
    )
    if fingerprint is None:
        integration = await async_get_integration(hass, DOMAIN)
        fingerprint = str(integration.version)
        _LOGGER.warning(
            "Could not read %s to fingerprint it; falling back to the "
            "integration version, which may serve a cached card",
            CARD_FILENAME,
        )

    add_extra_js_url(hass, f"{STATIC_URL}/{CARD_FILENAME}?v={fingerprint}")
