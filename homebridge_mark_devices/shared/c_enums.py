from enum import IntEnum


class DeviceType(IntEnum):
    AIR_CONDITIONER = 1
    APPLE_TV = 2


class ThermostatState(IntEnum):
    OFF = 0
    HEAT = 1
    COOL = 2
    AUTO = 3


class CurrentThermostatState(IntEnum):
    OFF = 0
    HEAT = 1
    COOL = 2


class CurrentHeaterCoolerState(IntEnum):
    OFF = 0
    IDLE = 1
    HEATING = 2
    COOLING = 3


class HeaterCoolerState(IntEnum):
    AUTO = 0
    HEAT = 1
    COOL = 2


class SwitchState(IntEnum):
    OFF = 0
    ON = 1


class Active(IntEnum):
    NO = 0
    YES = 1
