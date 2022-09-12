from typing import Any
import typing
import requests
import json
import os

from shared import c_types
from device_classes.device_config import AirConditionerConfig
from shared.c_enums import *
from shared.globals import *


class AirConditioner(AirConditionerConfig):
    auth_headers: c_types.AuthHeader

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
                        print(self.get_current_temp())
                    case "TargetTemperature":
                        print(float(self.target_temp))
                    case "CurrentHeatingCoolingState":
                        print(int(self.current_state))
                    case "TargetHeatingCoolingState":
                        print(int(self.state))
                    case "CurrentRelativeHumidity":
                        print(self.get_current_humidity())
                    case "RealState":
                        print(self.real_state)
                    case "RealActive":
                        print(self.real_active)
                    case "OutdoorTemperature":
                        print(self.outdoor_temp)
                    case "UpdateAC":
                        print(self.update_AC())

            case "Set":
                match characteristic:
                    case "TargetTemperature":
                        self.target_temp = float(option)
                        exit(0)
                    case "TargetHeatingCoolingState":
                        self.state = ThermostatState(int(option))
                    case "RealState":
                        self.real_state = HeaterCoolerState(int(option))
                    case "RealActive":
                        self.real_active = Active(int(option))

        return 0

    @property
    def auth_headers_dict(self):
        return typing.cast(dict[str, str], self.auth_headers)

    def get_current_humidity(self):
        ac = requests.get(
            self.url + "accessories/" + self.real_ID,
            headers=self.auth_headers_dict,
        )
        return ac.json()["values"]["CurrentRelativeHumidity"]

    @property
    def real_state(self):
        ac = requests.get(
            self.url + "accessories/" + self.real_ID,
            headers=self.auth_headers_dict,
        )

        return CurrentHeaterCoolerState(ac.json()["values"]["CurrentHeaterCoolerState"])

    @real_state.setter
    def real_state(self, value: HeaterCoolerState):

        data = {
            "characteristicType": "TargetHeaterCoolerState",
            "value": str(value),
        }

        header = {**{"Content-Type": "application/json"}, **self.auth_headers}

        x = requests.put(
            self.url + "accessories/" + self.real_ID,
            headers=header,
            json=data,
        )

    @property
    def real_active(self):
        ac = requests.get(
            self.url + "accessories/" + self.real_ID,
            headers=self.auth_headers_dict,
        )
        return Active(ac.json()["values"]["Active"])

    @real_active.setter
    def real_active(self, value: Active):

        data = {
            "characteristicType": "Active",
            "value": str(int(value)),
        }
        header = {**{"Content-Type": "application/json"}, **self.auth_headers}

        x = requests.put(
            self.url + "accessories/" + self.real_ID,
            headers=header,
            json=data,
        )

    def update_AC(self):
        real_state = self.real_state
        real_active = self.real_active
        outdoor_temp = float(self.outdoor_temp)
        cur_temp = float(self.get_current_temp())
        target_temp = float(self.target_temp)

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
            if real_state == CurrentHeaterCoolerState.COOLING:
                self.real_state = HeaterCoolerState.HEAT
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
                self.set_real_temp("30")
                if DEBUG():
                    print("Turning on; Temp is too low")

        elif self.state == ThermostatState.COOL:  # Cooling
            if DEBUG():
                print("Cooling")

            # Set Mode to Cool if not already set
            if real_state == CurrentHeaterCoolerState.HEATING:
                self.real_state = HeaterCoolerState.COOL
                self.set_real_temp("16")
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
                self.set_real_temp("16")
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
                and real_state == HeaterCoolerState.HEAT
            ):
                self.real_active = Active.NO
                if DEBUG():
                    print("Turning off; Temp is too high")

            # Temp is too Low and Heat is off, Turn Heat on
            elif (
                target_temp + (4 * weight if weightShift == "cool" else 0.15)
            ) > cur_temp and real_active == Active.NO:
                self.real_state = HeaterCoolerState.HEAT
                self.real_active = Active.YES

                self.set_real_temp("30")
                if DEBUG():
                    print("Turning on; Temp is too low")

            # Temp is too Low and Cool is on, Turn Cool off
            elif (
                target_temp > cur_temp
                and real_active == "1"
                and real_state == CurrentHeaterCoolerState.COOLING
            ):
                self.real_active = Active.NO
                if DEBUG():
                    print("Turning off; Temp is too low")

            # Temp is too High and Cool is off, Turn Cool on
            elif (
                target_temp + (4 * weight if weightShift == "heat" else 0.15)
            ) < cur_temp and real_active == Active.NO:
                self.real_state = HeaterCoolerState.COOL
                self.real_active = Active.YES

                self.set_real_temp("16")
                if DEBUG():
                    print("Turning on; Temp is too high")

    @property
    def current_state(self) -> CurrentThermostatState:
        real_state = self.real_state

        currentState: CurrentThermostatState = CurrentThermostatState.OFF

        if real_state == CurrentHeaterCoolerState.COOLING:
            currentState = CurrentThermostatState.COOL
        elif real_state == CurrentHeaterCoolerState.HEATING:
            currentState = CurrentThermostatState.HEAT
        elif real_state == CurrentHeaterCoolerState.IDLE:
            currentState = CurrentThermostatState.OFF
        elif real_state == CurrentHeaterCoolerState.OFF:
            currentState = CurrentThermostatState.OFF

        return currentState

    def set_real_temp(self, value: str):
        data_heating = {
            "characteristicType": "HeatingThresholdTemperature",
            "value": str(value),
        }
        data_cooling = {
            "characteristicType": "CoolingThresholdTemperature",
            "value": str(value),
        }

        header = {**{"Content-Type": "application/json"}, **self.auth_headers}

        x = requests.put(
            self.url + "accessories/" + self.real_ID,
            headers=header,
            json=data_heating,
        )
        x = requests.put(
            self.url + "accessories/" + self.real_ID,
            headers=header,
            json=data_cooling,
        )

    def getAccessories(self):
        x = requests.get(self.url + "accessories", headers=self.auth_headers_dict)
        return x

    def getDummyTemp(self):
        ac = requests.get(
            self.url + "accessories/" + self.dummy_ID,
            headers=self.auth_headers_dict,
        )
        return ac.json()["values"]["CurrentTemperature"]

    def get_current_temp(self):
        ac = requests.get(
            self.url + "accessories/" + self.real_ID,
            headers=self.auth_headers_dict,
        )
        return ac.json()["values"]["CurrentTemperature"]

    @property
    def outdoor_temp(self):
        x = requests.get(
            self.url + "accessories/" + self.weatherID, headers=self.auth_headers_dict
        )
        return x.json()["values"]["CurrentTemperature"]
