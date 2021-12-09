"""Configure all modules.

To change the configuration of a module just use the associated function: `save_config_<module>`.
To apply the saved configuration, just call the `apply_config_<module>` function.

It is also possible to apply a configuration from a TOML [1]_ file.

Notes
-----
.. [1] https://toml.io/en/
"""

import logging
import sys

import toml
import clearway.gpio as gpio
from clearway.ai import ai

# TODO Change argument name to correspond with dict key


USE_GPIO = "use_gpio"
PANEL_GPIOS = "panel_gpios"
INPUT_PATH = "input_path"
OUTPUT_PATH = "output_path"
YOLO_CFG_PATH = "yolo_cfg"
YOLO_WEIGHTS_PATH = "yolo_weights"
LOG_VERBOSITY_LEVEL = "verbosity"
CAMERA_ANGLE = "camera_angle"
SERVO_GPIO = "servo_gpio"
LOG_FORMAT = "log_format"
LOG_PATH = "log_path"


PROJECT_KEY_CONFIG = "clearway"

DEFAULT_PANEL_GPIOS = {5}
DEFAULT_SERVO_GPIO = 12  # GPIO 12 for PWM with 50Hz, pin 32
DEFAULT_SERVO_ANGLE = 75
DEFAULT_LOG_VERBOSITY_LEVEL = logging.getLevelName(logging.INFO)
DEFAULT_LOG_PATH = "ClearWay.log"
DEFAULT_LOG_FORMAT = "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s"

__config_dict = {
    USE_GPIO: True,
    PANEL_GPIOS: DEFAULT_PANEL_GPIOS,
    INPUT_PATH: "",
    OUTPUT_PATH: "",
    YOLO_CFG_PATH: "",
    YOLO_WEIGHTS_PATH: "",
    LOG_VERBOSITY_LEVEL: DEFAULT_LOG_VERBOSITY_LEVEL,
    CAMERA_ANGLE: DEFAULT_SERVO_ANGLE,
    SERVO_GPIO: DEFAULT_SERVO_GPIO,
    LOG_FORMAT: DEFAULT_LOG_FORMAT,
    LOG_PATH: DEFAULT_LOG_PATH,
}


def save_config_from_file(p_path: str) -> None:
    """Save the config from the given config file.

    The configuration file must be in toml format. The section searched is `PROJECT_KEY_CONFIG`.
    If the section is not found, then nothing happens.

    The keys used are:
        - use_gpio
        - panel_gpios
        - input_path
        - output_path
        - yolo_cfg
        - yolo_weights
        - verbosity
        - camera_angle
        - servo_gpio
        - log_format
        - log_path

    Keys that do not match are simply unused.

    Parameters
    ----------
    p_path : `str`
        The path to the config file.
    """
    global __config_dict

    l_config_file = toml.load(p_path)

    if PROJECT_KEY_CONFIG in l_config_file:
        for l_key in l_config_file[PROJECT_KEY_CONFIG].keys():
            __config_dict[l_key] = l_config_file[l_key]


#
# logging
#


def save_config_logging(p_verbosity_level: str = None):
    """Save the configuration for `logging` module.

    If the argument is set to `None` then it will not be saved.

    Parameters
    ----------
    p_verbosity_level : str, optional
        The verbosity level to use, by default None
    """
    global __config_dict

    if p_verbosity_level is not None:
        __config_dict[LOG_VERBOSITY_LEVEL] = p_verbosity_level


def apply_config_logging() -> None:
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
    global __config_dict

    l_verbosity_level = logging.INFO

    if __config_dict[LOG_VERBOSITY_LEVEL] == logging.getLevelName(logging.ERROR):
        l_verbosity_level = logging.CRITICAL
    elif __config_dict[LOG_VERBOSITY_LEVEL] == logging.getLevelName(logging.CRITICAL):
        l_verbosity_level = logging.CRITICAL
    elif __config_dict[LOG_VERBOSITY_LEVEL] == logging.getLevelName(logging.WARNING):
        l_verbosity_level = logging.WARNING
    elif __config_dict[LOG_VERBOSITY_LEVEL] == logging.getLevelName(logging.INFO):
        l_verbosity_level = logging.INFO
    elif __config_dict[LOG_VERBOSITY_LEVEL] == logging.getLevelName(logging.DEBUG):
        l_verbosity_level = logging.DEBUG

    logging.basicConfig(
        level=l_verbosity_level,
        format=__config_dict[LOG_FORMAT],
        handlers=[
            logging.FileHandler(__config_dict[LOG_PATH]),
            logging.StreamHandler(sys.stdout),
        ],
    )


#
# gpio
#


def save_config_gpio(p_use_gpio: bool = None, p_gpios: int = None) -> None:
    """Save the configuration for `clearway.gpio` module.

    If the argument is set to `None` then it will not be saved.

    Parameters
    ----------
    p_use_gpio : `bool`, optional
        `True` if you want to use GPIOs, `False` otherwise, by default None
    p_gpios : `int`, optional
        GPIOs to use, by default None
    """
    global __config_dict

    if p_use_gpio is not None:
        __config_dict[USE_GPIO] = p_use_gpio

    if p_gpios is not None:
        __config_dict[PANEL_GPIOS] = p_gpios


def apply_config_gpio() -> None:
    """Configure the `clearway.gpio` module.

    Configures:
    - whether the program uses GPIOs or not.
    - what are the GPIOs to use for signaling.
    - which GPIO to use for the servo motor.

    All these values are the ones provided when using `save_config_gpio`, otherwise the default values will be used
    """
    # gpio
    gpio.use_gpio(__config_dict[USE_GPIO])
    # gpio.stateMachinePanel
    gpio.stateMachinePanel.config(__config_dict[PANEL_GPIOS])
    # gpio.servo
    gpio.servo.config(__config_dict[CAMERA_ANGLE], __config_dict[SERVO_GPIO])


#
# ai
#


def save_config_ai(
    p_input_video_path: str = None,
    p_output_video_path: str = None,
    p_yolo_cfg_path: str = None,
    p_yolo_weights_path: str = None,
) -> None:
    """Save the configuration for `clearway.ai` module.

    If the argument is set to `None` then it will not be saved.

    Parameters
    ----------
    p_input_video_path : str, optional
        The path to the video to be analyzed, by default None
    p_output_video_path : str, optional
        The path to the file where the video analysis result is saved, by default None
    p_yolo_cfg_path : str, optional
        The path to the file containing the YOLO configuration, by default None
    p_yolo_weights_path : str, optional
        The path to the file containing the YOLO weights, by default None
    """
    global __config_dict

    if p_input_video_path is not None:
        __config_dict[INPUT_PATH] = p_input_video_path

    if p_output_video_path is not None:
        __config_dict[OUTPUT_PATH] = p_output_video_path

    if p_yolo_cfg_path is not None:
        __config_dict[YOLO_CFG_PATH] = p_yolo_cfg_path

    if p_yolo_weights_path is not None:
        __config_dict[YOLO_WEIGHTS_PATH] = p_yolo_weights_path


def apply_config_ai() -> None:
    """Configure the `clearway.ai` module.

    Configures:
    - the path to the YOLO weights file
    - the path to the YOLO config file
    - the path to the input video file
    - the path to the output video file

    All these values are the ones provided when using `save_config_ai`,
    otherwise the default values provided by the module will be used
    """
    ai.ai
    ai.config(
        __config_dict[YOLO_WEIGHTS_PATH],
        __config_dict[YOLO_CFG_PATH],
        __config_dict[INPUT_PATH],
        __config_dict[OUTPUT_PATH],
    )


def apply_config_all() -> None:
    """Configure all modules.

    Calls all methods `apply_config_<module>`.
    """
    apply_config_logging()
    apply_config_gpio()
    apply_config_ai()
