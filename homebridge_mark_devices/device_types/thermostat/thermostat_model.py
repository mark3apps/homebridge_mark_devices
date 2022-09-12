import typing

from shared import c_enums
from device_types.device_model import DeviceModel, DeviceConfig
from shared import credentials


class ThermostatData(typing.TypedDict):
    real_ID: str
    dummy_ID: str
    weather_ID: str


class ThermostatValues(typing.TypedDict):
    thermostat_target_state: int
    thermostat_current_state: int
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
    def __init__(self, name: str):
        super().__init__(name)
        self._config = typing.cast(ThermostatConfig, self._config)
        self.cred = credentials.get_cred_json("creds")
        self.auth_headers = credentials.get("creds")

    #
    # Authentication
    #

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
    def thermostat_target_state(self) -> c_enums.ThermostatState:
        return c_enums.ThermostatState(
            self._config["values"]["thermostat_target_state"]
        )

    @thermostat_target_state.setter
    def thermostat_target_state(self, value: c_enums.ThermostatState):
        self._config["values"]["thermostat_target_state"] = int(value)
        self.save_config()

    @property
    def heater_cooler_temperature(self) -> float:
        return self._config["values"]["heater_cooler_temperature"]

    @heater_cooler_temperature.setter
    def heater_cooler_temperature(self, value: float):
        self._config["values"]["heater_cooler_temperature"] = value
        self.save_config()

    @property
    def thermostat_current_state(self) -> c_enums.ThermostatCurrentState:
        return c_enums.ThermostatCurrentState(
            self._config["values"]["thermostat_current_state"]
        )

    @thermostat_current_state.setter
    def thermostat_current_state(self, value: c_enums.ThermostatCurrentState):
        self._config["values"]["thermostat_current_state"] = int(value)
        self.save_config()

    @property
    def heater_cooler_current_state(self) -> c_enums.HeaterCoolerCurrentState:
        return c_enums.HeaterCoolerCurrentState(
            self._config["values"]["heater_cooler_current_state"]
        )

    @heater_cooler_current_state.setter
    def heater_cooler_current_state(self, value: c_enums.HeaterCoolerCurrentState):
        self._config["values"]["heater_cooler_current_state"] = int(value)
        self.save_config()

    @property
    def heater_cooler_target_state(self) -> c_enums.HeaterCoolerTargetState:
        return c_enums.HeaterCoolerTargetState(
            self._config["values"]["heater_cooler_target_state"]
        )

    @heater_cooler_target_state.setter
    def heater_cooler_target_state(self, value: c_enums.HeaterCoolerTargetState):
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
