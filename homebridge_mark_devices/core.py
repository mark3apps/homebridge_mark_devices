# Internal Modules

from device_types import device_model
from shared.c_enums import DeviceType
from shared.globals import *
from device_types.thermostat import (
    thermostat_model,
    thermostat_view,
    thermostat_controller,
)

# External Modules
import os
import logging


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
            match io:
                case "Get":
                    device = thermostat_view.ThermostatView(device_name)
                    result = device.get(characteristic)
                case "Set":
                    device = thermostat_controller.ThermostatController(device_name)
                    result = device.set(characteristic, option)
                case "Update":
                    device = thermostat_model.ThermostatModel(device_name)
                    result = device.update()
                case _:
                    result = "Invalid IO"

        case DeviceType.APPLE_TV:
            device_path = os.path.join(
                BASE_PATH, "data", "devices", f"{device_name}.device"
            )
            result = ""

        case _:
            logging.debug("Unknown device type")
            result = ""

    return result
