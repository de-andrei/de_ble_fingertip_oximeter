"""Constants for DE BLE Fingertip Oximeter integration."""
from datetime import timedelta

DOMAIN = "de_ble_fingertip_oximeter"

# Device info
DEVICE_MANUFACTURER = "Contec"
DEVICE_MODEL = "PC-60FW"

# Service UUIDs
PULSEOX_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e"
PULSEOX_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"

# Update intervals
SCAN_INTERVAL = timedelta(seconds=3)
CONNECT_TIMEOUT = 10