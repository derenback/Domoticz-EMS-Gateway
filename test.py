#!/usr/bin/env python
"""
Test script for EMS Gateway REST API integration.

This script validates connectivity and data retrieval from the EMS gateway.
"""

import argparse
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

import requests


# Configuration
DEFAULT_ADDRESS = "192.168.0.127"
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


def _build_api_url(address: str, endpoint: str) -> str:
    """Build the full API URL for a given endpoint."""
    return f"http://{address}/api/{endpoint}/"


def _fetch_json(address: str, endpoint: str) -> dict:
    """Fetch JSON data from the EMS gateway API."""
    url = _build_api_url(address, endpoint)
    response = requests.get(url, verify=REQUEST_VERIFY_SSL, timeout=API_TIMEOUT)
    return response.json()


def _get_device_value(device: DeviceInfo, data: dict) -> Any | None:
    """Extract device value from API response data."""
    if device.path:
        return data.get(device.path, {}).get(device.ident)
    return data.get(device.ident)


def _print_device_values(data: dict) -> None:
    """Print all device values in a formatted table."""
    print(f"\n{'Identifier':<18} {'Name':<25} {'Value':<10}")
    print("-" * 55)

    for device in DEVICES:
        value = _get_device_value(device, data)
        if value is not None:
            print(f"{device.ident:<18} {device.name:<25} {value:<10}")


def test_ems(address: str = DEFAULT_ADDRESS) -> None:
    """
    Test EMS Gateway connectivity and data retrieval.

    Args:
        address: IP address of the EMS gateway.
    """
    print(f"Testing EMS Gateway at {address}\n")

    # Fetch system info
    try:
        info = _fetch_json(address, "system/info")
        version = info.get("System", {}).get("version") or info.get("version", "unknown")
        print(f"Gateway Version: {version}")
    except requests.RequestException as e:
        print(f"Failed to get system info: {e}")
        return
    except KeyError:
        print("Gateway Version: unknown (unexpected response format)")

    # Fetch and display boiler data
    try:
        boiler_data = _fetch_json(address, "boiler")
        _print_device_values(boiler_data)
    except requests.RequestException as e:
        print(f"Failed to get boiler data: {e}")


def _parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Test EMS Gateway REST API connectivity and data retrieval."
    )
    parser.add_argument(
        "-a", "--address",
        default=DEFAULT_ADDRESS,
        help=f"IP address of the EMS gateway (default: {DEFAULT_ADDRESS})",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    test_ems(args.address)