import argparse
import asyncio
import logging

import core


def main():
    # create a parser object for understanding command-line arguments
    parser = argparse.ArgumentParser(
        description="Homebridge Mark Devices",
        epilog="For more information, visit nowhere",
    )

    # add arguments
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )

    parser.add_argument("io", type=str, choices=["Set", "Get", "Update"], help="IO")
    parser.add_argument("device", type=str, help="Device name", nargs="?", default="")
    parser.add_argument(
        "characteristic", type=str, help="Characteristic name", nargs="?", default=""
    )
    parser.add_argument(
        "option",
        type=str,
        help="Option name (Required if using 'Set')",
        nargs="?",
        default="",
    )

    # parse the arguments
    args = parser.parse_args()

    # access the arguments
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("debug modes enabled")
    else:
        logging.basicConfig(level=logging.INFO)

    if args.io == "Set" or args.io == "Get":
        result = asyncio.run(
            core.main(args.io, args.device, args.characteristic, args.option)
        )
        print(result)
