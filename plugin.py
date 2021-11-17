#!/usr/bin/env python
"""
EMS Gateway simple integration via MQTT
Author: Derenback
Requirements:
    1. python 3.x
        + json and requests
"""
"""
<plugin key="EMS-API-GW" name="EMS GW REST API interface" version="0.0.1" author="Derenback">
    <params>
        <param field="Address" label="EMS Bridge IP" width="200px" required="true" default="192.168.0.127"/>
        <param field="Mode2" label="Reading Interval sec." width="40px" required="true" default="10" />
        <param field="Mode3" label="Token" width="800px" required="true" default="Your token!" />
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
import json
import requests

class device_info:
  def __init__(self, unit, type, sub, ident, name):
    self.unit = unit
    self.type = type
    self.sub = sub
    self.ident = ident
    self.name = name

boiler_units = [device_info( 1,80,5,"outdoortemp","Outdoor"),
                device_info( 2,80,5,"rettemp","Radiator return"),
                device_info( 3,80,5,"curflowtemp","Radiator out"),
                device_info( 4,80,5,"wwcurtemp","Water"),
                device_info(10,113,0,"nrgsuppww","Water (sup)"),
                device_info(11,113,0,"nrgsuppheating","Heating (sup)"),
                device_info(12,113,0,"nrgconscompheating","Heating (used)"),
                device_info(13,113,0,"nrgconscompww","Water (used)"),
                device_info(20,243,6,"curburnpow","Power"),
                device_info(30,244,73,"wwactivated","Warm water"),
                device_info(31,244,73,"wwheat","Warm water heater"),
                device_info(33,244,73,"wwdisinfecting","Water deisinfection"),
                device_info(40,248,1,"hppower","Power")]


def updateDevice(device, deviceValue):
    if (Parameters["Mode4"] == "Debug"):
        Domoticz.Log("EMS " + device.name + " : " + str(deviceValue))
    if (device.type == 80 and device.sub == 5) or (device.type == 81 and device.sub == 1):
        deviceValue = round(float(deviceValue), 1)
        Devices[device.unit].Update(nValue=1, sValue=str(deviceValue))
    if device.type == 113 and device.sub == 0:
        Devices[device.unit].Update(nValue=0, sValue=str(deviceValue))
    if device.type == 242 and device.sub == 1:
        Devices[device.unit].Update(nValue=1, sValue=str(deviceValue))
    if device.type == 243 and (device.sub in [6, 9, 19, 23]):
        Devices[device.unit].Update(nValue=1, sValue=str(float(deviceValue) * 1000))
    if device.type == 244 and device.sub == 73:
        if (str(deviceValue) == "1"):
            Devices[device.unit].Update(nValue=1,sValue="on")
        if (str(deviceValue) == "0"):
            Devices[device.unit].Update(nValue=0,sValue="off")
    if device.type == 248:
        deviceValue = float(deviceValue) * 1000
        Devices[device.unit].Update(nValue=1, sValue=str(deviceValue))


def onStart():
    Domoticz.Log("Domoticz EMS Gateway plugin start")

    if (Parameters["Mode4"] == "Debug"):
        Domoticz.Log("EMS Debug is On")

    Domoticz.Heartbeat(int(Parameters["Mode2"]))

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
    if (Parameters["Mode4"] == "Debug"):
        Domoticz.Log("EMS Heartbeat")
    url = "http://" + Parameters["Address"] + "/api/boiler/"
    token = Parameters["Mode3"]
    headers = { 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token }
    response = requests.get(url, headers=headers, verify=False)    
    json_response = json.loads(response.content.decode("utf8"))
    for device in boiler_units:
        if device.ident in json_response:
            updateDevice(device, json_response[device.ident])

def onStop():
    Domoticz.Log("EMS Stopped")

