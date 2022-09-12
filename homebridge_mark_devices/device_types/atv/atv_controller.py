import asyncio
import typing
from .atv_model import ATVCreds, ATVModel
from shared import c_enums

from pyatv import scan, pair, connect
from pyatv.const import Protocol

from shared.globals import DEBUG


class ATVController(ATVModel):
    def __init__(
        self,
        name: str,
    ):
        super().__init__(name)

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

    async def setup_atv(self):
        self.atv_config = await self.get_atv_config()
        self.atv_credentials = await self.pair_atv()
        self.atv = await self.connect_TV()

        if (
            self.atv != None
            and self.atv_credentials != None
            and self.atv_config != None
        ):
            return True

        return False

    async def get_atv_config(self):

        atv = (await scan(asyncio.get_event_loop(), identifier=self.id))[0]
        return atv

    async def pair_atv(self):

        atvs = await scan(asyncio.get_event_loop(), identifier=self.id)

        pairing = await pair(atvs[0], Protocol.Companion, asyncio.get_event_loop())
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
            creds = typing.cast(
                ATVCreds,
                {
                    "companion": {
                        "code": pairing.service.credentials,
                        "protocol": Protocol.Companion,
                    },
                    "airplay": {
                        "code": pairing.service.credentials,
                        "protocol": Protocol.AirPlay,
                    },
                },
            )
            await pairing.close()
            return creds
        else:
            await pairing.close()
            return None

    async def connect_TV(self):

        if self.atv_credentials != None:
            airplay_success = self.atv_config.set_credentials(
                self.atv_credentials["airplay"]["protocol"],
                self.atv_credentials["airplay"]["code"],
            )
            companion_success = self.atv_config.set_credentials(
                self.atv_credentials["companion"]["protocol"],
                self.atv_credentials["companion"]["code"],
            )

            if airplay_success and companion_success:

                # Connect to the device and print some information
                atv = await connect(self.atv_config, asyncio.get_event_loop())
                return atv

        return None
