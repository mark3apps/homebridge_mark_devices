import asyncio
import homebridge_mark_devices.controller.controller_core as controller_core
import sys

from shared.globals import *


def main():
    arguments = sys.argv[1:]
    asyncio.run(controller_core.main(arguments), debug=DEBUG())


if __name__ == "__main__":
    main()
