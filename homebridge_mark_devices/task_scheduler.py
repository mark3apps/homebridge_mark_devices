from argparse import Namespace
import logging
import schedule
import time
import os
import json
from shared.c_enums import DeviceType
from shared.globals import *
from device_types.thermostat import thermostat_model

# logging.basicConfig(
#     level=logging.DEBUG,
#     format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
#     datefmt="%H:%M:%S",
#     handlers=[
#         logging.FileHandler(BASE_PATH, "/logs/debug.log"),
#         logging.StreamHandler(),
#     ],
# )
logger = logging.getLogger(__name__)


def update_values():
    # Load Config JSON file
    with open(os.path.join(BASE_PATH, "config.json"), "r") as f:
        config = json.load(f)

    # Iterate through each device and update them
    for device_config in config["devices"]:
        try:

            # Get device
            match device_config["type"]:
                case DeviceType.AIR_CONDITIONER:
                    device = thermostat_model.ThermostatModel(
                        device_config["name"])
                    results = device.update_values()
                case _:
                    results = False

            logger.info(
                "Updated Values for Device: " + device_config["name"] +
                " with result: " + str(results)
            )
        except Exception as e:
            logger.error("Failed updating " +
                         device_config["name"] + ": " + str(e))


def update_services():
    # Load Config JSON file
    with open(os.path.join(BASE_PATH, "config.json"), "r") as f:
        config = json.load(f)

    # Iterate through each device and update them
    for device_config in config["devices"]:
        try:

            # Get device
            match device_config["type"]:
                case DeviceType.AIR_CONDITIONER:
                    device = thermostat_model.ThermostatModel(
                        device_config["name"])
                    results_hold = device.update_service()
                case _:
                    results_hold = None

            # Check if results hold is not a boolean
            if results_hold == None:
                results = False
            else:
                results = results_hold

            logger.info(
                "Updated Service for Device: " + device_config["name"] +
                " with result: " + str(results)
            )
        except Exception as e:
            logger.error("Failed updating " +
                         device_config["name"] + ": " + str(e))


def start(args: Namespace):
    schedule.every(2).seconds.do(update_values)
    time.sleep(1)
    schedule.every(4).seconds.do(update_services)

    while True:
        logger.info("")
        logger.info("Running pending tasks")
        schedule.run_pending()
        time.sleep(1)
