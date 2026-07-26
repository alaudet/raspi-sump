"""Websocket API so the Lovelace card can read readings through Home Assistant.

The card never talks to the Raspberry Pi directly: it asks Home Assistant, which
already holds the connection details.  That keeps the Pi's address out of the
browser, sidesteps CORS, and means the card inherits Home Assistant's own
authentication without raspi-sump having to grow any.
"""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, callback

from .api import RaspiSumpError
from .const import DOMAIN, WS_TYPE_READINGS
from .coordinator import RaspiSumpConfigEntry

DATE = vol.Match(r"^\d{4}-\d{2}-\d{2}$")
DATETIME = vol.Match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")


@callback
def async_setup(hass: HomeAssistant) -> None:
    """Register the Raspi-Sump websocket commands."""
    websocket_api.async_register_command(hass, ws_readings)


def _async_resolve_entry(
    hass: HomeAssistant, entry_id: str | None
) -> RaspiSumpConfigEntry:
    """Return the requested config entry, or the only one when unspecified."""
    loaded = [
        entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.state is ConfigEntryState.LOADED
    ]

    if entry_id is not None:
        for entry in loaded:
            if entry.entry_id == entry_id:
                return entry
        raise ValueError(f"No loaded Raspi-Sump config entry with id {entry_id}")

    if not loaded:
        raise ValueError("No loaded Raspi-Sump config entry")
    if len(loaded) > 1:
        raise ValueError(
            "Several Raspi-Sump instances are configured; "
            "set entry_id in the card configuration"
        )
    return loaded[0]


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_TYPE_READINGS,
        vol.Optional("entry_id"): str,
        vol.Optional("date"): DATE,
        vol.Optional("start"): DATETIME,
        vol.Optional("end"): DATETIME,
    }
)
@websocket_api.async_response
async def ws_readings(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Return a readings series, in the shape the uPlot chart consumes.

    The date parameters are pattern-matched above so this stays a fixed-shape
    proxy rather than an arbitrary query passthrough.
    """
    try:
        entry = _async_resolve_entry(hass, msg.get("entry_id"))
    except ValueError as err:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, str(err))
        return

    try:
        readings = await entry.runtime_data.client.async_get_readings(
            date=msg.get("date"), start=msg.get("start"), end=msg.get("end")
        )
    except RaspiSumpError as err:
        connection.send_error(
            msg["id"], websocket_api.ERR_HOME_ASSISTANT_ERROR, str(err)
        )
        return

    connection.send_result(msg["id"], readings)
