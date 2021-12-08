import logging
import sys

import toml
import clearway.gpio as gpio
from clearway.gpio import stateMachinePanel, servo
from clearway.ai import ai

# TODO Change argument name to correspond with dict key


USE_GPIO = "use_gpio"
PANEL_GPIOS = "panel_gpios"
INPUT_PATH = "input_path"
OUTPUT_PATH = "output_path"
YOLO_CFG_PATH = "yolo_cfg"
YOLO_WEIGHTS_PATH = "yolo_weights"
VERBOSITY_LEVEL = "verbosity_level"
CAMERA_ANGLE = "camera_angle"
SERVO_GPIO = "servo_gpio"
LOG_FORMAT = "log_format"
LOG_PATH = "log_path"


PROJECT_KEY_CONFIG = "clearway"

DEFAULT_PANEL_GPIOS = {5}
DEFAULT_SERVO_GPIO = 12  # GPIO 12 for PWM with 50Hz, pin 32
DEFAULT_SERVO_ANGLE = 75
DEFAULT_VERBOSITY_LEVEL = logging.getLevelName(logging.INFO)

__config_dict = {
    USE_GPIO: True,
    PANEL_GPIOS: DEFAULT_PANEL_GPIOS,
    INPUT_PATH: "",
    OUTPUT_PATH: "",
    YOLO_CFG_PATH: "yolo*.cfg",
    YOLO_WEIGHTS_PATH: "yolo*.weights",
    VERBOSITY_LEVEL: DEFAULT_VERBOSITY_LEVEL,
    CAMERA_ANGLE: DEFAULT_SERVO_ANGLE,
    SERVO_GPIO: DEFAULT_SERVO_GPIO,
    LOG_FORMAT: "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s",
    LOG_PATH: "ClearWay.log",
}


def __configure_logging(p_verbosity_level: str = DEFAULT_VERBOSITY_LEVEL) -> None:
    """Configure the app's logger.

    The log file is stored in `ClearWay.log` and every time the program
    restart, the file is cleared.
    Is format is:
        `Date Time FileName:FunctionName Level >> Message`
        example:
            `2021-10-28 18:20:19,018 foo.py:10 [INFO] >> Foo`

    The levels available are:
        - CRITICAL
        - ERROR
        - WARNING
        - INFO
        - DEBUG

    If `p_verbosity_level` does not have the expected format, then the verbosity level will be `INFO`

    Parameters
    ----------
    p_verbosity_level : `str`, optional
        The verbosity level to use, by default `DEFAULT_VERBOSITY_LEVEL`
    """
    global __config_dict

    l_verbosity_level = logging.INFO

    if p_verbosity_level == logging.getLevelName(logging.ERROR):
        l_verbosity_level = logging.CRITICAL
    elif p_verbosity_level == logging.getLevelName(logging.CRITICAL):
        l_verbosity_level = logging.CRITICAL
    elif p_verbosity_level == logging.getLevelName(logging.WARNING):
        l_verbosity_level = logging.WARNING
    elif p_verbosity_level == logging.getLevelName(logging.INFO):
        l_verbosity_level = logging.INFO
    elif p_verbosity_level == logging.getLevelName(logging.DEBUG):
        l_verbosity_level = logging.DEBUG

    logging.basicConfig(
        level=l_verbosity_level,
        format=__config_dict[LOG_FORMAT],
        handlers=[
            logging.FileHandler(__config_dict[LOG_PATH]),
            logging.StreamHandler(sys.stdout),
        ],
    )


def config_from_file(p_path: str) -> None:
    global __config_dict

    l_config_file = toml.load(p_path)[PROJECT_KEY_CONFIG]

    for l_key in l_config_file.keys():
        __config_dict[l_key] = l_config_file[l_key]


def save_config_gpio(p_use_gpio: int = None, p_gpios: int = None) -> None:
    global __config_dict

    if p_use_gpio is not None:
        __config_dict[USE_GPIO] = p_use_gpio

    if p_gpios is not None:
        __config_dict[PANEL_GPIOS] = p_gpios


def save_config_ai(
    p_input_video_path: str = None,
    p_output_video_path: str = None,
    p_yolo_cfg_path: str = None,
    p_yolo_weights_path: str = None,
) -> None:
    global __config_dict

    if p_input_video_path is not None:
        __config_dict[INPUT_PATH] = p_input_video_path

    if p_output_video_path is not None:
        __config_dict[OUTPUT_PATH] = p_output_video_path

    if p_yolo_cfg_path is not None:
        __config_dict[YOLO_CFG_PATH] = p_yolo_cfg_path

    if p_yolo_weights_path is not None:
        __config_dict[YOLO_WEIGHTS_PATH] = p_yolo_weights_path


def save_config_logging(p_verbosity_level: str = None):
    global __config_dict

    if p_verbosity_level is not None:
        __config_dict[VERBOSITY_LEVEL] = p_verbosity_level


def configure_all():
    global __config_dict

    # logging
    __configure_logging(__config_dict[VERBOSITY_LEVEL])

    # gpio
    gpio.use_gpio(__config_dict[USE_GPIO])
    # gpio.stateMachinePanel
    stateMachinePanel.config(__config_dict[PANEL_GPIOS])
    # gpio.servo
    servo.config(__config_dict[CAMERA_ANGLE], __config_dict[SERVO_GPIO])

    # TODO uncomment
    # ai.ai
    # ai.config(
    #     __config_dict[YOLO_WEIGHTS_PATH],
    #     __config_dict[YOLO_CFG_PATH],
    #     __config_dict[INPUT_PATH],
    #     __config_dict[OUTPUT_PATH],
    # )
