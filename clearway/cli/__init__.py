"""Command-line implementation of ClearWay."""

import logging
import sys
import argparse

from ..gpio import stateMachinePanel

__LOG_FORMAT = "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s"


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
        "--use-gpio",
        help="allow the program to use the GPIOs defined in the code, rather than just displaying messages",
        action="store_true",
    )
    # l_parser.add_argument(
    #     "-v",
    #     "--version",
    #     help="print the Python version number and exit",
    #     action='version',
    #     version='%(prog)s {version}'.format(version=__version__)
    # )

    # Parse arguments
    l_args = l_parser.parse_args()

    stateMachinePanel.use_gpio(l_args.use_gpio)

    # if l_args.version:
    #     print(clearway.__version__)
    #     exit(0)


def main() -> None:
    """Program input function."""
    __parse_arg()
    __configure_logging()

    # TODO remove
    stateMachinePanel.new(5)
    stateMachinePanel.start(5)

    stateMachinePanel.signal(5)
    stateMachinePanel.end_signal(5)
    stateMachinePanel.signal(5)
    stateMachinePanel.end_signal(5)
    stateMachinePanel.signal(5)
    stateMachinePanel.end_signal(5)

    stateMachinePanel.stop(5)
    stateMachinePanel.free(5)


if __name__ == "__main__":
    main()
