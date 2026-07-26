"""Base entity for the Raspi-Sump integration."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RaspiSumpCoordinator


class RaspiSumpEntity(CoordinatorEntity[RaspiSumpCoordinator]):
    """Common device wiring for every Raspi-Sump entity."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: RaspiSumpCoordinator, description: EntityDescription
    ) -> None:
        """Initialise the entity."""
        super().__init__(coordinator)
        self.entity_description = description

        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Raspi-Sump",
            manufacturer="linuxnorth.org",
            model="Raspi-Sump",
            sw_version=self.status.get("version"),
            # Puts a link to the real web UI on the device page.
            configuration_url=coordinator.client.base_url,
        )

    @property
    def status(self) -> dict[str, Any]:
        """Return the latest /api/status payload."""
        return self.coordinator.data or {}
