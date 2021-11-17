# Domoticz plugin for EMS Gateway REST API
The official MQTT based plugin ([Here](https://github.com/bbqkees/ems-esp-domoticz-plugin))
More ([documentaion](https://emsesp.github.io/docs/#/Command?id=http-api))

## Requirements
- Python 3.x (requests, json)

## Installation
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
- Domoticz version: 2020.2 (build 11997)
- EMS ESP32 - BBQKees gateway E32
- Boiler: Bosch Enviline/Compress 6000AW/Hybrid 7000iAW/SupraEco

## Version history
    0.0.1 Initial version


