import typing

from pyatv.const import Protocol
from device_types.device_model import DeviceModel, DeviceConfig


class ATVCred(typing.TypedDict):
    code: str
    protocol: Protocol


class ATVCreds(typing.TypedDict):
    airplay: str
    companion: str


class ATVConfig(DeviceConfig):
    on: bool
    playing: bool
    media_type: int
    id: str
    crendentials: ATVCreds


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
