import argparse


def main():
    # create a parser object for understanding command-line arguments
    parser = argparse.ArgumentParser(
        description="Homebridge Mark Devices",
        epilog="For more information, visit nowhere",
    )

    # add arguments
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument("io", type=str, choices=["Set", "Get", "Update"])

    # parse the arguments
    args = parser.parse_args()

    # access the arguments
    if args.debug:
        print("Debug mode enabled")
