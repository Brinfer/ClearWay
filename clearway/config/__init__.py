"""Configure all modules.

To change the configuration of a module just use the associated function: `save_config_<module>`.
To apply the saved configuration, just call the `apply_config_<module>` function.

It is also possible to save a configuration from a TOML [1]_ file.

Notes
-----
.. [1] https://toml.io/en/
"""

import logging
import sys
from typing import Any, Dict, Iterable, Optional

import toml
import clearway.gpio as gpio
from clearway.ai import ai
from clearway.gpio import stateMachinePanel, servo

# TODO Change argument name to correspond with dict key


USE_GPIO = "use_gpio"
"""The dictionary key to indicate if you want to use GPIOs or not."""

PANEL_GPIOS = "panel_gpios"
"""The dictionary key to indicate the set of GPIOs to use for signaling."""

INPUT_PATH = "input_path"
"""The dictionary key to indicate the path to the input video."""

OUTPUT_PATH = "output_path"
"""The dictionary key to indicate the path to the output video."""

YOLO_CFG_PATH = "yolo_cfg"
"""The dictionary key to indicate the path to the YOLO configuration file."""

YOLO_WEIGHTS_PATH = "yolo_weights"
"""The dictionary key to indicate the path to the YOLO weights file."""

CAMERA_ANGLE = "camera_angle"
"""The dictionary key to indicate the angle of the camera to be used."""

SERVO_GPIO = "servo_gpio"
"""The dictionary key to indicate the GPIO to use for the servo-motor."""

LOG_VERBOSITY_LEVEL = "verbosity"
"""The dictionary key to indicate the verbosity level for the `logging` module."""

LOG_FORMAT = "log_format"
"""The dictionary key to indicate the format for the `logging` module."""

LOG_PATH = "log_path"
"""The dictionary key to indicate the path to the log file for the `logging` module."""


MAIN_SECTION = "clearway"
"""The main section searched in a toml file."""

SUBSECTION_GPIO = "gpio"
"""The subsection for the `gpio` module searched in the toml file."""

SUBSECTION_AI = "ai"
"""The subsection for the `ai` module searched in the toml file."""

SUBSECTION_LOG = "log"
"""The subsection for the `logging` module searched in the toml file."""

__config_dict: Dict[str, Dict[str, Any]] = {
    SUBSECTION_AI: {
        INPUT_PATH: "",
        YOLO_CFG_PATH: "",
        OUTPUT_PATH: "",
        YOLO_WEIGHTS_PATH: "",
    },
    SUBSECTION_GPIO: {
        USE_GPIO: True,
        PANEL_GPIOS: {5},
        SERVO_GPIO: 12,  # GPIO 12 for PWM with 50Hz, pin 32,
        CAMERA_ANGLE: 75,
    },
    SUBSECTION_LOG: {
        LOG_VERBOSITY_LEVEL: logging.INFO,
        LOG_FORMAT: "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s",
        LOG_PATH: "ClearWay.log",
    },
}
"""The dictionary containing all the current configuration."""


def save_config_from_file(p_path: str) -> None:
    """Save the config from the given config file.

    The configuration file must be in toml format. The section searched is `MAIN_SECTION`.
    If the section is not found, then nothing happens.

    If one of the subsection, or key does not match, then the process continues without taking into account the error.

    The toml file should respect the following format:

    ```toml
    [clearway]

    [clearway.gpio]
    use_gpio = false
    panel_gpios = [5, 6]
    camera_angle = 75
    servo_gpio = 12

    [clearway.ai]
    input_path = "input/video1.mp4"
    output_path = "output/video1.mp4"
    yolo_cfg = "yolo_cfg"
    yolo_weights = "yolo_weights"

    [clearway.log]
    verbosity = "DEBUG"
    ```

    Parameters
    ----------
    p_path : `str`
        The path to the config file.

    See
    ---
    - `save_config_gpio`
    - `save_config_ai`
    - `save_config_logging`
    """
    global __config_dict

    logging.info("[CONFIG] Load config from the file %s", p_path)

    l_config_file = toml.load(p_path)

    if MAIN_SECTION in l_config_file:
        l_clearway_config = l_config_file[MAIN_SECTION]
        del l_config_file  # No more needed

        for l_subsection in l_clearway_config.keys():
            if l_subsection in __config_dict:
                if l_subsection == SUBSECTION_GPIO:
                    save_config_gpio(p_dict=l_clearway_config[SUBSECTION_GPIO])
                elif l_subsection == SUBSECTION_AI:
                    save_config_ai(p_dict=l_clearway_config[SUBSECTION_AI])
                elif l_subsection == SUBSECTION_LOG:
                    save_config_logging(p_dict=l_clearway_config[SUBSECTION_LOG])


#
# logging
#


def save_config_logging(
    p_verbosity_level: str = None,
    p_dict: Optional[Dict[str, Any]] = None,
) -> None:
    """Save the configuration for `logging` module.

    If the argument is set to `None` then it will not be saved.

    It is possible to provide a dictionary containing all or part of the information, example:

    ```python
        {
            LOG_VERBOSITY_LEVEL: logging.INFO,
            LOG_FORMAT: "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s",
            LOG_PATH: "ClearWay.log",
        }
    ```

    Notes
    -----
    It is recommended to use the constants provided by the module, for the dictionary keys,
    `LOG_VERBOSITY_LEVEL`, `LOG_FORMAT` and `LOG_PATH` documentation.

    To have futher details on the available option see `apply_config_logging` function.

    Parameters
    ----------
    p_verbosity_level : `str`, optional
        The verbosity level to use, by default `None`
    p_dict : `Dict[str, Any]`, optional
        A dictionary containing the informations, by default `None`

    Raises
    ------
    ValueError
        The value of `p_verbosity_level` is unknown
    """
    global __config_dict

    # TODO accept format and path

    if p_dict is not None:
        if LOG_VERBOSITY_LEVEL in p_dict.keys():
            save_config_logging(p_verbosity_level=p_dict[LOG_VERBOSITY_LEVEL])

    if isinstance(p_verbosity_level, str):

        l_verbosity_level = logging.INFO
        if p_verbosity_level == logging.getLevelName(logging.ERROR):
            l_verbosity_level = logging.ERROR
        elif p_verbosity_level == logging.getLevelName(logging.CRITICAL):
            l_verbosity_level = logging.CRITICAL
        elif p_verbosity_level == logging.getLevelName(logging.WARNING):
            l_verbosity_level = logging.WARNING
        elif p_verbosity_level == logging.getLevelName(logging.INFO):
            l_verbosity_level = logging.INFO
        elif p_verbosity_level == logging.getLevelName(logging.DEBUG):
            l_verbosity_level = logging.DEBUG
        else:
            raise ValueError("[CONFIG] Unknown verbosity level: {}".format(p_verbosity_level))

        logging.debug("[CONFIG] Save a new verbosity level: %s", logging.getLevelName(l_verbosity_level))
        __config_dict[SUBSECTION_LOG][LOG_VERBOSITY_LEVEL] = l_verbosity_level


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

    logging.info("[CONFIG] Apply configuration for logging module")

    logging.basicConfig(
        level=__config_dict[SUBSECTION_LOG][LOG_VERBOSITY_LEVEL],
        format=__config_dict[SUBSECTION_LOG][LOG_FORMAT],
        handlers=[
            logging.FileHandler(__config_dict[SUBSECTION_LOG][LOG_PATH]),
            logging.StreamHandler(sys.stdout),
        ],
    )


#
# gpio
#


def save_config_gpio(
    p_use_gpio: Optional[bool] = None,
    p_gpios: Optional[Iterable[int]] = None,
    p_servo: Optional[int] = None,
    p_camera_angle: Optional[int] = None,
    p_dict: Optional[Dict[str, Any]] = None,
) -> None:
    """Save the configuration for `clearway.gpio` module.

    If the element is `None` or does not respect the expected type, then it will be ignored.

    It is possible to provide a dictionary containing all or part of the information, example:

    ```python
        {
            USE_GPIO: True,
            PANEL_GPIOS: {5, 6},
            SERVO_GPIO: 12,
            CAMERA_ANGLE: 75,
        }
    ```

    Notes
    -----
    It is recommended to use the constants provided by the module, for the dictionary keys,
    `USE_GPIO`, `PANEL_GPIOS`, `SERVO_GPIO` and `CAMERA_ANGLE` documentation.

    To have futher details on the available option see `apply_config_gpio` function.

    Parameters
    ----------
    p_use_gpio : `bool`, optional
        `True` if you want to use GPIOs, `False` otherwise, by default `None`
    p_gpios : `Iterable[int]`, optional
        GPIOs to use, by default `None`
    p_servo : `int`, optional
        The GPIO to use for the servo-motor, by default `None`
    p_camera_angle : `int`, optional
        The angle for the camera, by default `None`
    p_dict : `Dict[str, Any]`, optional
        A dictionary containing the informations, by default `None`
    """
    global __config_dict

    if p_dict is not None:
        if USE_GPIO in p_dict.keys():
            save_config_gpio(p_use_gpio=p_dict[USE_GPIO])

        if PANEL_GPIOS in p_dict.keys():
            save_config_gpio(p_gpios=p_dict[PANEL_GPIOS])

        if SERVO_GPIO in p_dict.keys():
            save_config_gpio(p_servo=p_dict[SERVO_GPIO])

        if CAMERA_ANGLE in p_dict.keys():
            save_config_gpio(p_camera_angle=p_dict[CAMERA_ANGLE])

    if isinstance(p_use_gpio, bool):
        logging.debug("[CONFIG] Save new instruction for the use of the GPIOs: {}".format(p_use_gpio))
        __config_dict[SUBSECTION_GPIO][USE_GPIO] = p_use_gpio

    if (
        isinstance(p_gpios, Iterable)
        and any(isinstance(l_gpio, int) for l_gpio in p_gpios)
        and any((int(l_gpio) > 0) for l_gpio in p_gpios)
    ):
        logging.debug("[CONFIG] Save new GPIOs to use: %s", ", ".join([str(i) for i in p_gpios]))
        __config_dict[SUBSECTION_GPIO][PANEL_GPIOS] = p_gpios

    if isinstance(p_servo, int):
        logging.debug("[CONFIG] Save new GPIO for the servo-motors to use: %d", p_servo)
        __config_dict[SUBSECTION_GPIO][SERVO_GPIO] = p_servo

    if isinstance(p_camera_angle, int):
        logging.debug("[CONFIG] Save new GPIO for the servo-motors to use: %d", p_camera_angle)
        __config_dict[SUBSECTION_GPIO][CAMERA_ANGLE] = p_camera_angle


def apply_config_gpio() -> None:
    """Configure the `clearway.gpio` module.

    Configures:
    - whether the program uses GPIOs or not.
    - what are the GPIOs to use for signaling.
    - which GPIO to use for the servo motor.

    All these values are the ones provided when using `save_config_gpio`, otherwise the default values will be used.
    """
    logging.info("[CONFIG] Apply configuration for gpio module")

    # gpio
    gpio.use_gpio(__config_dict[SUBSECTION_GPIO][USE_GPIO])
    # gpio.stateMachinePanel
    stateMachinePanel.config(__config_dict[SUBSECTION_GPIO][PANEL_GPIOS])
    # gpio.servo
    servo.config(__config_dict[SUBSECTION_GPIO][CAMERA_ANGLE], __config_dict[SUBSECTION_GPIO][SERVO_GPIO])


#
# ai
#


def save_config_ai(
    p_input_video_path: Optional[str] = None,
    p_output_video_path: Optional[str] = None,
    p_yolo_cfg_path: Optional[str] = None,
    p_yolo_weights_path: Optional[str] = None,
    p_dict: Optional[Dict[str, Any]] = None,
) -> None:
    """Save the configuration for `clearway.ai` module.

    If the element is `None` or does not respect the expected type, then it will be ignored.

    It is possible to provide a dictionary containing all or part of the information, example:

    ```python
        {
            INPUT_PATH: "path/to/my/video.mp4",
            OUTPUT_PATH: "path/to/my/videoOutput.mp4",
            YOLO_CFG_PATH: "path/to/my/yolo.cfg",
            YOLO_WEIGHTS_PATH: "path/to/my/yolo.weights",
        }
    ```

    Notes
    -----
    It is recommended to use the constants provided by the module, for the dictionary keys,
    `INPUT_PATH`, `YOLO_CFG_PATH`, `OUTPUT_PATH` and `YOLO_WEIGHTS_PATH` documentation.

    To have futher details on the available option see `apply_config_ai` function.

    Parameters
    ----------
    p_input_video_path : str, optional
        The path to the video to be analyzed, by default `None`
    p_output_video_path : str, optional
        The path to the file where the video analysis result is saved, by default `None`
    p_yolo_cfg_path : str, optional
        The path to the file containing the YOLO configuration, by default `None`
    p_yolo_weights_path : str, optional
        The path to the file containing the YOLO weights, by default `None`
    p_dict : `Dict[str, Any]`, optional
        A dictionary containing the informations, by default `None`
    """
    global __config_dict

    logging.debug(p_dict)

    if p_dict is not None:
        if INPUT_PATH in p_dict.keys():
            save_config_ai(p_input_video_path=p_dict[INPUT_PATH])

        if OUTPUT_PATH in p_dict.keys():
            save_config_ai(p_output_video_path=p_dict[OUTPUT_PATH])

        if YOLO_CFG_PATH in p_dict.keys():
            save_config_ai(p_yolo_cfg_path=p_dict[YOLO_CFG_PATH])

        if YOLO_WEIGHTS_PATH in p_dict.keys():
            save_config_ai(p_yolo_weights_path=p_dict[YOLO_WEIGHTS_PATH])

    if isinstance(p_input_video_path, str):
        __config_dict[SUBSECTION_AI][INPUT_PATH] = p_input_video_path

    if isinstance(p_output_video_path, str):
        __config_dict[SUBSECTION_AI][OUTPUT_PATH] = p_output_video_path

    if isinstance(p_yolo_cfg_path, str):
        __config_dict[SUBSECTION_AI][YOLO_CFG_PATH] = p_yolo_cfg_path

    if isinstance(p_yolo_weights_path, str):
        __config_dict[SUBSECTION_AI][YOLO_WEIGHTS_PATH] = p_yolo_weights_path


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
    logging.info("[CONFIG] Apply configuration for ai module")

    logging.debug(__config_dict[SUBSECTION_AI])
    # ai.ai
    ai.config(
        __config_dict[SUBSECTION_AI][YOLO_WEIGHTS_PATH],
        __config_dict[SUBSECTION_AI][YOLO_CFG_PATH],
        __config_dict[SUBSECTION_AI][INPUT_PATH],
        __config_dict[SUBSECTION_AI][OUTPUT_PATH],
    )


def apply_config_all() -> None:
    """Configure all modules.

    Calls all methods `apply_config_<module>`.

    See
    ---
    - `apply_config_logging`
    - `apply_config_gpio`
    - `apply_config_ai`
    """
    apply_config_logging()
    apply_config_gpio()
    apply_config_ai()
