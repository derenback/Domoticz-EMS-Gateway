#!/usr/bin/env python
from dataclasses import dataclass
import json
import requests

ADDRESS = "192.168.0.127"

# Types
TEMPERATURE = 80
COUNTER = 113
GENERAL = 243
LIGHT_SWITCH = 244
USAGE = 248
# Subtypes
ENERGY = 0
ELECTRIC = 1
LACROSSE = 5
PERCENTAGE = 6
SWITCH = 73


@dataclass
class device_info:
    unit: int
    type: int
    sub: int
    path: str
    ident: str
    name: str

UNITS = [device_info( 1, TEMPERATURE,  LACROSSE,   "",    "outdoortemp",        "Outdoor"),
         device_info( 2, TEMPERATURE,  LACROSSE,   "",    "rettemp",            "Radiator return"),
         device_info( 3, TEMPERATURE,  LACROSSE,   "",    "curflowtemp",        "Radiator out"),
         device_info( 4, TEMPERATURE,  LACROSSE,   "dhw", "curtemp",            "Water"),
         device_info( 5, TEMPERATURE,  LACROSSE,   "",    "hpbrinein",          "Brine in"),
         device_info( 6, TEMPERATURE,  LACROSSE,   "",    "hpbrineout",         "Brine out"),
         device_info(10, COUNTER,      ENERGY,     "dhw", "nrgsupp",            "Water (supplied)"),
         device_info(11, COUNTER,      ENERGY,     "",    "nrgsuppheating",     "Heating (supplied)"),
         device_info(12, COUNTER,      ENERGY,     "",    "nrgconscompheating", "Heating (used)"),
         device_info(13, COUNTER,      ENERGY,     "dhw", "nrgconscomp",        "Water (used)"),
         device_info(20, GENERAL,      PERCENTAGE, "",    "curburnpow",         "Power"),
         device_info(21, GENERAL,      PERCENTAGE, "",    "hpcircspd",          "Circulation pump speed"),
         device_info(22, GENERAL,      PERCENTAGE, "",    "hpbrinepumpspd",     "Brine pump speed"),
         device_info(23, GENERAL,      PERCENTAGE, "",    "hpcompspd",          "Compressor speed"),
         device_info(30, LIGHT_SWITCH, SWITCH,     "dhw", "activated",          "Warm water"),
         device_info(33, LIGHT_SWITCH, SWITCH,     "dhw", "disinfecting",       "Water disinfection"),
         device_info(40, USAGE,        ELECTRIC,   "",    "hppower",            "Power")]

def test_ems():
    response = requests.get("http://" + ADDRESS + "/api/system/info/",verify=False, timeout=2)    
    json_response = json.loads(response.content.decode("utf8"))
    #print(json.dumps(json_response, indent=2, sort_keys=True))

    #print("Devices:")
    #for device in UNITS:
        #print(device.name)

    response = requests.get("http://" + ADDRESS + "/api/boiler/",verify=False, timeout=2)    
    json_response = json.loads(response.content.decode("utf8"))
    print(json.dumps(json_response, indent=2, sort_keys=True))

    for device in UNITS:
        if device.path == "":
            if device.ident in json_response:
                print(f"{device.ident: <18} {device.name: <20} {json_response[device.ident]: <5}")
        else:            
            if device.ident in json_response[device.path]:
                print(f"{device.ident: <18} {device.name: <20} {json_response[device.path][device.ident]: <5}")

test_ems()