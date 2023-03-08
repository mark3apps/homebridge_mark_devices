import argparse
import logging
import task_scheduler

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

    parser.add_argument(
        "io", type=str, choices=["Set", "Get", "Update", "Schedule"], help="IO"
    )
    parser.add_argument(
        "device_name", type=str, help="Device name", nargs="?", default=""
    )
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
    if args.debug == True:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
            datefmt="%H:%M:%S",
        )

    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    logger.debug("debug mode enabled")

    logger.debug("IO: " + args.io)
    logger.debug("Device: " + args.device_name)
    logger.debug("Characteristic: " + args.characteristic)
    logger.debug("Option: " + args.option)

    if args.io != "Schedule":
        logger.debug("Running Once")

        result = core.main(args.io, args.device_name, args.characteristic, args.option)

        if result != None:
            print(result)

    else:
        logger.debug("Running Scheduler")
        task_scheduler.start(args)
