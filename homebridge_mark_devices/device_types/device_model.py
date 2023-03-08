import logging
import os
import json
import time
import typing

from shared import c_enums
from shared.globals import *


class DeviceConfig(typing.TypedDict):
    type: int


class DeviceModel:
    def __init__(self, name: str):
        self.name = name
        self._config_path = os.path.join(
            BASE_PATH, "data", "devices", self.name + ".json"
        )
        self._config = typing.cast(DeviceConfig, self._load_config())

    @property
    def type(self) -> c_enums.DeviceType:
        return c_enums.DeviceType(self._config["type"])

    @type.setter
    def type(self, value: c_enums.DeviceType):
        self._config["type"] = int(value)
        self.save_config()

    def _load_config(self):
        while True:
            with open(self._config_path, "r") as f:
                if f == None or f == "":
                    config = None
                else:
                    config = json.load(f)

            if config != None:
                break
            else:
                logging.debug(
                    "Waiting for config to be created for " + self._config_path
                )
                time.sleep(1)

        return config

    def save_config(self):
        with open(self._config_path, "w") as f:
            json.dump(self._config, f)
            logging.debug("Saved config for " + self.name)


# Load Homebridge device config values by name
def getType(name: str):
    while True:
        with open(
            os.path.join(BASE_PATH, "data", "devices", f"{name}.json"),
            "r",
        ) as f:
            if f == None or f == "":
                config = None
            else:
                config = typing.cast(DeviceConfig, json.load(f))

        if config != None:
            break
        else:
            logging.debug("Waiting for config to be created for " + name)
            time.sleep(1)

    return config["type"]
