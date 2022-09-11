# Internal Modules
import asyncio
import typing
from device_classes import air_conditioner, device_config, atv
from library.c_enums import DeviceType
from settings import *

# External Modules
import sys
import os
import pickle


async def main(arguments):
    length = len(arguments)

    # print(arguments)
    # print(length

    if length == 0:
        print("No arguments provided")
        return
    elif arguments[0] == "Debug":
        if length >= 2:
            io: str = arguments[1]
        else:
            io: str = ""
        if length >= 3:
            device_name: str = arguments[2]
        else:
            device_name: str = ""
        if length >= 4:
            characteristic: str = arguments[3]
        else:
            characteristic = ""
        if length >= 5:
            option: str = arguments[4]
        else:
            option = ""

        set_debug(True)
    else:
        if length >= 1:
            io: str = arguments[0]
        else:
            io = ""
        if length >= 2:
            device_name: str = arguments[1]
        else:
            device_name: str = ""
        if length >= 3:
            characteristic: str = arguments[2]
        else:
            characteristic: str = ""
        if length >= 4:
            option: str = arguments[3]
        else:
            option: str = ""

        set_debug(False)

    if DEBUG():
        print("Debug mode")
        print("IO: " + io)
        print("Device: " + device_name)
        print("Characteristic: " + characteristic)
        print("Option: " + option)

    device_type = DeviceType(device_config.getType(device_name))

    if DEBUG():
        print("Device type: " + str(device_type))

    match device_type:
        case DeviceType.AIR_CONDITIONER:
            device = air_conditioner.AirConditioner(device_name)
            device.parse_command(io, characteristic, option)
        case DeviceType.APPLE_TV:
            device_path = os.path.join(
                path(), "data", "devices", f"{device_name}.device"
            )

            # Check if Pickled object exists for this device in the data/devices folder
            # If it does, load it
            # If it doesn't, create it
            if os.path.isfile(device_path):
                with open(device_path, "rb") as file:
                    device = typing.cast(atv.ATV, pickle.load(file))

            else:
                device = atv.ATV(device_name)
                test = await device.setup_atv()

                if test:
                    await device.parse_command(io, characteristic, option)

                    if device.atv:
                        device.atv.close()

                # Save the device to the data/devices folder
                # with open(device_path, "wb") as file:
                #     pickle.dump(device, file, pickle.HIGHEST_PROTOCOL)

            # asyncio.run()
        case _:
            print("Unknown device type")
            return 1


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1:]), debug=DEBUG())
