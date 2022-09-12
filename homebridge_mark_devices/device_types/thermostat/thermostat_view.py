import typing

from ...shared.c_enums import *
from .thermostat_model import ThermostatModel

import requests


class ThermostatView(ThermostatModel):
    def __init__(self, name) -> None:
        super().__init__(name)

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

        return HeaterCoolerCurrentState(ac.json()["values"]["CurrentHeaterCoolerState"])

    @real_state.setter
    def real_state(self, value: HeaterCoolerTargetState):

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
            self.url + "accessories/" + self.weather_ID, headers=self.auth_headers_dict
        )
        return x.json()["values"]["CurrentTemperature"]
