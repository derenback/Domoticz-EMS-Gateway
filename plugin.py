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

@dataclass
class device_info:
    unit: int
    type: int
    sub: int
    ident: str
    name: str

heartbeat = 5
heartbeat_count = 0

boiler_units = [device_info( 1, 80, 5,"outdoortemp","Outdoor"),
                device_info( 2, 80, 5,"rettemp","Radiator return"),
                device_info( 3, 80, 5,"curflowtemp","Radiator out"),
                device_info( 4, 80, 5,"wwcurtemp","Water"),
                device_info(10,113, 0,"nrgsuppww","Water (supplied)"),
                device_info(11,113, 0,"nrgsuppheating","Heating (supplied)"),
                device_info(12,113, 0,"nrgconscompheating","Heating (used)"),
                device_info(13,113, 0,"nrgconscompww","Water (used)"),
                device_info(20,243, 6,"curburnpow","Power"),
                device_info(21,243, 6,"hpcircspd","Circulation pump speed"),
                device_info(22,243, 6,"hpbrinepumpspd","Brine pump speed"),
                device_info(23,243, 6,"hpcompspd","Compressor speed"),
                device_info(30,244,73,"wwactivated","Warm water"),
                device_info(31,244,73,"wwheat","Warm water heater"),
                device_info(33,244,73,"wwdisinfecting","Water disinfection"),
                device_info(40,248, 1,"hppower","Power")]


def updateDevice(device, value):
    if Parameters["Mode4"] == "Debug":
        Domoticz.Log("EMS " + device.name + " : " + str(value))
    
    if device.type == 80:
        value = round(float(value), 1)
        Devices[device.unit].Update(nValue=1, sValue=str(value))
    elif device.type == 113:
        Devices[device.unit].Update(nValue=0, sValue=str(float(value) * 1000))
    elif device.type == 243:
        Devices[device.unit].Update(nValue=1, sValue=str(value))
    elif device.type == 244:
        if str(value) == "1":
            Devices[device.unit].Update(nValue=1,sValue="on")
        elif str(value) == "0":
            Devices[device.unit].Update(nValue=0,sValue="off")
    elif device.type == 248:
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

    for device in boiler_units:
        if device.unit not in Devices:
            Domoticz.Log("EMS Created sensor " + device.name)
            if device.type == 113:
                Domoticz.Device(Name=device.name, Unit=device.unit, Type=device.type, Subtype=device.sub, Switchtype=4, Used=1).Create()
            elif device.type == 244:
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
            for device in boiler_units:
                if device.ident in json_response:
                    updateDevice(device, json_response[device.ident])
        except:
            Domoticz.Log("EMS Failed to get data from gateway")

def onStop():
    Domoticz.Log("EMS Stopped")
