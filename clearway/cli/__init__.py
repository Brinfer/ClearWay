"""Command-line implementation of ClearWay."""

import logging
import sys
import argparse
import signal
import types

import clearway
import clearway.gpio as gpio
from clearway.gpio import stateMachinePanel
from clearway.gpio import servo
from clearway.ai import ai

__LOG_FORMAT = "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s"
__DEFAULT_GPIO = 5
__DEFAULT_VERBOSITY_LEVEL = logging.INFO
__LOG_PATH = "ClearWay.log"

__gpio_led = None
__input_video_path = None
__output_video_path = None
__yolo_cfg = ""
__yolo_weights = ""
__verbosity_level = None

# Angle of the camera
_camera_angle = 75
_servo_pin = 12


def __signal_handler(p_signum: int, _p_stack_frame: types.FrameType) -> None:
    """Signal handler.

    When is called, then all state machines are stopped and destroyed

    Parameters
    ----------
    p_signum : `int`
        The number of the signal calling the function
    _p_stack_frame : `FrameType`
        the frame that was interrupted by the signal.
    """
    logging.warning("[CLI] Intercept signal {}".format(signal.Signals(p_signum).name))

    # Stop all state machine
    stateMachinePanel.stop_all()

    # Free all state machine
    stateMachinePanel.free_all()

    sys.exit(0)


def __signal_handler(p_signum: int, _p_stack_frame: types.FrameType) -> None:
    """Signal handler.

    When is called, then all state machines are stopped and destroyed

    Parameters
    ----------
    p_signum : `int`
        The number of the signal calling the function
    _p_stack_frame : `FrameType`
        the frame that was interrupted by the signal.
    """
    logging.warning("[CLI] Intercept signal {}".format(signal.Signals(p_signum).name))

    # Stop all state machine
    stateMachinePanel.stop_all()

    # Free all state machine
    stateMachinePanel.free_all()

    sys.exit(0)


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
        --gpio GPIO
            tells the program which gpio to use, the default is __DEFAULT_GPIO
        --no-gpio
            tells the program that it does not want to use the GPIOs, only the logs will be displayed
        -i INPUT_PATH, --input-path INPUT_PATH
            the path to the input video to be analyzed rather than using the video stream from the camera
        -o OUTPUT_PATH, --output-path OUTPUT_PATH
            the path to the folder that will contain the output video with boxes around detected bicycles
        -v {WARNING,INFO,DEBUG}, --verbosity {WARNING,INFO,DEBUG}
            indicates the level of verbosity, default is __DEFAULT_VERBOSITY_LEVEL
        -V, --version
            print the ClearWay version and exit

    The required arguments are:
        --yolo-weights YOLO_WEIGHTS
            the path to the weights file of yolo
        --yolo-cfg YOLO_CFG
            the path to the configuration file of yolo
    """
    global __gpio_led, __input_video_path, __output_video_path, __yolo_cfg, __yolo_weights
    global __verbosity_level, __DEFAULT_GPIO

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
        "-i",
        "--input-path",
        help="the path to the input video to be analyzed rather than using the video stream from the camera",
        action="store",
        default=None,
    )

    l_parser.add_argument(
        "-o",
        "--output-path",
        help="the path to the folder that will contain the output video with boxes around detected bicycles",
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

    required_arguments = l_parser.add_argument_group("required arguments")

    required_arguments.add_argument(
        "--yolo-weights",
        help="the path to the weights file of yolo",
        action="store",
        default=None,
        required=True,
    )

    required_arguments.add_argument(
        "--yolo-cfg",
        help="the path to the configuration file of yolo",
        action="store",
        default=None,
        required=True,
    )

    l_args = l_parser.parse_args()

    gpio.use_gpio(not l_args.no_gpio)
    __gpio_led = l_args.gpio
    __input_video_path = l_args.input_path
    __output_video_path = l_args.output_path
    __yolo_cfg = l_args.yolo_cfg
    __yolo_weights = l_args.yolo_weights

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

    # Add signal handler
    signal.signal(signal.SIGINT, __signal_handler)  # Interrupt from keyboard (CTRL + C)
    signal.signal(signal.SIGTERM, __signal_handler)  # Termination signal

    if __gpio_led is None:
        __gpio_led = __DEFAULT_GPIO

    servo.servo_init(_camera_angle, _servo_pin)

    stateMachinePanel.new(__gpio_led)
    stateMachinePanel.start(__gpio_led)

    # Give the path to the input video to process it
    # Otherwise it will use the Raspberry Pi camera
    ai.init(__yolo_weights, __yolo_cfg, __input_video_path, __output_video_path)
    ai.bicycle_detector(__gpio_led)

    stateMachinePanel.stop(__gpio_led)
    stateMachinePanel.free(__gpio_led)


if __name__ == "__main__":
    main()
