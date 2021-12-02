"""Command-line implementation of ClearWay."""

import logging
import sys
import argparse

import clearway
from clearway.gpio import stateMachinePanel
from clearway.ai import ai

__LOG_FORMAT = "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s"
__DEFAULT_GPIO = 5
__DEFAULT_VERBOSITY_LEVEL = logging.INFO
__LOG_PATH = "ClearWay.log"

__gpio_led = None
__video_path = None
__verbosity_level = None


def __is_positive(p_value):
    l_int_value = int(p_value)
    if l_int_value <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid value, should be a positive integer" % p_value)
    return l_int_value


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
    global __verbosity_level, __DEFAULT_VERBOSITY_LEVEL, __LOG_FORMAT

    logging.basicConfig(
        level=__verbosity_level if __verbosity_level is not None else __DEFAULT_VERBOSITY_LEVEL,
        format=__LOG_FORMAT,
        handlers=[
            logging.FileHandler(__LOG_PATH),
            logging.StreamHandler(sys.stdout),
        ],
    )


def __parse_arg() -> None:
    """Parse the arguments passed in parameter at the launching of the program.

    The available optional arguments are:
        --no-gpio
            tells the program that it does not want to use the GPIOs, only the logs will be displayed
        --gpio GPIO
            tells the program which gpio to use, the default value is __DEFAULT_GPIO
        --path PATH
            the path to the video to be analyzed rather than using the video stream from the camera
        -v {WARNING,INFO,DEBUG}, --verbosity {WARNING,INFO,DEBUG}
            indicates the level of verbosity, default is __DEFAULT_VERBOSITY_LEVEL
        -V, --version
            print the project version and exit
    """
    global __gpio_led, __video_path, __verbosity_level, __DEFAULT_GPIO

    l_parser = argparse.ArgumentParser()

    # Add arguments
    l_parser.add_argument(
        "--gpio",
        help="tells the program which gpio to use, the default is {}".format(__DEFAULT_GPIO),
        action="store",
        type=__is_positive,
        default=__DEFAULT_GPIO,
    )

    l_parser.add_argument(
        "--no-gpio",
        help="tells the program that it does not want to use the GPIOs, only the logs will be displayed",
        action="store_true",
        default=False,
    )

    l_parser.add_argument(
        "--path",
        help="the path to the video to be analyzed rather than using the video stream from the camera",
        action="store",
        default=None,
    )

    l_parser.add_argument(
        "-v",
        "--verbosity",
        type=str,
        choices=[
            logging.getLevelName(logging.WARNING),
            logging.getLevelName(logging.INFO),
            logging.getLevelName(logging.DEBUG),
        ],
        help="indicates the level of verbosity, default is {}".format(logging.getLevelName(__DEFAULT_VERBOSITY_LEVEL)),
        default=__DEFAULT_VERBOSITY_LEVEL,
    )

    l_parser.add_argument(
        "-V",
        "--version",
        help="print the {} version and exit".format(clearway.__project__),
        action="version",
        version="{} {}".format(clearway.__project__, clearway.__version__),
    )

    l_args = l_parser.parse_args()

    stateMachinePanel.use_gpio(not l_args.no_gpio)
    __gpio_led = l_args.gpio
    __video_path = l_args.path

    if l_args.verbosity == logging.getLevelName(logging.WARNING):
        __verbosity_level = logging.WARNING
    elif l_args.verbosity == logging.getLevelName(logging.INFO):
        __verbosity_level = logging.INFO
    elif l_args.verbosity == logging.getLevelName(logging.DEBUG):
        __verbosity_level = logging.DEBUG


def main() -> None:
    """Program input function."""
    global __gpio_led, __DEFAULT_GPIO

    __parse_arg()
    __configure_logging()

    if __gpio_led is None:
        __gpio_led = __DEFAULT_GPIO

    stateMachinePanel.new(__gpio_led)
    stateMachinePanel.start(__gpio_led)

    # Give the path to the input video to process it
    # Otherwise it will use the Raspberry Pi camera
    ai.init(path_to_input_video=__video_path)
    ai.bicycle_detector(__gpio_led)

    stateMachinePanel.stop(__gpio_led)
    stateMachinePanel.free(__gpio_led)


if __name__ == "__main__":
    main()
