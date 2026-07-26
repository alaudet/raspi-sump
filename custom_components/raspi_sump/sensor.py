"""Sensor platform for the Raspi-Sump integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfLength
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util import dt as dt_util

from .const import UNIT_CM, UNIT_INCHES
from .coordinator import RaspiSumpConfigEntry, RaspiSumpCoordinator
from .entity import RaspiSumpEntity

# raspi-sump reading labels → Home Assistant units.
UNIT_MAP = {
    UNIT_CM: UnitOfLength.CENTIMETERS,
    UNIT_INCHES: UnitOfLength.INCHES,
}


def _day(data: dict[str, Any], key: str) -> StateType:
    """Return one of today's aggregate values."""
    return (data.get("day") or {}).get(key)


def _pit_full(data: dict[str, Any]) -> StateType:
    """Return how full the pit is, as a percentage of its depth."""
    level = data.get("level")
    pit_depth = data.get("pit_depth")
    if level is None or not pit_depth:
        return None
    return max(0.0, min(100.0, level / pit_depth * 100))


def _last_reading(data: dict[str, Any]) -> datetime | None:
    """Return when the most recent reading was taken."""
    if not (last_ts := data.get("last_ts")):
        return None
    return dt_util.parse_datetime(last_ts)


@dataclass(frozen=True, kw_only=True)
class RaspiSumpSensorEntityDescription(SensorEntityDescription):
    """Describes a Raspi-Sump sensor."""

    value_fn: Callable[[dict[str, Any]], StateType | datetime]
    # Water measurements are reported in whichever unit the pit is configured
    # for, so their unit is resolved at runtime rather than declared here.
    is_level: bool = False
    exists_fn: Callable[[dict[str, Any]], bool] = lambda _data: True


SENSORS: tuple[RaspiSumpSensorEntityDescription, ...] = (
    RaspiSumpSensorEntityDescription(
        key="water_level",
        translation_key="water_level",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        is_level=True,
        value_fn=lambda data: data.get("level"),
    ),
    RaspiSumpSensorEntityDescription(
        key="pit_full",
        translation_key="pit_full",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
        value_fn=_pit_full,
    ),
    RaspiSumpSensorEntityDescription(
        key="level_min_today",
        translation_key="level_min_today",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        is_level=True,
        value_fn=lambda data: _day(data, "min"),
    ),
    RaspiSumpSensorEntityDescription(
        key="level_max_today",
        translation_key="level_max_today",
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
        is_level=True,
        value_fn=lambda data: _day(data, "max"),
    ),
    RaspiSumpSensorEntityDescription(
        key="pit_empties_today",
        translation_key="pit_empties_today",
        state_class=SensorStateClass.TOTAL_INCREASING,
        # Cycle detection is an opt-in experimental feature; without it
        # raspi-sump reports null and the entity is not worth creating.
        exists_fn=lambda data: data.get("cycles_today") is not None,
        value_fn=lambda data: data.get("cycles_today"),
    ),
    RaspiSumpSensorEntityDescription(
        key="readings_today",
        translation_key="readings_today",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: _day(data, "count"),
    ),
    RaspiSumpSensorEntityDescription(
        key="last_reading",
        translation_key="last_reading",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_last_reading,
    ),
    RaspiSumpSensorEntityDescription(
        key="critical_level",
        translation_key="critical_level",
        device_class=SensorDeviceClass.DISTANCE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
        is_level=True,
        value_fn=lambda data: data.get("critical_level"),
    ),
    RaspiSumpSensorEntityDescription(
        key="pit_depth",
        translation_key="pit_depth",
        device_class=SensorDeviceClass.DISTANCE,
        entity_category=EntityCategory.DIAGNOSTIC,
        suggested_display_precision=1,
        is_level=True,
        value_fn=lambda data: data.get("pit_depth"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: RaspiSumpConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Raspi-Sump sensors."""
    coordinator = entry.runtime_data
    async_add_entities(
        RaspiSumpSensor(coordinator, description)
        for description in SENSORS
        if description.exists_fn(coordinator.data or {})
    )


class RaspiSumpSensor(RaspiSumpEntity, SensorEntity):
    """A single value from /api/status."""

    entity_description: RaspiSumpSensorEntityDescription

    def __init__(
        self,
        coordinator: RaspiSumpCoordinator,
        description: RaspiSumpSensorEntityDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator, description)
        if description.is_level:
            # Fixed at setup: a pit does not change between metric and imperial
            # while Home Assistant is running, and a unit that moved underneath
            # a recorded sensor would invalidate its long-term statistics.
            # Centimetres is the fallback when raspi-sump cannot read its own
            # config, in which case there is no state to label anyway.
            self._attr_native_unit_of_measurement = UNIT_MAP.get(
                self.status.get("unit"), UnitOfLength.CENTIMETERS
            )

    @property
    def native_value(self) -> StateType | datetime:
        """Return the current value."""
        return self.entity_description.value_fn(self.status)
