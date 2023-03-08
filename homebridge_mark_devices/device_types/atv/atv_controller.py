import asyncio
import logging
from .atv_model import ATVConfig, ATVCreds, ATVModel
from shared import c_enums

from pyatv import scan, pair, connect
from pyatv.const import Protocol, PowerState, DeviceState, MediaType
from pyatv.interface import AppleTV, BaseConfig


class ATVController(ATVModel):
    _config: ATVConfig | None
    atv: AppleTV | None
    atv_config: BaseConfig | None

    def __init__(
        self,
        name: str,
    ):
        super().__init__(name)

    def get(self, characteristic: str):
        match characteristic:
            case "Playing":
                return int(self.playing)
            case "Music":
                return int(self.music)
            case "Video":
                return int(self.video)

    async def setup_apple_tv(self):

        self.atv_config = await self.get_atv_config()

        if (
            self.credentials["airplay"] == ""
            and self.credentials["airplay"] == ""
            and self.atv_config != None
        ):
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
        return self.config["credentials"]

    @credentials.setter
    def credentials(self, creds: ATVCreds):
        config = self.config
        config["credentials"] = creds
        self.config = config

    @property
    def device_state(self):
        return DeviceState(self.config["device_state"])

    @device_state.setter
    def device_state(self, state: DeviceState):
        config: ATVConfig = self.config
        config["device_state"] = int(state.value)
        self.config = config

    @property
    def title(self):
        return self.config["title"]

    @title.setter
    def title(self, text: str):
        config = self.config
        config["title"] = text
        self.config = config

    @property
    def media_type(self):
        return MediaType(self.config["media_type"])

    @media_type.setter
    def media_type(self, media_type: MediaType):
        config = self.config
        config["media_type"] = int(media_type.value)
        self.config = config

    @property
    def video(self):
        if self.media_type == MediaType.TV or self.media_type == MediaType.Video:
            return True
        else:
            return False

    @property
    def music(self):
        if self.media_type == MediaType.Music:
            return True
        else:
            return False

    @property
    def playing(self):
        if (self.device_state) == DeviceState.Playing:
            return True
        else:
            return False

    async def get_metadata(self):
        logging.debug("Get Playing")

        if self.atv != None:
            return await self.atv.metadata.playing()

        return None

    async def set_playing(self, playing: c_enums.SwitchState):
        if self.atv != None:
            if playing == c_enums.SwitchState.ON:
                success = await self.atv.remote_control.play()
            else:
                success = await self.atv.remote_control.pause()

            return True

        return False

    async def get_on(self):
        if self.atv != None:
            on = self.atv.power.power_state
            print("On: " + str(on))

            if on == PowerState.On:
                return True
            else:
                return False

        return False

    async def set_on(self, on: c_enums.SwitchState):
        pass

    async def get_atv_config(self):

        atv = (await scan(asyncio.get_event_loop(), identifier=self.id))[0]
        return atv

    async def pair_atv(self):

        cred: ATVCreds = {"airplay": "", "companion": "", "mrp": ""}

        if self.atv_config == None:
            logging.error("ATV Config doesn't Exist")
            return cred

        # For loop iterate twice
        for i in range(2):
            if i == 0:
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
                elif protocol == Protocol.Companion:
                    cred["companion"] = pairing.service.credentials
                else:
                    cred["mrp"] = pairing.service.credentials

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

    async def update_values(self):
        setup = await self.setup_apple_tv()

        if self.atv:
            test = self.atv.power.power_state

            print(test)

        if self.atv != None and setup:
            metadata = await self.get_metadata()

            if metadata != None:
                print("Metadata")
                print(metadata)

                self.device_state = metadata.device_state
                self.media_type = metadata.media_type
                self.title = metadata.title if metadata.title else ""

            else:
                self.device_state = DeviceState.Idle
                self.media_type = MediaType.Unknown
                self.title = ""

        return True
