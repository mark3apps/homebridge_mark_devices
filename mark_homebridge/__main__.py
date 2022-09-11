import asyncio
import core
import sys

from settings import *


def main():
    arguments = sys.argv[1:]
    asyncio.run(core.main(arguments), debug=DEBUG())


if __name__ == "__main__":
    main()

exit(0)
