"""Sensor platform for DE BLE Fingertip Oximeter."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SpO2Sensor(coordinator, entry),
        PulseSensor(coordinator, entry),
        PerfIndexSensor(coordinator, entry),
        BatterySensor(coordinator, entry),
        ConnectionSensor(coordinator, entry),
    ])

class SpO2Sensor(SensorEntity, RestoreEntity):
    """Representation of SpO2 sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "SpO2"
    _attr_icon = "mdi:lung"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_spo2"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None
        self._attr_native_value = 0
        self._received_first_update = False

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()
        
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                self._attr_native_value = int(float(last_state.state))
                _LOGGER.debug(f"Restored {self.entity_id} = {self._attr_native_value}")
            except (ValueError, TypeError):
                _LOGGER.debug("Could not restore state for %s", self.entity_id)
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "spo2":
                if not self._received_first_update and data == 0:
                    self._received_first_update = True
                    return
                self._attr_native_value = data
                self._received_first_update = True
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> int:
        """Return the state."""
        return self._attr_native_value

class PulseSensor(SensorEntity, RestoreEntity):
    """Representation of Pulse sensor."""

    _attr_native_unit_of_measurement = "bpm"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Pulse"
    _attr_icon = "mdi:heart-pulse"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_pulse"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None
        self._attr_native_value = 0
        self._received_first_update = False

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()
        
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                self._attr_native_value = int(float(last_state.state))
                _LOGGER.debug(f"Restored {self.entity_id} = {self._attr_native_value}")
            except (ValueError, TypeError):
                _LOGGER.debug("Could not restore state for %s", self.entity_id)
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "pulse":
                if not self._received_first_update and data == 0:
                    self._received_first_update = True
                    return
                self._attr_native_value = data
                self._received_first_update = True
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> int:
        """Return the state."""
        return self._attr_native_value

class PerfIndexSensor(SensorEntity, RestoreEntity):
    """Representation of Perfusion Index sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Perfusion Index"
    _attr_icon = "mdi:waves"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_perf_index"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None
        self._attr_native_value = 0.0
        self._received_first_update = False

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()
        
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                self._attr_native_value = float(last_state.state)
                _LOGGER.debug(f"Restored {self.entity_id} = {self._attr_native_value}")
            except (ValueError, TypeError):
                _LOGGER.debug("Could not restore state for %s", self.entity_id)
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "perf_index":
                if not self._received_first_update and data == 0.0:
                    self._received_first_update = True
                    return
                self._attr_native_value = data
                self._received_first_update = True
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> float:
        """Return the state."""
        return self._attr_native_value

class BatterySensor(SensorEntity, RestoreEntity):
    """Representation of Battery sensor."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_has_entity_name = True
    _attr_name = "Battery"
    _attr_icon = "mdi:battery"
    _attr_available = True
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_battery"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None
        self._attr_native_value = 0
        self._received_first_update = False

    async def async_added_to_hass(self) -> None:
        """Restore last state."""
        await super().async_added_to_hass()
        
        if (last_state := await self.async_get_last_state()) is not None:
            try:
                self._attr_native_value = int(float(last_state.state))
                _LOGGER.debug(f"Restored {self.entity_id} = {self._attr_native_value}")
            except (ValueError, TypeError):
                _LOGGER.debug("Could not restore state for %s", self.entity_id)
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source == "battery":
                if not self._received_first_update and data == 0:
                    self._received_first_update = True
                    return
                self._attr_native_value = data
                self._received_first_update = True
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> int:
        """Return the state."""
        return self._attr_native_value

class ConnectionSensor(SensorEntity):
    """Representation of connection status (no restore needed)."""

    _attr_has_entity_name = True
    _attr_name = "Connection Status"
    _attr_icon = "mdi:bluetooth-connect"
    _attr_should_poll = False

    def __init__(self, coordinator, entry):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{entry.unique_id or entry.entry_id}_connection"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.address)},
        )
        self._async_unsub_dispatcher = None

    async def async_added_to_hass(self) -> None:
        """Run when entity about to be added."""
        await super().async_added_to_hass()
        
        @callback
        def update(source: str, data: Any) -> None:
            """Update state."""
            if source in ["connected", "disconnected"]:
                self.async_write_ha_state()
        
        self._async_unsub_dispatcher = async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.coordinator.entry_id}_update", update
        )
    
    async def async_will_remove_from_hass(self) -> None:
        """Run when entity will be removed."""
        if self._async_unsub_dispatcher:
            self._async_unsub_dispatcher()
        await super().async_will_remove_from_hass()
    
    @property
    def native_value(self) -> str:
        """Return the state."""
        if self.coordinator.connected:
            return "Connected"
        return "Disconnected"
    
    @property
    def icon(self) -> str:
        """Return icon based on connection state."""
        if self.coordinator.connected:
            return "mdi:bluetooth-connect"
        return "mdi:bluetooth-off"
