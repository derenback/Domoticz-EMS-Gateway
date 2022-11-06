#!/usr/bin/env python
from dataclasses import dataclass
import json
import requests

ADDRESS = "192.168.0.127"

@dataclass
class device_info:
    unit: int
    type: int
    sub: int
    ident: str
    name: str

boiler_units = [device_info( 1, 80, 5,"outdoortemp","Outdoor"),
                device_info( 2, 80, 5,"rettemp","Radiator return"),
                device_info( 3, 80, 5,"curflowtemp","Radiator out"),
                device_info( 4, 80, 5,"wwcurtemp","Water"),
                device_info(10,113, 0,"nrgsuppww","Water (supplied)"),
                device_info(11,113, 0,"nrgsuppheating","Heating (supplied)"),
                device_info(12,113, 0,"nrgconscompheating","Heating (used)"),
                device_info(13,113, 0,"nrgconscompww","Water (used)"),
                device_info(20,243, 6,"curburnpow","Power"),
                device_info(30,244,73,"wwactivated","Warm water"),
                device_info(31,244,73,"wwheat","Warm water heater"),
                device_info(33,244,73,"wwdisinfecting","Water disinfection"),
                device_info(40,248, 1,"hppower","Power")]


def test_ems():
    response = requests.get("http://" + ADDRESS + "/api/system/info/",verify=False, timeout=2)    
    json_response = json.loads(response.content.decode("utf8"))
    print(json.dumps(json_response, indent=2, sort_keys=True))

    print("Devices:")
    for device in boiler_units:
        print(device.name)

    response = requests.get("http://" + ADDRESS + "/api/boiler/",verify=False, timeout=2)    
    json_response = json.loads(response.content.decode("utf8"))
    print(json.dumps(json_response, indent=2, sort_keys=True))

    for device in boiler_units:
        if device.ident in json_response:
            print(f"{device.ident: <18} {device.name: <20} {json_response[device.ident]: <5}")

test_ems()