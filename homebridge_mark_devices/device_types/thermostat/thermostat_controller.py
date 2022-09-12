from device_types.thermostat.thermostat_model import *
from shared.c_enums import *
from shared.globals import *


class ThermostatController(ThermostatModel):
    def __init__(
        self,
        name: str,
    ):
        super().__init__(name)

    def set(self, characteristic: str, option: str = ""):

        result = ""

        match characteristic:
            case "TargetTemperature":
                self.target_temperature = float(option)
            case "TargetHeatingCoolingState":
                self.state = ThermostatState(int(option))
            case "RealState":
                self.real_state = HeaterCoolerTargetState(int(option))
            case "RealActive":
                self.heater_cooler_active = Active(int(option))
            case _:
                result = "Unknown characteristic"

        return str(result)

    @property
    def current_state(self) -> ThermostatCurrentState:
        real_state = self.real_state

        currentState: ThermostatCurrentState = ThermostatCurrentState.OFF

        if real_state == HeaterCoolerCurrentState.COOLING:
            currentState = ThermostatCurrentState.COOL
        elif real_state == HeaterCoolerCurrentState.HEATING:
            currentState = ThermostatCurrentState.HEAT
        elif real_state == HeaterCoolerCurrentState.IDLE:
            currentState = ThermostatCurrentState.OFF
        elif real_state == HeaterCoolerCurrentState.OFF:
            currentState = ThermostatCurrentState.OFF

        return currentState
