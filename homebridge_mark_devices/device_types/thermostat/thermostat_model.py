import logging
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
    _config: ThermostatConfig

    low_temp = 16.1
    high_temp = 26.1

    def __init__(self, name: str):
        super().__init__(name)

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
    # Overrides
    #

    def load_config(self):
        return typing.cast(ThermostatConfig, self._load_config())

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

        self.set_accessory(self.real_ID, "TargetHeaterCoolerState", str(int(value)))

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

    def update(self):
        self.update_values()
        self.update_service()

    def update_values(self):
        dummy_AC = self.get_accessory(self.real_ID)

        self._config = self.load_config()
        self._config["values"]["heater_cooler_current_state"] = int(
            dummy_AC["CurrentHeaterCoolerState"]
        )
        self._config["values"]["heater_cooler_active"] = dummy_AC["Active"]
        self._config["values"]["heater_cooler_temperature"] = dummy_AC[
            "HeatingThresholdTemperature"
        ]
        self._config["values"]["current_temperature"] = dummy_AC["CurrentTemperature"]
        self._config["values"]["outdoor_temperature"] = dummy_AC["CurrentTemperature"]

        if self.thermostat_target_state == ThermostatState.HEAT and self.heater_cooler_temperature != self.low_temp:
            thermostat_current_state = ThermostatCurrentState.HEAT
                
        elif self.thermostat_target_state == ThermostatState.COOL and self.heater_cooler_temperature != self.high_temp:
            thermostat_current_state = ThermostatCurrentState.COOL
        
        else:
            thermostat_current_state: ThermostatCurrentState = ThermostatCurrentState.OFF
            

        self._config["values"]["thermostat_current_state"] = thermostat_current_state

        self.save_config()
        return True

    def update_service(self):

        heater_cooler_target_state = self.heater_cooler_target_state
        heater_cooler_active = self.heater_cooler_active
        outdoor_temperature = float(self.outdoor_temperature)
        current_temperature = float(self.current_temperature)
        target_temperature = float(self.target_temperature)

        

        logging.debug("thermostat_target_state: " + str(self.thermostat_target_state))
        logging.debug("heater_cooler_target_state: " + str(heater_cooler_target_state))
        logging.debug("heater_cooler_active: " + str(heater_cooler_active))
        logging.debug("current_temperature: " + str(current_temperature))
        logging.debug("target_temperature: " + str(target_temperature))
        logging.debug("outdoor_temperature: " + str(outdoor_temperature))
        logging.debug("low Temp: " + str(self.low_temp))
        logging.debug("high Temp: " + str(self.high_temp))
        logging.debug("real target temp: " + str(self.heater_cooler_temperature))
        logging.debug("low Temp Matches Target: " + str(str(self.low_temp) == str(self.heater_cooler_temperature)))
        logging.debug("high Temp Matches Target: " + str(str(self.high_temp) == str(self.heater_cooler_temperature)))
        logging.debug("Heater Cooler Active == On: " + str(heater_cooler_active == SwitchState.ON))

        if self.thermostat_target_state == ThermostatState.OFF:  # Off
            if heater_cooler_active == SwitchState.ON:
                self.heater_cooler_active = Active.NO

                logging.debug("Turning off")

        elif self.thermostat_target_state == ThermostatState.HEAT:  # Heating

            logging.debug("Heating")
            
            if heater_cooler_active != SwitchState.ON:
                self.heater_cooler_active = Active.NO

                logging.debug("Turning on")

            # Set Mode to Heat if not already set
            if heater_cooler_target_state != HeaterCoolerTargetState.HEAT:
                self.heater_cooler_target_state = HeaterCoolerTargetState.HEAT

                logging.debug("Setting Mode to Heat")

            # Temp is too High and Heat is on, Turn Heat off
            if (
                target_temperature < current_temperature
                and self.heater_cooler_temperature != self.low_temp
            ):
                self.heater_cooler_temperature = self.low_temp

                logging.debug("Turning off; Temp is too high")

            # Temp is too Low and temp is not Low_temp, Turn Heat on
            if (
                target_temperature - 0.25
            ) > current_temperature and self.heater_cooler_temperature != self.high_temp:
                self.heater_cooler_temperature = self.high_temp

                logging.debug("Turning on; Temp is too low")

        elif self.thermostat_target_state == ThermostatState.COOL:  # Cooling

            logging.debug("Cooling")

            if heater_cooler_active != SwitchState.ON:
                self.heater_cooler_active = Active.NO

                logging.debug("Turning on")

            # Set Mode to Cool if not already set
            if heater_cooler_target_state != HeaterCoolerTargetState.COOL:
                self.heater_cooler_target_state = HeaterCoolerTargetState.COOL

                logging.debug("Setting Mode to Cool")

            # Temp is too Low and Cool is on, Turn Cool off
            if (
                target_temperature > current_temperature
                and self.heater_cooler_temperature != self.high_temp
            ):
                self.heater_cooler_temperature = self.high_temp

                logging.debug("Turning off; Temp is too low")

            # Temp is too High and Cool is off, Turn Cool on
            if (
                target_temperature + 0.25
            ) < current_temperature and self.heater_cooler_temperature != self.low_temp:
                self.heater_cooler_temperature = self.low_temp

                logging.debug("Turning on; Temp is too high")

        elif self.thermostat_target_state == ThermostatState.AUTO:  # Auto
            weight = 0
            weightShift = "cool"

            if outdoor_temperature > current_temperature:
                weight = (outdoor_temperature - current_temperature) / 6
                weightShift = "cool"
            if outdoor_temperature < current_temperature:
                weight = (current_temperature - outdoor_temperature) / 6
                weightShift = "heat"

            if weight > 1:
                weight = 1
            elif weight < -1:
                weight = -1

            logging.debug("Weight: " + str(weight))
            logging.debug(
                "Heat Toggle: "
                + str(
                    target_temperature - (6 * weight if weightShift == "cool" else 0.25)
                )
            )
            logging.debug(
                "Cool Toggle: "
                + str(
                    target_temperature + (4 * weight if weightShift == "heat" else 0.25)
                )
            )

            # Temp is too High and Heat is on, Turn Heat off
            if (
                target_temperature < current_temperature
                and heater_cooler_active == Active.YES
                and heater_cooler_target_state == HeaterCoolerTargetState.HEAT
            ):
                self.heater_cooler_active = Active.NO

                logging.debug("Turning off; Temp is too high")

            # Temp is too Low and Heat is off, Turn Heat on
            elif (
                target_temperature + (4 * weight if weightShift == "cool" else 0.15)
            ) > current_temperature and heater_cooler_active == Active.NO:
                self.heater_cooler_target_state = HeaterCoolerTargetState.HEAT
                self.heater_cooler_active = Active.YES

                self.heater_cooler_temperature = 30

                logging.debug("Turning on; Temp is too low")

            # Temp is too Low and Cool is on, Turn Cool off
            elif (
                target_temperature > current_temperature
                and heater_cooler_active == "1"
                and heater_cooler_target_state == HeaterCoolerCurrentState.COOLING
            ):
                self.heater_cooler_active = Active.NO

                logging.debug("Turning off; Temp is too low")

            # Temp is too High and Cool is off, Turn Cool on
            elif (
                target_temperature + (4 * weight if weightShift == "heat" else 0.15)
            ) < current_temperature and heater_cooler_active == Active.NO:
                self.heater_cooler_target_state = HeaterCoolerTargetState.COOL
                self.heater_cooler_active = Active.YES

                self.heater_cooler_temperature = 16

                logging.debug("Turning on; Temp is too high")
