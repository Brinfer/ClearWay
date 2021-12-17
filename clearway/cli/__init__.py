"""Command-line implementation of ClearWay."""

import logging
import argparse
import sys
import signal
import types
from typing import Optional

import clearway
import clearway.config as config
import clearway.gpio as gpio
from clearway.gpio import stateMachinePanel, servo
from clearway.ai import ai

VERSION_MESAGE: str = """
   ________               _       __
  / ____/ /__  ____ _____| |     / /___ ___  __
 / /   / / _ \\/ __ `/ ___/ | /| / / __ `/ / / /
/ /___/ /  __/ /_/ / /   | |/ |/ / /_/ / /_/ /
\\____/_/\\___/\\__,_/_/    |__/|__/\\__,_/\\__, /
                                      /____/

ClearWay v{}
Copyright (C) 2021-2022 {}

This program may be freely redistributed under the terms of the {} license.
""".format(
    clearway.__version__, clearway.__author__, clearway.__license__
)
"""The message displayed when using the `clearway --version` command."""


def __signal_handler(p_signum: int, _p_stack_frame: Optional[types.FrameType] = None) -> None:
    """Signal handler.

    When is called, then all state machines are stopped and destroyed.

    Parameters
    ----------
    p_signum : `int`
        The number of the signal calling the function.
    _p_stack_frame : `FrameType`, optional
        the frame that was interrupted by the signal, by default `None`.
    """
    logging.warning("[CLI] Intercept signal {}".format(signal.Signals(p_signum).name))

    # Stop all state machine
    stateMachinePanel.stop()

    # Free all state machine
    stateMachinePanel.free()

    sys.exit(0)


def __parse_arg() -> None:
    """Parse the arguments passed in parameter at the launching of the program.

    After parsing all the options, they are saved for the different modules.

    ```text
    optional arguments:
        -h, --help            show this help message and exit
        --panel_gpios PANEL_GPIOS
                              tells the program which gpio to use
        --no-gpio             tells the program to not use the GPIOs, only the logs will be displayed
        --use-gpio            tells the program to use the GPIOs
        --on-raspberry        tells the program if we are using a raspberry or a computer
        --see-rtp             tells the program if we want to see a window with the real-time processing in it
        -i INPUT_PATH, --input-path INPUT_PATH
                              the path to the input video to be analyzed rather than using the video stream from
                              the camera
        -o OUTPUT_PATH, --output-path OUTPUT_PATH
                              the path to the folder that will contain the output video with boxes around detected
                              bicycles
        -v {WARNING,INFO,DEBUG}, --verbosity {WARNING,INFO,DEBUG}
                              indicates the level of verbosity
        -V, --version         print the ClearWay version and exit

        required arguments:
        --yolo-weights YOLO_WEIGHTS
                              the path to the weights file of yolo, required if the --config argument is not
                              provided.
                              The configuration file must then contain the path to the yolo file
        --yolo-cfg YOLO_CFG   the path to the configuration file of yolo, required if the argument --config is not
                              provided.
                              The configuration file must then contain the path to the yolo file.
        -c CONFIG, --config CONFIG
                              the path to the config file, required if the arguments --yolo-cfg and --yolo-weights are
                              not provided.
                              All parameters contained in the configuration file can be overloaded with optional
                              arguments.
        --size SIZE           the size of the images converted to blob (320 or 416 recommended), required if the
                              argument --config is not provided.
                              The configuration file must then contain the size of the image.
        ```
    """

    def arguments_is_given(*p_args: str) -> bool:
        """Test if the arguments are passed at program startup.

        It is possible to pass one or more character strings.

        Returns
        -------
        bool
            `True` if one the arguments are present, `False` false if none is present.
        """
        return len(set(p_args) & set(sys.argv)) > 0

    l_parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        usage="clearway [OPTIONS] --yolo-cfg YOLO_CFG --yolo-weights YOLO_WEIGHTS --config CONFIG",
    )

    # Optionals arguments

    l_parser.add_argument(
        "--panel-gpios",
        help="tells the program which gpio to use",
        nargs="+",
        action="store",
        type=int,
        default=None,
    )

    l_group_gpio = l_parser.add_mutually_exclusive_group()
    l_group_gpio.add_argument(
        "--no-gpio",
        help="tells the program to not use the GPIOs, only the logs will be displayed",
        dest="use_gpio",
        action="store_false",
        default=None,
    )
    l_group_gpio.add_argument(
        "--use-gpio",
        help="tells the program to use the GPIOs",
        action="store_true",
        default=None,
    )

    l_parser.add_argument(
        "--on-raspberry",
        help="tells the program if we are using a raspberry or a computer",
        action="store_true",
        default=None,
    )

    l_parser.add_argument(
        "--see-rtp",
        help="tells the program if we want to see a window with the real-time processing in it",
        action="store_true",
        default=None,
    )

    l_parser.add_argument(
        "-i",
        "--input-path",
        help="the path to the input video to be analyzed rather than using the video stream from the camera",
        action="store",
        type=str,
        default=None,
    )

    l_parser.add_argument(
        "-o",
        "--output-path",
        help="the path to the folder that will contain the output video with boxes around detected bicycles",
        action="store",
        type=str,
        default=None,
    )

    l_parser.add_argument(
        "-v",
        "--verbosity",
        choices=[
            logging.getLevelName(logging.WARNING),
            logging.getLevelName(logging.INFO),
            logging.getLevelName(logging.DEBUG),
        ],
        help="indicates the level of verbosity",
        type=str,
        default=None,
    )

    l_parser.add_argument(
        "-V",
        "--version",
        help="print the {} version and exit".format(clearway.__project__),
        action="version",
        version=VERSION_MESAGE,
    )

    # Required arguments

    l_group_required = l_parser.add_argument_group("required arguments")

    l_group_required.add_argument(
        "--yolo-weights",
        help="""the path to the weights file of yolo, required if the --config argument is not provided.
The configuration file must then contain the path to the yolo file""",
        action="store",
        default=None,
        type=str,
        required=not arguments_is_given("--config", "-c"),
    )

    l_group_required.add_argument(
        "--yolo-cfg",
        help="""the path to the configuration file of yolo, required if the argument --config is not provided.
The configuration file must then contain the path to the yolo file.""",
        action="store",
        type=str,
        default=None,
        required=not arguments_is_given("--config", "-c"),
    )

    l_group_required.add_argument(
        "-c",
        "--config",
        help="""the path to the config file, required if the arguments --yolo-cfg and --yolo-weights are not provided.
All parameters contained in the configuration file can be overloaded with optional arguments.""",
        action="store",
        type=str,
        default=None,
        required=not (arguments_is_given("--yolo-cfg") and arguments_is_given("--yolo-weights")),
    )

    l_group_required.add_argument(
        "--size",
        type=int,
        help="""the size of the images converted to blob (320 or 416 recommended), required if the argument --config is not provided.
The configuration file must then contain the size of the image""",
        action="store",
        default=None,
        required=not arguments_is_given("--config", "-c"),
    )

    # Parse the arguments
    l_args = l_parser.parse_args()

    # Configure the modules

    # Load config file
    if l_args.config is not None:
        config.save_config_from_file(l_args.config)

    # Overload config file with argument

    print(l_args.panel_gpios)
    print(type(l_args.panel_gpios))
    print(type(l_args.panel_gpios[0]))

    # Save GPIO config module
    config.save_config_gpio(p_use_gpio=l_args.use_gpio, p_gpios=l_args.panel_gpios)

    # Save AI config module
    config.save_config_ai(
        p_input_video_path=l_args.input_path,
        p_output_video_path=l_args.output_path,
        p_yolo_cfg_path=l_args.yolo_cfg,
        p_yolo_weights_path=l_args.yolo_weights,
        p_size=l_args.size,
        p_on_raspberry=l_args.on_raspberry,
        p_real_time_processing=l_args.see_rtp,
    )

    # Save logging config module
    config.save_config_logging(p_verbosity_level=l_args.verbosity)


def __apply_config_logging() -> None:
    """Configure the `logging` module.

    The log file is stored in `DEFAULT_LOG_PATH` and every time the program
    restart, the file is cleared.
    Is format is:
        `Date Time FileName:FunctionName Level >> Message`
        example:
            `2021-10-28 18:20:19,018 [foo.py:10] INFO >> Foo`

    The levels available are:
        - CRITICAL
        - ERROR
        - WARNING
        - INFO
        - DEBUG

    All these values are the ones provided when using `save_config_logging`,
    otherwise the default values provided by the module will be used
    """
    logging.basicConfig(
        level=config.get_config(config.MODULE_LOGGING, config.LOG_VERBOSITY_LEVEL),
        format=config.get_config(config.MODULE_LOGGING, config.LOG_FORMAT),
        handlers=[
            logging.FileHandler(config.get_config(config.MODULE_LOGGING, config.LOG_PATH)),
            logging.StreamHandler(sys.stdout),
        ],
    )


def main() -> None:
    """Program input function."""
    __parse_arg()
    __apply_config_logging()

    # Add signal handler
    signal.signal(signal.SIGINT, __signal_handler)  # Interrupt from keyboard (CTRL + C)
    signal.signal(signal.SIGTERM, __signal_handler)  # Termination signal

    gpio.use_gpio(config.get_config(config.MODULE_GPIO, config.USE_GPIO))
    servo.set_angle()

    stateMachinePanel.new(config.get_config(config.MODULE_GPIO, config.PANEL_GPIOS))
    stateMachinePanel.start()

    # Give the path to the input video to process it
    # Otherwise it will use the Raspberry Pi camera
    ai_instance = ai.Ai(
        config.get_config(config.MODULE_AI, config.ON_RASPBERRY),
        config.get_config(config.MODULE_AI, config.SEE_REAL_TIME_PROCESS),
        config.get_config(config.MODULE_AI, config.YOLO_WEIGHTS_PATH),
        config.get_config(config.MODULE_AI, config.YOLO_CFG_PATH),
        config.get_config(config.MODULE_AI, config.IMG_SIZE),
        config.get_config(config.MODULE_AI, config.INPUT_PATH),
        config.get_config(config.MODULE_AI, config.OUTPUT_PATH),
    )

    ai_instance.bicycle_detector(config.get_config(config.MODULE_GPIO, config.PANEL_GPIOS))

    stateMachinePanel.stop()
    stateMachinePanel.free()


if __name__ == "__main__":
    main()
