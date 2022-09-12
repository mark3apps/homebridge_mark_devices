from ast import Pass
import typing
import requests

from shared.c_enums import *
from device_types.device_model import DeviceModel, DeviceConfig
from shared import credentials


class ThermostatData(typing.TypedDict):
    real_ID: str
    dummy_ID: str
    weather_ID: str


class ThermostatValues(typing.TypedDict):
    thermostat_target_state: int
    thermostat_current_state: int
    heater_cooler_active: int
    heater_cooler_current_state: int
    heater_cooler_target_state: int
    heater_cooler_temperature: float
    current_temperature: float
    target_temperature: float
    outdoor_temperature: float


class ThermostatConfig(DeviceConfig):
    values: ThermostatValues
    properties: ThermostatData


class ThermostatModel(DeviceModel):
    _cred: credentials.Credentials | None = None
    _auth_headers: credentials.AuthHeader | None = None

    def __init__(self, name: str):
        super().__init__(name)
        self._config = typing.cast(ThermostatConfig, self._config)

    #
    # Authentication
    #

    @property
    def cred(self):
        if self._cred is None:
            return credentials.get_cred_json("homebridge_creds")
        else:
            return self._cred

    @property
    def auth_headers(self):
        if self._auth_headers is None:
            return credentials.get("homebridge_creds")
        else:
            return self._auth_headers

    @property
    def auth_headers_dict(self):
        return typing.cast(dict[str, str], self.auth_headers)

    @property
    def url(self):
        return self.cred["url"]

    @property
    def username(self):
        return self.cred["username"]

    @property
    def password(self):
        return self.cred["password"]

    #
    # VALUES
    #

    @property
    def thermostat_target_state(self) -> ThermostatState:
        return ThermostatState(self._config["values"]["thermostat_target_state"])

    @thermostat_target_state.setter
    def thermostat_target_state(self, value: ThermostatState):
        self._config["values"]["thermostat_target_state"] = int(value)
        self.save_config()

    @property
    def thermostat_current_state(self) -> ThermostatCurrentState:
        return ThermostatCurrentState(
            self._config["values"]["thermostat_current_state"]
        )

    @thermostat_current_state.setter
    def thermostat_current_state(self, value: ThermostatCurrentState):
        self._config["values"]["thermostat_current_state"] = int(value)
        self.save_config()

        self.set_accessory(self.real_ID, "TargetHeaterCoolerState", str(value))

    @property
    def heater_cooler_temperature(self) -> float:
        return self._config["values"]["heater_cooler_temperature"]

    @heater_cooler_temperature.setter
    def heater_cooler_temperature(self, value: float):
        self._config["values"]["heater_cooler_temperature"] = value
        self.save_config()

        self.set_accessory(self.real_ID, "HeatingThresholdTemperature", value)
        self.set_accessory(self.real_ID, "CoolingThresholdTemperature", value)

    @property
    def heater_cooler_current_state(self) -> HeaterCoolerCurrentState:
        return HeaterCoolerCurrentState(
            self._config["values"]["heater_cooler_current_state"]
        )

    @heater_cooler_current_state.setter
    def heater_cooler_current_state(self, value: HeaterCoolerCurrentState):
        self._config["values"]["heater_cooler_current_state"] = int(value)
        self.save_config()

    @property
    def heater_cooler_target_state(self) -> HeaterCoolerTargetState:
        return HeaterCoolerTargetState(
            self._config["values"]["heater_cooler_target_state"]
        )

    @heater_cooler_target_state.setter
    def heater_cooler_target_state(self, value: HeaterCoolerTargetState):
        self._config["values"]["heater_cooler_target_state"] = int(value)
        self.save_config()

    @property
    def target_temperature(self):
        return self._config["values"]["target_temperature"]

    @target_temperature.setter
    def target_temperature(self, value: float):
        self._config["values"]["target_temperature"] = value
        self.save_config()

    @property
    def current_temperature(self):
        return self._config["values"]["current_temperature"]

    @current_temperature.setter
    def current_temperature(self, value: float):
        self._config["values"]["current_temperature"] = value
        self.save_config()

    @property
    def outdoor_temperature(self):
        return self._config["values"]["outdoor_temperature"]

    @outdoor_temperature.setter
    def outdoor_temperature(self, value: float):
        self._config["values"]["outdoor_temperature"] = value
        self.save_config()

    @property
    def heater_cooler_active(self):
        return Active(self._config["values"]["heater_cooler_active"])

    @heater_cooler_active.setter
    def heater_cooler_active(self, value: Active):
        self._config["values"]["heater_cooler_active"] = int(value)
        self.save_config()

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

    #
    # PROPERTIES
    #

    @property
    def real_ID(self) -> str:
        return self._config["properties"]["real_ID"]

    @property
    def dummy_ID(self) -> str:
        return self._config["properties"]["dummy_ID"]

    @property
    def weather_ID(self) -> str:
        return self._config["properties"]["weather_ID"]

    #
    # Updates
    #

    def set_accessory(self, id: str, characteristic: str, value: str | float | int):
        data = {
            "characteristicType": characteristic,
            "value": str(value),
        }

        header = {**{"Content-Type": "application/json"}, **self.auth_headers}

        x = requests.put(
            self.url + "accessories/" + id,
            headers=header,
            json=data,
        )

        return x

    def get_accessory(self, id: str) -> dict[str, typing.Any]:
        ac = requests.get(
            self.url + "accessories/" + id,
            headers=self.auth_headers_dict,
        )
        return ac.json()["values"]

    async def update_values(self):
        self._config["values"]["heater_cooler_current_state"] = int(
            self.get_accessory(self.real_ID)["CurrentHeaterCoolerState"]
        )
        self._config["values"]["heater_cooler_target_state"] = int(
            self.get_accessory(self.real_ID)["TargetHeaterCoolerState"]
        )
        self._config["values"]["heater_cooler_active"] = int(
            self.get_accessory(self.real_ID)["Active"]
        )
        self._config["values"]["heater_cooler_temperature"] = self.get_accessory(
            self.real_ID
        )["HeatingThresholdTemperature"]
        self._config["values"]["current_temperature"] = self.get_accessory(
            self.real_ID
        )["CurrentTemperature"]
        self._config["values"]["outdoor_temperature"] = self.get_accessory(
            self.weather_ID
        )["CurrentTemperature"]

        heater_cooler_state = self.heater_cooler_current_state

        thermostat_current_state: ThermostatCurrentState = ThermostatCurrentState.OFF

        if heater_cooler_state == HeaterCoolerCurrentState.COOLING:
            thermostat_current_state = ThermostatCurrentState.COOL
        elif heater_cooler_state == HeaterCoolerCurrentState.HEATING:
            thermostat_current_state = ThermostatCurrentState.HEAT
        elif heater_cooler_state == HeaterCoolerCurrentState.IDLE:
            thermostat_current_state = ThermostatCurrentState.OFF
        elif heater_cooler_state == HeaterCoolerCurrentState.OFF:
            thermostat_current_state = ThermostatCurrentState.OFF

        self._config["values"]["thermostat_current_state"] = thermostat_current_state

        self.save_config()
        return True

    def update_service(self):
        real_state = self.heater_cooler_target_state
        real_active = self.heater_cooler_active
        outdoor_temp = float(self.outdoor_temperature)
        current_temperature = float(self.current_temperature)
        target_temp = float(self.target_temperature)

        print("State: " + str(self.thermostat_target_state))
        print("Real State: " + str(real_state))
        print("Real Active: " + str(real_active))
        print("Current Temp: " + str(current_temperature))
        print("Target Temp: " + str(target_temp))
        print("Outdoor Temp: " + str(outdoor_temp))

        if self.thermostat_target_state == ThermostatState.OFF:  # Off
            if real_active == SwitchState.ON:
                self.heater_cooler_active = Active.NO

                print("Turning off")

        elif self.thermostat_target_state == ThermostatState.HEAT:  # Heating

            print("Heating")

            # Set Mode to Heat if not already set
            if real_state == HeaterCoolerCurrentState.COOLING:
                self.heater_cooler_target_state = HeaterCoolerTargetState.HEAT

                print("Setting Mode to Heat")

            # Temp is too High and Heat is on, Turn Heat off
            if target_temp < current_temperature and real_active == "1":
                self.heater_cooler_active = Active.NO

                print("Turning off; Temp is too high")

            # Temp is too Low and Heat is off, Turn Heat on
            if (target_temp - 0.25) > current_temperature and real_active == "0":
                self.heater_cooler_active = Active.YES
                self.heater_cooler_temperature = 30

                print("Turning on; Temp is too low")

        elif self.thermostat_target_state == ThermostatState.COOL:  # Cooling

            print("Cooling")

            # Set Mode to Cool if not already set
            if real_state == HeaterCoolerCurrentState.HEATING:
                self.heater_cooler_target_state = HeaterCoolerTargetState.COOL
                self.heater_cooler_temperature = 16

                print("Setting Mode to Cool")

            # Temp is too Low and Cool is on, Turn Cool off
            if target_temp > current_temperature and real_active == Active.YES:
                self.heater_cooler_active = Active.NO

                print("Turning off; Temp is too low")

            # Temp is too High and Cool is off, Turn Cool on
            if (target_temp + 0.25) < current_temperature and real_active == Active.NO:
                self.heater_cooler_active = Active.YES
                self.heater_cooler_temperature = 16

                print("Turning on; Temp is too high")

        elif self.thermostat_target_state == ThermostatState.AUTO:  # Auto
            weight = 0
            weightShift = "cool"

            if outdoor_temp > current_temperature:
                weight = (outdoor_temp - current_temperature) / 6
                weightShift = "cool"
            if outdoor_temp < current_temperature:
                weight = (current_temperature - outdoor_temp) / 6
                weightShift = "heat"

            if weight > 1:
                weight = 1
            elif weight < -1:
                weight = -1

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
                target_temp < current_temperature
                and real_active == Active.YES
                and real_state == HeaterCoolerTargetState.HEAT
            ):
                self.heater_cooler_active = Active.NO

                print("Turning off; Temp is too high")

            # Temp is too Low and Heat is off, Turn Heat on
            elif (
                target_temp + (4 * weight if weightShift == "cool" else 0.15)
            ) > current_temperature and real_active == Active.NO:
                self.heater_cooler_target_state = HeaterCoolerTargetState.HEAT
                self.heater_cooler_active = Active.YES

                self.heater_cooler_temperature = 30

                print("Turning on; Temp is too low")

            # Temp is too Low and Cool is on, Turn Cool off
            elif (
                target_temp > current_temperature
                and real_active == "1"
                and real_state == HeaterCoolerCurrentState.COOLING
            ):
                self.heater_cooler_active = Active.NO

                print("Turning off; Temp is too low")

            # Temp is too High and Cool is off, Turn Cool on
            elif (
                target_temp + (4 * weight if weightShift == "heat" else 0.15)
            ) < current_temperature and real_active == Active.NO:
                self.heater_cooler_target_state = HeaterCoolerTargetState.COOL
                self.heater_cooler_active = Active.YES

                self.heater_cooler_temperature = 16

                print("Turning on; Temp is too high")
