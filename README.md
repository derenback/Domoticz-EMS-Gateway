# Domoticz EMS Gateway Plugin

A Domoticz plugin that integrates with [EMS-ESP](https://emsesp.github.io/docs/) gateways via the REST API.

> **Note:** For the official MQTT-based plugin, see [ems-esp-domoticz-plugin](https://github.com/bbqkees/ems-esp-domoticz-plugin).

## Features

- Temperature monitoring (outdoor, radiator, water, brine)
- Energy consumption tracking (heating and hot water)
- Pump and compressor speed monitoring
- Hot water system control

## Requirements

- Domoticz with Python plugin support
- Python 3.x
- `requests` library

## Installation

### 1. Configure your EMS Gateway

- Go to **Gateway Settings → Formatting Options**
- Set **Boolean Format** to `1/0` for API/MQTT

### 2. Install the plugin

```bash
cd ~/domoticz/plugins
git clone https://github.com/derenback/Domoticz-EMS-Gateway.git
pip3 install requests
sudo systemctl restart domoticz
```

### 3. Add the hardware in Domoticz

1. Ensure **Setup → Settings → "Accept new Hardware Devices"** is enabled
2. Go to **Setup → Hardware**
3. Add new hardware of type **"EMS Gateway REST API interface"**
4. Enter your EMS Gateway IP address
5. Configure the polling interval (default: 10 seconds)

## Updating

```bash
cd ~/domoticz/plugins/Domoticz-EMS-Gateway
git pull
sudo systemctl restart domoticz
```

## Tested Configuration

| Component | Version/Model |
|-----------|---------------|
| Domoticz | 2024.7 |
| Gateway | BBQKees Gateway E32 |
| EMS-ESP | 3.7.0 |
| Boiler | Bosch Enviline / Compress 6000AW / Hybrid 7000iAW / SupraEco |

## Version History

| Version | Changes |
|---------|---------|
| 0.1.2 | Refatored code |
| 0.1.0 | Fix for breaking change in EMS-ESP 3.7.0 |
| 0.0.8 | Add support for longer poll interval |
| 0.0.7 | Use dataclass for device list |
| 0.0.6 | Added compressor speed |
| 0.0.5 | Added brine pump speed |
| 0.0.4 | Added circulation pump speed |
| 0.0.3 | Fix spelling and update readme |
| 0.0.2 | Added error handling and gateway version for debug |
| 0.0.1 | Initial version |

## Resources

- [EMS-ESP Documentation](https://emsesp.github.io/docs/)
- [EMS-ESP HTTP API Reference](https://emsesp.github.io/docs/#/Command?id=http-api)


