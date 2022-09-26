from shared.c_enums import *
from device_types.thermostat.thermostat_model import ThermostatModel

import requests


class ThermostatView(ThermostatModel):
    def __init__(self, name) -> None:
        super().__init__(name)

    async def get(self, characteristic: str):
        match characteristic:
            case "CurrentTemperature":
                result = self.current_temperature
            case "TargetTemperature":
                result = self.target_temperature
            case "CurrentHeatingCoolingState":
                result = int(self.thermostat_current_state)
            case "TargetHeatingCoolingState":
                result = int(self.thermostat_target_state)
            case "HeaterCoolerTargetState":
                result = int(self.heater_cooler_target_state)
            case "HeaterCoolerCurrentState":
                result = int(self.heater_cooler_current_state)
            case "RealActive":
                result = int(self.heater_cooler_active)
            case "OutdoorTemperature":
                result = self.outdoor_temperature
            case _:
                result = "Unknown characteristic"

        return str(result)
