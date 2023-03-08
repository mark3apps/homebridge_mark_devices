import typing

from pyatv.const import Protocol
from device_types.device_model import DeviceModel, DeviceConfig


class ATVCred(typing.TypedDict):
    code: str
    protocol: Protocol


class ATVCreds(typing.TypedDict):
    airplay: str
    companion: str
    mrp: str


class ATVConfig(DeviceConfig):
    device_state: int
    media_type: int
    title: str
    id: str
    credentials: ATVCreds


class ATVModel(DeviceModel):
    def __init__(self, name: str):
        super().__init__(name)

    @property
    def config(self):
        if self._config == None:
            self._config = self.load_config()

        return self._config

    def load_config(self):
        return typing.cast(ATVConfig, self._load_config())

    @config.setter
    def config(self, value: ATVConfig):
        self._config = value
        self.save_config()

    @property
    def id(self) -> str:
        return self.config["id"]

    @id.setter
    def id(self, value):
        config = self.config
        config["id"] = value
        self.config = config
