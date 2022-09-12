from typing import TypedDict
import shared.c_enums as c_enums
from pyatv.const import Protocol

##
# General
##


class AuthHeader(TypedDict):
    accept: str
    Authorization: str


class Credentials(TypedDict):
    username: str
    password: str
    url: str


##
# Device Configs
##


class BaseDeviceConfig(TypedDict):
    type: int


class AirConditionerConfig(BaseDeviceConfig):
    realID: str
    dummyID: str
    state: int
    target_temp: float
    weatherID: str


class ATVConfig(BaseDeviceConfig):
    on: int
    id: str
    airplay_credentials: str
    companion_credentials: str


class SwitchConfig(BaseDeviceConfig):
    realID: str
    dummyID: str
    state: c_enums.SwitchState


class ATVCred(TypedDict):
    code: str
    protocol: Protocol


class ATVCreds(TypedDict):
    airplay: ATVCred
    companion: ATVCred
