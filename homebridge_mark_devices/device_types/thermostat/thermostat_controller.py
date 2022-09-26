from device_types.thermostat.thermostat_model import *
from shared.c_enums import *
from shared.globals import *


class ThermostatController(ThermostatModel):
    def __init__(
        self,
        name: str,
    ):
        super().__init__(name)

    async def set(self, characteristic: str, option: str = ""):

        result = ""

        match characteristic:
            case "TargetTemperature":
                self.target_temperature = float(option)
            case "TargetHeatingCoolingState":
                self.thermostat_target_state = ThermostatState(int(option))
            case "RealState":
                self.real_state = HeaterCoolerTargetState(int(option))
            case "RealActive":
                self.heater_cooler_active = Active(int(option))
            case _:
                result = "Unknown characteristic"

        return str(result)
