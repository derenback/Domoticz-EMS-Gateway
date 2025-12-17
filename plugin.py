#!/usr/bin/env python
"""
EMS Gateway simple integration via REST API.

Author: Derenback
Requirements:
    1. Python 3.x
    2. requests library
"""
"""
<plugin key="EMS-API-GW" name="EMS Gateway REST API interface" version="0.1.2" author="Derenback">
    <params>
        <param field="Address" label="EMS Bridge IP" width="200px" required="true" default="192.168.0.127"/>
        <param field="Mode2" label="Reading Interval sec." width="40px" required="true" default="10" />
        <param field="Mode4" label="Debug" width="75px">
            <options>
                <option label="On" value="Debug"/>
                <option label="Off" value="Off" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Any

import Domoticz
import requests


# Parameter field names
PARAM_ADDRESS = "Address"
PARAM_INTERVAL = "Mode2"
PARAM_DEBUG = "Mode4"
DEBUG_ON = "Debug"

# API settings
API_TIMEOUT = 2
REQUEST_VERIFY_SSL = False


class DeviceType(IntEnum):
    """Domoticz device types."""
    TEMPERATURE = 80
    COUNTER = 113
    GENERAL = 243
    LIGHT_SWITCH = 244
    USAGE = 248


class DeviceSubtype(IntEnum):
    """Domoticz device subtypes."""
    ENERGY = 0
    ELECTRIC = 1
    LACROSSE = 5
    PERCENTAGE = 6
    SWITCH = 73


# Global state
_heartbeat_interval = 5
_heartbeat_count = 0


@dataclass
class DeviceInfo:
    """Configuration for a single EMS device sensor."""
    unit: int
    device_type: DeviceType
    subtype: DeviceSubtype
    path: str
    ident: str
    name: str


# Device definitions
DEVICES = [
    # Temperature sensors
    DeviceInfo(1, DeviceType.TEMPERATURE, DeviceSubtype.LACROSSE, "", "outdoortemp", "Outdoor"),
    DeviceInfo(2, DeviceType.TEMPERATURE, DeviceSubtype.LACROSSE, "", "rettemp", "Radiator return"),
    DeviceInfo(3, DeviceType.TEMPERATURE, DeviceSubtype.LACROSSE, "", "curflowtemp", "Radiator out"),
    DeviceInfo(4, DeviceType.TEMPERATURE, DeviceSubtype.LACROSSE, "dhw", "curtemp", "Water"),
    DeviceInfo(5, DeviceType.TEMPERATURE, DeviceSubtype.LACROSSE, "", "hpbrinein", "Brine in"),
    DeviceInfo(6, DeviceType.TEMPERATURE, DeviceSubtype.LACROSSE, "", "hpbrineout", "Brine out"),
    # Energy counters
    DeviceInfo(10, DeviceType.COUNTER, DeviceSubtype.ENERGY, "dhw", "nrgsupp", "Water (supplied)"),
    DeviceInfo(11, DeviceType.COUNTER, DeviceSubtype.ENERGY, "", "nrgsuppheating", "Heating (supplied)"),
    DeviceInfo(12, DeviceType.COUNTER, DeviceSubtype.ENERGY, "", "nrgconscompheating", "Heating (used)"),
    DeviceInfo(13, DeviceType.COUNTER, DeviceSubtype.ENERGY, "dhw", "nrgconscomp", "Water (used)"),
    # Percentage sensors
    DeviceInfo(20, DeviceType.GENERAL, DeviceSubtype.PERCENTAGE, "", "curburnpow", "Power"),
    DeviceInfo(21, DeviceType.GENERAL, DeviceSubtype.PERCENTAGE, "", "hpcircspd", "Circulation pump speed"),
    DeviceInfo(22, DeviceType.GENERAL, DeviceSubtype.PERCENTAGE, "", "hpbrinepumpspd", "Brine pump speed"),
    DeviceInfo(23, DeviceType.GENERAL, DeviceSubtype.PERCENTAGE, "", "hpcompspd", "Compressor speed"),
    # Switches
    DeviceInfo(30, DeviceType.LIGHT_SWITCH, DeviceSubtype.SWITCH, "dhw", "activated", "Warm water"),
    DeviceInfo(33, DeviceType.LIGHT_SWITCH, DeviceSubtype.SWITCH, "dhw", "disinfecting", "Water disinfection"),
    # Usage
    DeviceInfo(40, DeviceType.USAGE, DeviceSubtype.ELECTRIC, "", "hppower", "Power"),
]


def _is_debug_enabled() -> bool:
    """Check if debug mode is enabled."""
    return Parameters[PARAM_DEBUG] == DEBUG_ON


def _log_debug(message: str) -> None:
    """Log a message if debug mode is enabled."""
    if _is_debug_enabled():
        Domoticz.Log(f"EMS {message}")


def _build_api_url(endpoint: str) -> str:
    """Build the full API URL for a given endpoint."""
    return f"http://{Parameters[PARAM_ADDRESS]}/api/{endpoint}/"


def _fetch_json(endpoint: str) -> dict:
    """Fetch JSON data from the EMS gateway API."""
    url = _build_api_url(endpoint)
    response = requests.get(url, verify=REQUEST_VERIFY_SSL, timeout=API_TIMEOUT)
    return response.json()


def _get_device_value(device: DeviceInfo, data: dict) -> Any | None:
    """Extract device value from API response data."""
    if device.path:
        return data.get(device.path, {}).get(device.ident)
    return data.get(device.ident)


def _update_device(device: DeviceInfo, value: Any) -> None:
    """Update a Domoticz device with a new value."""
    if device.unit not in Devices:
        return

    _log_debug(f"{device.name}: {value}")

    unit = Devices[device.unit]

    match device.device_type:
        case DeviceType.TEMPERATURE:
            unit.Update(nValue=1, sValue=str(round(float(value), 1)))
        case DeviceType.COUNTER:
            unit.Update(nValue=0, sValue=str(float(value) * 1000))
        case DeviceType.GENERAL:
            unit.Update(nValue=1, sValue=str(value))
        case DeviceType.LIGHT_SWITCH:
            is_on = str(value) == "1"
            unit.Update(nValue=int(is_on), sValue="on" if is_on else "off")
        case DeviceType.USAGE:
            unit.Update(nValue=1, sValue=str(float(value) * 1000))


def _create_device(device: DeviceInfo) -> None:
    """Create a new Domoticz device."""
    Domoticz.Log(f"EMS Created sensor {device.name}")

    common_args = {
        "Name": device.name,
        "Unit": device.unit,
        "Type": device.device_type,
        "Subtype": device.subtype,
        "Used": 1,
    }

    match device.device_type:
        case DeviceType.COUNTER:
            Domoticz.Device(**common_args, Switchtype=4).Create()
        case DeviceType.LIGHT_SWITCH:
            Domoticz.Device(**common_args, Switchtype=0).Create()
        case _:
            Domoticz.Device(**common_args).Create()


def _create_missing_devices() -> None:
    """Create any devices that don't exist yet."""
    for device in DEVICES:
        if device.unit not in Devices:
            _create_device(device)


def _poll_devices() -> None:
    """Poll all device values from the gateway and update Domoticz."""
    try:
        data = _fetch_json("boiler")
        for device in DEVICES:
            value = _get_device_value(device, data)
            if value is not None:
                _update_device(device, value)
    except requests.RequestException:
        Domoticz.Log("EMS Failed to get data from gateway")


def onStart() -> None:
    """Plugin startup handler."""
    global _heartbeat_interval

    Domoticz.Log("Domoticz EMS Gateway plugin start")

    if _is_debug_enabled():
        Domoticz.Log("EMS Debug is On")
        try:
            info = _fetch_json("system/info")
            version = info.get("System", {}).get("version") or info.get("version", "unknown")
            Domoticz.Log(f"EMS GW Version: {version}")
        except requests.RequestException:
            Domoticz.Log("EMS Failed to get version from gateway")

    Domoticz.Heartbeat(1)
    _heartbeat_interval = int(Parameters[PARAM_INTERVAL])
    _create_missing_devices()


def onHeartbeat() -> None:
    """Periodic heartbeat handler."""
    global _heartbeat_count

    if _heartbeat_count > 0:
        _heartbeat_count -= 1
        return

    _heartbeat_count = _heartbeat_interval
    _log_debug("Heartbeat")
    _poll_devices()


def onStop() -> None:
    """Plugin shutdown handler."""
    Domoticz.Log("EMS Stopped")
