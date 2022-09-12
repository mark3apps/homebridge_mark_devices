import typing
import requests
from homebridge_mark_devices.device_types.thermostat.thermostat_model import (
    ThermostatModel,
)


from shared import c_types
from shared.c_enums import *
from shared.globals import *


class ThermostatController(ThermostatModel):
    def __init__(
        self,
        name: str,
    ):
        super().__init__(name)

    def parse_command(self, io: str, characteristic: str, option: str = ""):
        match io:
            case "Get":
                match characteristic:
                    case "CurrentTemperature":
                        self.update_AC()
                        result = self.current_temperature
                    case "TargetTemperature":
                        result = self.target_temperature
                    case "CurrentHeatingCoolingState":
                        result = self.current_state
                    case "TargetHeatingCoolingState":
                        result = self.state
                    case "RealState":
                        result = self.real_state
                    case "RealActive":
                        result = self.real_active
                    case "OutdoorTemperature":
                        result = self.outdoor_temperature
                    case "UpdateAC":
                        result = self.update_AC()
                    case _:
                        result = "Unknown characteristic"

            case "Set":
                result = ""

                match characteristic:
                    case "TargetTemperature":
                        self.target_temperature = float(option)
                    case "TargetHeatingCoolingState":
                        self.state = ThermostatState(int(option))
                    case "RealState":
                        self.real_state = HeaterCoolerTargetState(int(option))
                    case "RealActive":
                        self.real_active = Active(int(option))
                    case _:
                        result = "Unknown characteristic"
            case _:
                result = "Unknown IO"

        return str(result)

    def update_AC(self):
        real_state = self.real_state
        real_active = self.real_active
        outdoor_temp = float(self.outdoor_temperature)
        cur_temp = float(self.current_temperature)
        target_temp = float(self.target_temperature)

        if DEBUG():
            print("State: " + str(self.state))
            print("Real State: " + str(real_state))
            print("Real Active: " + str(real_active))
            print("Current Temp: " + str(cur_temp))
            print("Target Temp: " + str(target_temp))
            print("Outdoor Temp: " + str(outdoor_temp))

        if self.state == ThermostatState.OFF:  # Off
            if real_active == SwitchState.ON:
                self.real_active = Active.NO
                if DEBUG():
                    print("Turning off")

        elif self.state == ThermostatState.HEAT:  # Heating

            if DEBUG():
                print("Heating")

            # Set Mode to Heat if not already set
            if real_state == HeaterCoolerCurrentState.COOLING:
                self.real_state = HeaterCoolerTargetState.HEAT
                if DEBUG():
                    print("Setting Mode to Heat")

            # Temp is too High and Heat is on, Turn Heat off
            if target_temp < cur_temp and real_active == "1":
                self.real_active = Active.NO
                if DEBUG():
                    print("Turning off; Temp is too high")

            # Temp is too Low and Heat is off, Turn Heat on
            if (target_temp - 0.25) > cur_temp and real_active == "0":
                self.real_active = Active.YES
                self.heater_cooler_temperature = 30
                if DEBUG():
                    print("Turning on; Temp is too low")

        elif self.state == ThermostatState.COOL:  # Cooling
            if DEBUG():
                print("Cooling")

            # Set Mode to Cool if not already set
            if real_state == HeaterCoolerCurrentState.HEATING:
                self.real_state = HeaterCoolerTargetState.COOL
                self.heater_cooler_temperature = 16
                if DEBUG():
                    print("Setting Mode to Cool")

            # Temp is too Low and Cool is on, Turn Cool off
            if target_temp > cur_temp and real_active == Active.YES:
                self.real_active = Active.NO
                if DEBUG():
                    print("Turning off; Temp is too low")

            # Temp is too High and Cool is off, Turn Cool on
            if (target_temp + 0.25) < cur_temp and real_active == Active.NO:
                self.real_active = Active.YES
                self.heater_cooler_temperature = 16
                if DEBUG():
                    print("Turning on; Temp is too high")

        elif self.state == ThermostatState.AUTO:  # Auto
            weight = 0
            weightShift = "cool"

            if outdoor_temp > cur_temp:
                weight = (outdoor_temp - cur_temp) / 6
                weightShift = "cool"
            if outdoor_temp < cur_temp:
                weight = (cur_temp - outdoor_temp) / 6
                weightShift = "heat"

            if weight > 1:
                weight = 1
            elif weight < -1:
                weight = -1

            if DEBUG():
                print("Weight: " + str(weight))
                print(
                    "Heat Toggle: "
                    + str(target_temp - (6 * weight if weightShift == "cool" else 0.25))
                )
                print(
                    "Cool Toggle: "
                    + str(target_temp + (4 * weight if weightShift == "heat" else 0.25))
                )

            # Temp is too High and Heat is on, Turn Heat off
            if (
                target_temp < cur_temp
                and real_active == Active.YES
                and real_state == HeaterCoolerTargetState.HEAT
            ):
                self.real_active = Active.NO
                if DEBUG():
                    print("Turning off; Temp is too high")

            # Temp is too Low and Heat is off, Turn Heat on
            elif (
                target_temp + (4 * weight if weightShift == "cool" else 0.15)
            ) > cur_temp and real_active == Active.NO:
                self.real_state = HeaterCoolerTargetState.HEAT
                self.real_active = Active.YES

                self.heater_cooler_temperature = 30
                if DEBUG():
                    print("Turning on; Temp is too low")

            # Temp is too Low and Cool is on, Turn Cool off
            elif (
                target_temp > cur_temp
                and real_active == "1"
                and real_state == HeaterCoolerCurrentState.COOLING
            ):
                self.real_active = Active.NO
                if DEBUG():
                    print("Turning off; Temp is too low")

            # Temp is too High and Cool is off, Turn Cool on
            elif (
                target_temp + (4 * weight if weightShift == "heat" else 0.15)
            ) < cur_temp and real_active == Active.NO:
                self.real_state = HeaterCoolerTargetState.COOL
                self.real_active = Active.YES

                self.heater_cooler_temperature = 16
                if DEBUG():
                    print("Turning on; Temp is too high")

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
