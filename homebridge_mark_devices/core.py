# Internal Modules
import logging
import typing
from homebridge_mark_devices.device_types import device_model
from device_types.thermostat import thermostat_controller
from shared.c_enums import DeviceType
from shared.globals import *


# External Modules
import sys
import os
import pickle


async def main(io: str, device_name: str, characteristic: str, option: str):

    logging.debug("Debug mode")
    logging.debug("IO: " + io)
    logging.debug("Device: " + device_name)
    logging.debug("Characteristic: " + characteristic)
    logging.debug("Option: " + option)

    device_type = DeviceType(device_model.getType(device_name))

    logging.debug("Device type: " + str(device_type))

    match device_type:
        case DeviceType.AIR_CONDITIONER:
            device = thermostat_controller.ThermostatController(device_name)
            result = device.parse_command(io, characteristic, option)
        case DeviceType.APPLE_TV:
            device_path = os.path.join(
                BASE_PATH, "data", "devices", f"{device_name}.device"
            )
            result = ""

        case _:
            logging.debug("Unknown device type")
            result = ""

    return result
