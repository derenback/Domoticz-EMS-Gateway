# Domoticz plugin for EMS Gateway REST API
The official MQTT based plugin ([Here](https://github.com/bbqkees/ems-esp-domoticz-plugin))
More ([documentaion](https://emsesp.github.io/docs/#/Command?id=http-api))

## Requirements
- Python 3.x (requests, json)

## Installation
- Make sure to set Boolean Format to "1/0" for API/MQTT on your Gateway Settings - Formatting Options
- Make sure to have the setting "Accept new Hardware Devices" turned on for new devices to be added when adding the Hardware in domoticz.

```bash
cd ~/domoticz/plugins
git clone https://github.com/derenback/Domoticz-EMS-Gateway.git
pip3 install requests
sudo systemctl restart domoticz
```
- Create a new hardware of the type "EMS GW REST API interface"

## Update
```bash
cd ~/domoticz/plugins/Domoticz-EMS-Gateway
git pull
sudo systemctl restart domoticz
```

## Tested on
- Domoticz version: 2024.7
- EMS ESP32 - BBQKees gateway E32 
    - Versions: 3.7.0
- Boiler: Bosch Enviline/Compress 6000AW/Hybrid 7000iAW/SupraEco

## Version history
    0.1.0 Fix for breaking change in EMS ESP32 3.7.0
    0.0.8 Add support for longer poll interval
    0.0.7 Use dataclass for device list
    0.0.6 Added Compressor speed
    0.0.5 Added Brine pump speed
    0.0.4 Added Circulation pump speed
    0.0.3 Fix spelling and update readme.
    0.0.2 Added some error handling and GW version for debug
    0.0.1 Initial version


