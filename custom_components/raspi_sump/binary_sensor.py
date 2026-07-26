"""Binary sensor platform for the Raspi-Sump integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import RaspiSumpConfigEntry
from .entity import RaspiSumpEntity


def _is_critical(data: dict[str, Any]) -> bool | None:
    """Return whether the water level has crossed the configured alert threshold.

    Mirrors raspisump/reading.py: the recorded value is the depth of water in
    the pit, so a sump pit alerts when it rises above critical_water_level and
    a cistern alerts when it falls below.
    """
    level = data.get("level")
    critical_level = data.get("critical_level")
    if level is None or critical_level is None:
        return None
    if data.get("alert_when") == "low":
        return level < critical_level
    return level > critical_level


@dataclass(frozen=True, kw_only=True)
class RaspiSumpBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a Raspi-Sump binary sensor."""

    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSORS: tuple[RaspiSumpBinarySensorEntityDescription, ...] = (
    RaspiSumpBinarySensorEntityDescription(
        key="critical",
        translation_key="critical",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=_is_critical,
    ),
    RaspiSumpBinarySensorEntityDescription(
        key="service",
        translation_key="service",
        device_class=BinarySensorDeviceClass.RUNNING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("service_active"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RaspiSumpConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Raspi-Sump binary sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        RaspiSumpBinarySensor(coordinator, description)
        for description in BINARY_SENSORS
    )


class RaspiSumpBinarySensor(RaspiSumpEntity, BinarySensorEntity):
    """A single boolean derived from /api/status."""

    entity_description: RaspiSumpBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return the current state."""
        return self.entity_description.value_fn(self.status)
