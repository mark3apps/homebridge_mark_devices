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
import logging


def main(io: str, device_name: str, characteristic: str, option: str):

    device_name_split = device_name.split("_")

    if len(device_name_split) == 1:
        device_type = DeviceType(device_model.getType(device_name))
    else:
        device_type = DeviceType(device_model.getType(device_name_split[0]))

    logging.debug("Device type: " + str(device_type))

    match device_type:
        case DeviceType.AIR_CONDITIONER:
            match io:
                case "Get":
                    device = thermostat_view.ThermostatView(device_name)
                    result = device.get(characteristic)
                case "Set":
                    device = thermostat_controller.ThermostatController(
                        device_name)
                    result = device.set(characteristic, option)
                case "Update":
                    device = thermostat_model.ThermostatModel(device_name)
                    if characteristic == "Service":
                        result = device.update_service()
                    else:
                        result = device.update_values()
                case _:
                    result = None

        case _:
            logging.debug("Unknown device type")
            result = None

    if result != None:
        return str(result)

    return None
