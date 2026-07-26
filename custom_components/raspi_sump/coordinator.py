"""Polling coordinator for the Raspi-Sump integration."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import RaspiSumpClient, RaspiSumpError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

type RaspiSumpConfigEntry = ConfigEntry[RaspiSumpCoordinator]


class RaspiSumpCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Polls /api/status and shares one payload with every entity."""

    config_entry: RaspiSumpConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: RaspiSumpConfigEntry,
        client: RaspiSumpClient,
        scan_interval: int,
    ) -> None:
        """Initialise the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch the current state summary."""
        try:
            return await self.client.async_get_status()
        except RaspiSumpError as err:
            raise UpdateFailed(str(err)) from err
