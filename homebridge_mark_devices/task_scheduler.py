from argparse import Namespace
import asyncio
import logging
import time
import schedule
import os
import json
from shared.c_enums import DeviceType
from shared.globals import *
from device_types.thermostat import thermostat_model

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    handlers=[logging.FileHandler("logs/debug.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


def update_values():
    # Load Config JSON file
    with open(os.path.join(BASE_PATH, "config.json"), "r") as f:
        config = json.load(f)

    # Iterate through each device and update them
    for device_config in config["devices"]:
        try:
            logger.debug("")
            logger.debug("Updating device: " + device_config["name"])

            # Get device
            match device_config["type"]:
                case DeviceType.AIR_CONDITIONER:
                    device = thermostat_model.ThermostatModel(device_config["name"])
                    results_hold = device.update_values()
                case _:
                    results_hold = None

            if results_hold != None:
                results = asyncio.run(results_hold)
            else:
                results = False

            logger.debug(
                "Updated " + device_config["name"] + " with result: " + str(results)
            )
            logger.debug("")
        except Exception as e:
            logger.error("Error updating " + device_config["name"] + ": " + str(e))


def update_services():
    pass


def start(args: Namespace):
    schedule.every(5).seconds.do(update_values)
    schedule.every(8).seconds.do(update_services)

    while True:
        logger.debug("Running pending tasks")
        schedule.run_pending()
        time.sleep(1)
