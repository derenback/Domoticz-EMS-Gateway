#!/usr/bin/env python
"""
EMS Gateway simple integration via MQTT
Author: Derenback
Requirements:
    1. python 3.x
        + json and requests
"""
"""
<plugin key="EMS-API-GW" name="EMS Gateway REST API interface" version="0.0.8" author="Derenback">
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

import Domoticz
from dataclasses import dataclass
import json
import requests

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

heartbeat = 5
heartbeat_count = 0

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


def updateDevice(device, value):
    if Parameters["Mode4"] == "Debug":
        Domoticz.Log("EMS " + device.name + " : " + str(value))
    
    if device.type == TEMPERATURE:
        value = round(float(value), 1)
        Devices[device.unit].Update(nValue=1, sValue=str(value))
    elif device.type == COUNTER:
        Devices[device.unit].Update(nValue=0, sValue=str(float(value) * 1000))
    elif device.type == GENERAL:
        Devices[device.unit].Update(nValue=1, sValue=str(value))
    elif device.type == LIGHT_SWITCH:
        if str(value) == "1":
            Devices[device.unit].Update(nValue=1,sValue="on")
        elif str(value) == "0":
            Devices[device.unit].Update(nValue=0,sValue="off")
    elif device.type == USAGE:
        Devices[device.unit].Update(nValue=1, sValue=str(float(value) * 1000))


def onStart():
    global heartbeat
    Domoticz.Log("Domoticz EMS Gateway plugin start")

    if (Parameters["Mode4"] == "Debug"):
        Domoticz.Log("EMS Debug is On")
        try:
            response = requests.get("http://" + Parameters["Address"] + "/api/system/info/",verify=False, timeout=2)    
            json_response = json.loads(response.content.decode("utf8"))
            Domoticz.Log("EMS GW Version: " + json_response["System"]["version"])
        except:
            Domoticz.Log("EMS Failed to get version from gateway")

    Domoticz.Heartbeat(1)
    heartbeat = int(Parameters["Mode2"])

    for device in UNITS:
        if device.unit not in Devices:
            Domoticz.Log("EMS Created sensor " + device.name)
            if device.type == COUNTER:
                Domoticz.Device(Name=device.name, Unit=device.unit, Type=device.type, Subtype=device.sub, Switchtype=4, Used=1).Create()
            elif device.type == LIGHT_SWITCH:
                Domoticz.Device(Name=device.name, Unit=device.unit, Type=device.type, Subtype=device.sub, Switchtype=0, Used=1).Create()
            else:
                Domoticz.Device(Name=device.name, Unit=device.unit, Type=device.type, Subtype=device.sub, Used=1).Create()


def onHeartbeat():
    global heartbeat_count
    if heartbeat_count > 0:
        heartbeat_count -= 1
    else:
        heartbeat_count = heartbeat    
        if (Parameters["Mode4"] == "Debug"):
            Domoticz.Log("EMS Heartbeat")
        try:
            response = requests.get("http://" + Parameters["Address"] + "/api/boiler/",verify=False, timeout=2)    
            json_response = json.loads(response.content.decode("utf8"))
            for device in UNITS:
                if device.path == "":
                    if device.ident in json_response:
                        updateDevice(device, json_response[device.ident])
                else:
                    if device.ident in json_response[device.path]:
                        updateDevice(device, json_response[device.path][device.ident])
        except:
            Domoticz.Log("EMS Failed to get data from gateway")

def onStop():
    Domoticz.Log("EMS Stopped")
