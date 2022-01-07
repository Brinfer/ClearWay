"""Configure all modules.

To change the configuration of a module just use the associated function: `save_config_<module>`.
To apply the saved configuration, just call the `apply_config_<module>` function.

It is also possible to save a configuration from a TOML [1]_ file.

Notes
-----
.. [1] https://toml.io/en/
"""

import logging
from typing import Any, Dict, Iterable, Optional

import toml


# For the gpio module

USE_GPIO = "use_gpio"
"""The dictionary key to indicate if you want to use GPIOs or not."""

PANEL_GPIOS = "panel_gpios"
"""The dictionary key to indicate the set of GPIOs to use for signaling."""

CAMERA_ANGLE = "camera_angle"
"""The dictionary key to indicate the angle of the camera to be used."""

SERVO_GPIO = "servo_gpio"
"""The dictionary key to indicate the GPIO to use for the servo-motor."""

# For the ai module

INPUT_PATH = "input_path"
"""The dictionary key to indicate the path to the input video."""

OUTPUT_PATH = "output_path"
"""The dictionary key to indicate the path to the output video."""

YOLO_CFG_PATH = "yolo_cfg"
"""The dictionary key to indicate the path to the YOLO configuration file."""

YOLO_WEIGHTS_PATH = "yolo_weights"
"""The dictionary key to indicate the path to the YOLO weights file."""

ON_RASPBERRY = "on_raspberry"
"""The dictionary key to indicate the if we are using a raspberry or a computer."""

IMG_SIZE = "size"
"""The dictionary key to indicate the size of the images converted to blob."""

SEE_REAL_TIME_PROCESS = "see_rtp"
"""The dictionary key to indicate if we want to see a window with the real-time processing in it."""

# For the logging module

LOG_VERBOSITY_LEVEL = "verbosity"
"""The dictionary key to indicate the verbosity level for the `logging` module."""

LOG_FORMAT = "format"
"""The dictionary key to indicate the format for the `logging` module."""

LOG_PATH = "path"
"""The dictionary key to indicate the path to the log file for the `logging` module."""

# List au module

MAIN_SECTION = "clearway"
"""The main section searched in a toml file."""

MODULE_GPIO = "gpio"
"""The subsection for the `gpio` module searched in the configuration."""

MODULE_AI = "ai"
"""The subsection for the `ai` module searched in the configuration."""

MODULE_LOGGING = "log"
"""The subsection for the `logging` module searched in the configuration."""

__config_dict: Dict[str, Dict[str, Any]] = {
    MODULE_AI: {
        INPUT_PATH: None,
        YOLO_CFG_PATH: "",
        OUTPUT_PATH: None,
        YOLO_WEIGHTS_PATH: "",
        ON_RASPBERRY: False,
        IMG_SIZE: 320,
        SEE_REAL_TIME_PROCESS: False,
    },
    MODULE_GPIO: {
        USE_GPIO: True,
        PANEL_GPIOS: {5},
        SERVO_GPIO: 12,  # GPIO 12 for PWM with 50Hz, pin 32,
        CAMERA_ANGLE: 75,
    },
    MODULE_LOGGING: {
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
    yolo_cfg = "resources/yolov2-tiny.cfg"
    yolo_weights = "resources/yolov2-tiny.weights"
    on_raspberry = false
    size = 320
    see_rtp = false

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

    l_config_file = toml.load(p_path)

    if MAIN_SECTION in l_config_file:
        l_clearway_config = l_config_file[MAIN_SECTION]
        del l_config_file  # No more needed

        for l_subsection in l_clearway_config.keys():
            if l_subsection in __config_dict:
                if l_subsection == MODULE_GPIO:
                    save_config_gpio(p_dict=l_clearway_config[MODULE_GPIO])
                elif l_subsection == MODULE_AI:
                    save_config_ai(p_dict=l_clearway_config[MODULE_AI])
                elif l_subsection == MODULE_LOGGING:
                    save_config_logging(p_dict=l_clearway_config[MODULE_LOGGING])


#
# logging
#


def save_config_logging(
    p_verbosity_level: Optional[str] = None,
    p_format: Optional[str] = None,
    p_path: Optional[str] = None,
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
    p_format : `str`, optional
        The log format, by default `None`
    p_path : `str`, optional
        The path to the log file, by default `None`
    p_dict : `Dict[str, Any]`, optional
        A dictionary containing the information, by default `None`

    Raises
    ------
    ValueError
        The value of `p_verbosity_level` is unknown
    """
    global __config_dict

    # TODO accept format and path
    def recursive_call(p_dict: Dict[str, Any]) -> None:
        if LOG_VERBOSITY_LEVEL in p_dict.keys():
            save_config_logging(p_verbosity_level=p_dict[LOG_VERBOSITY_LEVEL])

        if LOG_FORMAT in p_dict.keys():
            save_config_logging(p_format=p_dict[LOG_FORMAT])

        if LOG_PATH in p_dict.keys():
            save_config_logging(p_path=p_dict[LOG_PATH])

    if p_dict is not None:
        recursive_call(p_dict)

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

        __config_dict[MODULE_LOGGING][LOG_VERBOSITY_LEVEL] = l_verbosity_level

    if isinstance(p_format, str):
        __config_dict[MODULE_LOGGING][LOG_FORMAT] = p_format

    if isinstance(p_path, str):
        __config_dict[MODULE_LOGGING][LOG_PATH] = p_path


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
        A dictionary containing the information, by default `None`
    """
    global __config_dict

    def recursive_call(p_dict: Dict[str, Any]) -> None:
        if USE_GPIO in p_dict.keys():
            save_config_gpio(p_use_gpio=p_dict[USE_GPIO])

        if PANEL_GPIOS in p_dict.keys():
            save_config_gpio(p_gpios=p_dict[PANEL_GPIOS])

        if SERVO_GPIO in p_dict.keys():
            save_config_gpio(p_servo=p_dict[SERVO_GPIO])

        if CAMERA_ANGLE in p_dict.keys():
            save_config_gpio(p_camera_angle=p_dict[CAMERA_ANGLE])

    if p_dict is not None:
        recursive_call(p_dict)

    if isinstance(p_use_gpio, bool):
        __config_dict[MODULE_GPIO][USE_GPIO] = p_use_gpio

    if (
        isinstance(p_gpios, Iterable)
        and any(isinstance(l_gpio, int) for l_gpio in p_gpios)
        and any((int(l_gpio) > 0) for l_gpio in p_gpios)
    ):
        __config_dict[MODULE_GPIO][PANEL_GPIOS] = p_gpios

    if isinstance(p_servo, int):
        __config_dict[MODULE_GPIO][SERVO_GPIO] = p_servo

    if isinstance(p_camera_angle, int):
        __config_dict[MODULE_GPIO][CAMERA_ANGLE] = p_camera_angle


#
# ai
#


def save_config_ai(
    p_input_video_path: Optional[str] = None,
    p_output_video_path: Optional[str] = None,
    p_yolo_cfg_path: Optional[str] = None,
    p_yolo_weights_path: Optional[str] = None,
    p_size: Optional[int] = None,
    p_on_raspberry: Optional[bool] = None,
    p_real_time_processing: Optional[bool] = None,
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
            ON_RASPBERRY: False,
            IMG_SIZE: 320,
            SEE_REAL_TIME_PROCESS: False,
        }
    ```

    Notes
    -----
    It is recommended to use the constants provided by the module, for the dictionary keys,
    `INPUT_PATH`, `YOLO_CFG_PATH`, `OUTPUT_PATH` and `YOLO_WEIGHTS_PATH` documentation.

    To have futher details on the available option see `apply_config_ai` function.

    Parameters
    ----------
    p_input_video_path : `str`, optional
        The path to the video to be analyzed, by default `None`.
    p_output_video_path : `str`, optional
        The path to the file where the video analysis result is saved, by default `None`.
    p_yolo_cfg_path : `str`, optional
        The path to the file containing the YOLO configuration, by default `None`.
    p_yolo_weights_path : `str`, optional
        The path to the file containing the YOLO weights, by default `None`.
    p_size : `int`, optional
        The size of the images converted to blob, by default `None`.
    p_on_raspberry : `bool`, optional
        Indicate if we are using a raspberry or not, by default `None`.
    p_real_time_processing : `bool`, optional
        Indicate if we want to see a window with the real-time processing in it, by default `None`.
    p_dict : `Dict[str, Any]`, optional
        A dictionary containing the information, by default `None`.

    """
    global __config_dict

    def recursive_call(p_dict: Dict[str, Any]) -> None:
        if INPUT_PATH in p_dict.keys():
            save_config_ai(p_input_video_path=p_dict[INPUT_PATH])

        if OUTPUT_PATH in p_dict.keys():
            save_config_ai(p_output_video_path=p_dict[OUTPUT_PATH])

        if YOLO_CFG_PATH in p_dict.keys():
            save_config_ai(p_yolo_cfg_path=p_dict[YOLO_CFG_PATH])

        if YOLO_WEIGHTS_PATH in p_dict.keys():
            save_config_ai(p_yolo_weights_path=p_dict[YOLO_WEIGHTS_PATH])

        if SEE_REAL_TIME_PROCESS in p_dict.keys():
            save_config_ai(p_real_time_processing=p_dict[SEE_REAL_TIME_PROCESS])

        if ON_RASPBERRY in p_dict.keys():
            save_config_ai(p_on_raspberry=p_dict[ON_RASPBERRY])

        if IMG_SIZE in p_dict.keys():
            save_config_ai(p_size=p_dict[IMG_SIZE])

    if p_dict is not None:
        recursive_call(p_dict)

    if isinstance(p_input_video_path, str):
        __config_dict[MODULE_AI][INPUT_PATH] = p_input_video_path

    if isinstance(p_output_video_path, str):
        __config_dict[MODULE_AI][OUTPUT_PATH] = p_output_video_path

    if isinstance(p_yolo_cfg_path, str):
        __config_dict[MODULE_AI][YOLO_CFG_PATH] = p_yolo_cfg_path

    if isinstance(p_yolo_weights_path, str):
        __config_dict[MODULE_AI][YOLO_WEIGHTS_PATH] = p_yolo_weights_path

    if isinstance(p_size, int):
        __config_dict[MODULE_AI][IMG_SIZE] = p_size

    if isinstance(p_on_raspberry, bool):
        __config_dict[MODULE_AI][ON_RASPBERRY] = p_on_raspberry

    if isinstance(p_real_time_processing, bool):
        __config_dict[MODULE_AI][SEE_REAL_TIME_PROCESS] = p_real_time_processing


def get_config(p_module_id: Optional[str] = None, p_value_id: Optional[str] = None) -> Any:
    """Return the configuration for the given module and given value id.

    If `p_module_id` is not specified then all parameters are returned.

    If `p_value_id` is not specified but `p_module_id` is, then all parameters of the module are returned

    Parameters
    ----------
    p_module_id : `str`, optional
        The name of the module whose parameters are desired, by default `None`.
    p_value_id : Optional[`str`], optional
        The name of the module variable whose parameters are desired, by default `None`.

    Returns
    -------
    Any
        The requested configuration.

    Raises
    ------
    KeyError
        The module or the variable does not exist or is not linked.

    See
    ---
    - `save_config_ai`
    - `save_config_gpio`
    - `save_config_logging`
    """
    if p_module_id is not None:
        if p_value_id is not None:
            return __config_dict[p_module_id][p_value_id]
        else:
            return __config_dict[p_module_id].copy()
    else:
        return __config_dict.copy()
