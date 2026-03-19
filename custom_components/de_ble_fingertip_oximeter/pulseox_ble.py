"""Async Python library for Fingertip Oximeter."""

import asyncio
import logging
from typing import Optional, Callable, Any, Union

from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice
from bleak_retry_connector import establish_connection, BleakClientWithServiceCache

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.WARNING)

# UUIDs из вашего ESPHome конфига
PULSEOX_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
PULSEOX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

class PulseOximeter:
    """Fingertip Oximeter interface."""
    
    def __init__(self, address_or_ble_device: Union[str, BLEDevice]):
        """Initialize pulse oximeter with address or BLEDevice."""
        if isinstance(address_or_ble_device, BLEDevice):
            self.address = address_or_ble_device.address
            self.ble_device = address_or_ble_device
        else:
            self.address = address_or_ble_device
            self.ble_device = None
            
        self.client: Optional[BleakClientWithServiceCache] = None
        self._spo2: int = 0
        self._pulse: int = 0
        self._perf_index: float = 0.0
        self._battery: int = 0
        self._callback: Optional[Callable[[str, Any], None]] = None
        self._disconnect_called = False
        
    def set_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Set callback for data updates."""
        self._callback = callback
        
    def _notification_handler(self, sender: int, data: bytearray) -> None:
        """Handle incoming notifications."""
        try:
            # Пакет с данными SpO2, Pulse, Perfusion Index (12 байт)
            if len(data) == 12 and data[0] == 0xAA and data[1] == 0x55 and data[2] == 0x0F and data[3] == 0x08:
                if data[5] != 0:  # SpO2
                    self._spo2 = data[5]
                    if self._callback:
                        self._callback("spo2", self._spo2)
                
                if data[6] != 0:  # Pulse
                    self._pulse = data[6]
                    if self._callback:
                        self._callback("pulse", self._pulse)
                
                if data[8] != 0:  # Perfusion Index
                    self._perf_index = data[8] / 10.0
                    if self._callback:
                        self._callback("perf_index", self._perf_index)
            
            # Пакет с батареей (7 байт) 
            elif len(data) == 7 and data[0] == 0xAA and data[1] == 0x55 and data[2] == 0xF0 and data[3] == 0x3 and data[4] == 0x3:
                if data[5] != 0:
                    self._battery = data[5]
                    if self._callback:
                        # Конвертация 0-3 в проценты
                        battery_percent = (self._battery / 3.0) * 100.0
                        # Ограничиваем от 0 до 100
                        if battery_percent < 0:
                            battery_percent = 0
                        if battery_percent > 100:
                            battery_percent = 100
                        self._callback("battery", battery_percent)
        except Exception:
            pass
    
    def _disconnected_callback(self, client: BleakClient) -> None:
        """Handle disconnection."""
        _LOGGER.debug("Device %s disconnected", self.address)
        self.client = None
        if self._callback and not self._disconnect_called:
            self._callback("disconnected", None)
    
    async def async_connect(self) -> bool:
        """Connect to fingertip oximeter and enable notifications."""
        if self.client and self.client.is_connected:
            return True
            
        self._disconnect_called = False
        
        try:
            if not self.ble_device:
                self.ble_device = await BleakScanner.find_device_by_address(
                    self.address, timeout=3.0
                )
                if not self.ble_device:
                    _LOGGER.debug("Device %s not found", self.address)
                    return False
            
            _LOGGER.debug("Connecting to %s", self.address)
            
            # Используем establish_connection из bleak-retry-connector
            self.client = await establish_connection(
                BleakClientWithServiceCache,
                self.ble_device,
                self.address,
                self._disconnected_callback,
                max_attempts=3,
                use_services_cache=True,
            )
            
            # Подписываемся на уведомления
            await self.client.start_notify(
                PULSEOX_CHAR_UUID,
                self._notification_handler
            )
            
            _LOGGER.debug("Connected to %s", self.address)
            
            if self._callback:
                self._callback("connected", None)
            
            return True
            
        except Exception as e:
            _LOGGER.debug("Connection failed: %s", e)
            self.client = None
            return False
    
    async def async_disconnect(self) -> None:
        """Disconnect from fingertip oximeter."""
        self._disconnect_called = True
        if self.client and self.client.is_connected:
            try:
                await self.client.stop_notify(PULSEOX_CHAR_UUID)
                await self.client.disconnect()
            except Exception:
                pass
            finally:
                self.client = None
                if self._callback:
                    self._callback("disconnected", None)
    
    @property
    def spo2(self) -> int:
        """Current SpO2 value (%)."""
        return self._spo2
    
    @property
    def pulse(self) -> int:
        """Current pulse rate (BPM)."""
        return self._pulse
    
    @property
    def perf_index(self) -> float:
        """Current perfusion index (%)."""
        return self._perf_index
    
    @property
    def battery(self) -> float:
        """Current battery level (%)."""
        return (self._battery / 3.0) * 100.0 if self._battery > 0 else 0
    
    @property
    def connected(self) -> bool:
        """Connection status."""
        return self.client is not None and self.client.is_connected
    
    @staticmethod
    async def discover_devices(timeout: float = 5.0) -> list[BLEDevice]:
        """Discover nearby pulse oximeters."""
        devices = []
        
        def detection_callback(device: BLEDevice, advertisement_data):
            if advertisement_data and advertisement_data.service_uuids:
                if PULSEOX_SERVICE_UUID in advertisement_data.service_uuids:
                    devices.append(device)
        
        scanner = BleakScanner(detection_callback)
        await scanner.start()
        await asyncio.sleep(timeout)
        await scanner.stop()
        
        return devices
