"""Command-line implementation of ClearWay."""

import logging
import sys
import argparse

from ..gpio import stateMachinePanel
from ..ai import ai

__LOG_FORMAT = "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s"
__gpio_led = 5


def __configure_logging() -> None:
    """Configure the app's logger.

    The log file is stored in `ClearWay.log` and every time the program
    restart, the file is cleared.
    Is format is:
        `Date Time FileName:FunctionName Level >> Message`
        example:
            `2021-10-28 18:20:19,018 foo.py:10 [INFO] >> Foo`

    There is two mode:
        - Release mode, where the log are only print in the file, the minimum level of the lof is `INFO`.
        - Debug mode, where the log are print in the file and displayed in the console, The minimum level of the
        log is `DEBUG`.
    """
    if __debug__:
        logging.basicConfig(
            level=logging.DEBUG,
            format=__LOG_FORMAT,
            handlers=[
                logging.FileHandler("ClearWay.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
    else:
        logging.basicConfig(
            level=logging.DEBUG,
            format=__LOG_FORMAT,
            filename="ClearWay.log",
        )


def __parse_arg() -> None:
    l_parser = argparse.ArgumentParser()

    # Add arguments
    l_parser.add_argument(
        "--no-gpio",
        help="tells the program that it does not want to use the GPIOs, only the logs will be displayed",
        action="store_true",
    )
    # l_parser.add_argument(
    #     "-v",
    #     "--version",
    #     help="print the Python version number and exit",
    #     action='version',
    #     version='%(prog)s {version}'.format(version=__version__)
    # )

    l_args = l_parser.parse_args()

    # TODO remove on release
    if True:
        # Parse arguments
        stateMachinePanel.use_gpio(not l_args.no_gpio)
    else:
        stateMachinePanel.use_gpio(False)

    # if l_args.version:
    #     print(clearway.__version__)
    #     exit(0)


def main() -> None:
    """Program input function."""
    __parse_arg()
    __configure_logging()

    stateMachinePanel.new(__gpio_led)
    stateMachinePanel.start(__gpio_led)

    # Give the path to the input video to process it
    # Otherwise it will use the Raspberry Pi camera
    ai.init()
    ai.bicycle_detector(__gpio_led)

    stateMachinePanel.stop(__gpio_led)
    stateMachinePanel.free(__gpio_led)


if __name__ == "__main__":
    main()
