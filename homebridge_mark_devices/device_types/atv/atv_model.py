import typing

from pyatv.const import Protocol
from device_types.device_model import DeviceModel, DeviceConfig


class ATVConfig(DeviceConfig):
    on: int
    id: str
    airplay_credentials: str
    companion_credentials: str


class ATVCred(typing.TypedDict):
    code: str
    protocol: Protocol


class ATVCreds(typing.TypedDict):
    airplay: ATVCred
    companion: ATVCred


class ATVModel(DeviceModel):
    def __init__(self, name: str):
        super().__init__(name)
        self._config = typing.cast(ATVConfig, self._config)

    @property
    def id(self) -> str:
        return self._config["id"]

    @id.setter
    def id(self, value):
        self._config["id"] = value
        self.save_config()
