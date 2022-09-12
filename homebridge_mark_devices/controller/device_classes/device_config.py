import os
import json
import typing

from shared import c_enums, c_types, credentials
from shared.globals import *


class DeviceConfig:
    def __init__(self, name: str):
        self.name = name
        self._config_path = os.path.join(
            BASE_PATH, "data", "devices", self.name + ".json"
        )
        self.load_config()
        self.cred = credentials.get_cred_json("creds")
        self.auth_headers = credentials.get("creds")
        self._config = self.load_config()

    @property
    def url(self):
        return self.cred["url"]

    @property
    def username(self):
        return self.cred["username"]

    @property
    def password(self):
        return self.cred["password"]

    @property
    def type(self) -> c_enums.DeviceType:
        return self._config["type"]

    def load_config(self):
        with open(self._config_path, "r") as f:
            return json.load(f)

    def save_config(self):
        with open(self._config_path, "w") as f:
            json.dump(self._config, f)


class AirConditionerConfig(DeviceConfig):
    def __init__(self, name: str):
        super().__init__(name)
        self._config = typing.cast(c_types.AirConditionerConfig, self._config)

    @property
    def real_ID(self) -> str:
        return self._config["realID"]

    @property
    def dummy_ID(self) -> str:
        return self._config["dummyID"]

    @property
    def state(self) -> c_enums.ThermostatState:
        return c_enums.ThermostatState(self._config["state"])

    @state.setter
    def state(self, value: c_enums.ThermostatState):
        self._config["state"] = int(value)
        self.save_config()

    @property
    def target_temp(self):
        return self._config["target_temp"]

    @target_temp.setter
    def target_temp(self, value: float):
        self._config["target_temp"] = value
        self.save_config()

    @property
    def weatherID(self) -> str:
        return self._config["weatherID"]


class ATVConfig(DeviceConfig):
    def __init__(self, name: str):
        super().__init__(name)
        self._config = typing.cast(c_types.ATVConfig, self._config)

    @property
    def id(self) -> str:
        return self._config["id"]

    @id.setter
    def id(self, value):
        self._config["id"] = value
        self.save_config()


# Load Homebridge device config values by name
def getType(name: str):
    with open(
        os.path.join(BASE_PATH, "data", "devices", f"{name}.json"),
        "r",
    ) as f:
        config = typing.cast(c_types.BaseDeviceConfig, json.load(f))

    return config["type"]
