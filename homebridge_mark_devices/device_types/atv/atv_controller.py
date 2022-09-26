import asyncio
import typing
from .atv_model import ATVConfig, ATVCred, ATVCreds, ATVModel
from shared import c_enums

from pyatv import scan, pair, connect
from pyatv.const import Protocol
from pyatv.interface import AppleTV, BaseConfig

from shared.globals import DEBUG


class ATVController(ATVModel):
    _config: ATVConfig
    atv: AppleTV | None
    atv_config: BaseConfig | None

    def __init__(
        self,
        name: str,
    ):
        super().__init__(name)
        self.load_config()

    async def parse_command(self, io: str, characteristic: str, option: str = ""):
        match io:
            case "Get":
                match characteristic:
                    case "On":
                        print(str(await self.get_on()))
                    case "Playing":
                        print(str(await self.get_playing()))

            case "Set":
                match characteristic:
                    case "On":
                        await self.set_on(c_enums.SwitchState(option))
                    case "Playing":
                        await self.set_playing(c_enums.SwitchState(option))

    def load_config(self):
        self._config = typing.cast(ATVConfig, self._load_config())

    async def setup_atv(self):

        self.atv_config = await self.get_atv_config()

        if self.credentials["airplay"] == "" and self.credentials["airplay"] == "":
            self.credentials = await self.pair_atv()

        self.atv = await self.connect_TV()

        if (
            self.atv != None
            and self.credentials["airplay"] != ""
            and self.atv_config != None
        ):
            return True

        return False

    @property
    def credentials(self):
        return self._config["crendentials"]

    @credentials.setter
    def credentials(self, creds: ATVCreds):
        self._config["crendentials"] = creds
        self.save_config()

    @property
    def on(self):
        return self._config["on"]

    @on.setter
    def on(self, state: bool):
        self.load_config()
        self._config["on"] = state
        self.save_config()

    @property
    def playing(self):
        return self._config["playing"]

    @playing.setter
    def playing(self, state: bool):
        self.load_config()
        self._config["playing"] = state
        self.save_config()

    @property
    def media_type(self):
        return self._config["media_type"]

    @media_type.setter
    def media_type(self, value: int):
        self.load_config()
        self._config["media_type"] = value
        self.save_config()

    async def get_playing(self):
        if self.atv != None:
            playing = await self.atv.metadata.playing()

            if DEBUG():
                print("Playing: ", playing)

            if playing.device_state == "playing":
                return True

        return False

    async def set_playing(self, playing: c_enums.SwitchState):
        if self.atv != None:
            if playing == c_enums.SwitchState.ON:
                success = await self.atv.remote_control.play()
            else:
                success = await self.atv.remote_control.pause()

            return True

        return False

    async def get_on(self):
        return self._config["on"]

    async def set_on(self, on: c_enums.SwitchState):
        pass

    async def get_atv_config(self):

        atv = (await scan(asyncio.get_event_loop(), identifier=self.id))[0]
        return atv

    async def pair_atv(self):

        cred: ATVCreds = {"airplay": "", "companion": ""}

        if self.atv_config == None:
            return cred

        # For loop iterate twice
        for i in range(2):
            if i == 1:
                protocol = Protocol.Companion
            else:
                protocol = Protocol.AirPlay

            pairing = await pair(self.atv_config, protocol, asyncio.get_event_loop())
            await pairing.begin()

            if pairing.device_provides_pin:
                pin = int(input("Enter PIN: "))
                pairing.pin(pin)
            else:
                pairing.pin(1234)  # Should be randomized
                input("Enter this PIN on the device: 1234")

            await pairing.finish()

            # Give some feedback about the process
            if pairing.has_paired:
                print("Paired with device!")
                print("Credentials:", pairing.service.credentials)
            else:
                print("Did not pair with device!")

            if pairing.service.credentials:
                if protocol == Protocol.AirPlay:
                    cred["airplay"] = pairing.service.credentials
                else:
                    cred["companion"] = pairing.service.credentials

                await pairing.close()
            else:
                await pairing.close()

        return cred

    async def connect_TV(self):

        if self.atv_config == None:
            return None

        airplay_success: bool = False
        companion_success: bool = False

        if self.credentials["airplay"] != "":
            airplay_success = self.atv_config.set_credentials(
                Protocol.AirPlay,
                self.credentials["airplay"],
            )
        if self.credentials["companion"] != "":
            companion_success = self.atv_config.set_credentials(
                Protocol.Companion,
                self.credentials["companion"],
            )

        if airplay_success and companion_success:

            # Connect to the device and print some information
            atv = await connect(self.atv_config, asyncio.get_event_loop())
            return atv

        return None
