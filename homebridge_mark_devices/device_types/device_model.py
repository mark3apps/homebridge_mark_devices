import os
import json
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
        self._config = typing.cast(DeviceConfig, self.load_config())

    @property
    def type(self) -> c_enums.DeviceType:
        return c_enums.DeviceType(self._config["type"])

    @type.setter
    def type(self, value: c_enums.DeviceType):
        self._config["type"] = int(value)
        self.save_config()

    def load_config(self):
        with open(self._config_path, "r") as f:
            return json.load(f)

    def save_config(self):
        with open(self._config_path, "w") as f:
            json.dump(self._config, f)


# Load Homebridge device config values by name
def getType(name: str):
    with open(
        os.path.join(BASE_PATH, "data", "devices", f"{name}.json"),
        "r",
    ) as f:
        config = typing.cast(DeviceConfig, json.load(f))

    return config["type"]
