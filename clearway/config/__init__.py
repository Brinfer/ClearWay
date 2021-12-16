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


MAIN_SECTION = "clearway"
SUBSECTION_GPIO = "gpio"
SUBSECTION_AI = "ai"
SUBSECTION_LOG = "log"

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


def save_config_from_file(p_path: str) -> None:
    """Save the config from the given config file.

    The configuration file must be in toml format. The section searched is `PROJECT_KEY_CONFIG`.
    If the section is not found, then nothing happens.

    If one of the subsection does not match, then this section is not taken into consideration.

    Parameters
    ----------
    p_path : `str`
        The path to the config file.

    Raises
    ------
    toml.TomlDecodeError:
        Error while decoding toml
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

    Parameters
    ----------
    p_verbosity_level : str, optional
        The verbosity level to use, by default None

    Raises
    ------
    TypeError
        The type of `p_verbosity_level` is not `str`
    ValueError
        The value of `p_verbosity_level` is unknown
    """
    global __config_dict

    if p_dict is not None:
        if LOG_VERBOSITY_LEVEL in p_dict.keys():
            save_config_logging(p_verbosity_level=p_dict[LOG_VERBOSITY_LEVEL])

    if p_verbosity_level is not None:
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
        else:
            raise TypeError(
                "[CONFIG] Wrong type for p_verbosity_level, {} instead of str".format(type(p_verbosity_level))
            )


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

    If the argument is set to `None` then it will not be saved.

    Parameters
    ----------
    p_use_gpio : `bool`, optional
        `True` if you want to use GPIOs, `False` otherwise, by default None
    p_gpios : `Iterable[int]`, optional
        GPIOs to use, by default None

    Raises
    ------
    TypeError
        The type of `p_use_gpio` is not `bool`
    TypeError
        The type of `p_gpios` is not `Iterable`
    TypeError
        One of the elements in `p_gpios` is not an `int`
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

    if p_use_gpio is not None:
        if isinstance(p_use_gpio, bool):
            logging.debug("[CONFIG] Save new instruction for the use of the GPIOs: {}".format(p_use_gpio))
            __config_dict[SUBSECTION_GPIO][USE_GPIO] = p_use_gpio
        else:
            raise TypeError("[CONFIG] Wrong type for p_use_gpio, {} instead of bool".format(type(p_use_gpio)))

    if p_gpios is not None:
        if isinstance(p_gpios, Iterable):
            if any(isinstance(l_gpio, int) for l_gpio in p_gpios):
                logging.debug("[CONFIG] Save new GPIOs to use: %s", ", ".join([str(i) for i in p_gpios]))
                __config_dict[SUBSECTION_GPIO][PANEL_GPIOS] = p_gpios
            else:
                raise TypeError("[CONFIG] Wrong type in p_gpios, not all element are int")
        else:
            raise TypeError("[CONFIG] Wrong type for p_gpios, {} instead of Iterable".format(type(p_gpios)))

    if p_servo is not None:
        if isinstance(p_servo, int):
            logging.debug("[CONFIG] Save new GPIO for the servo-motors to use: %d", p_servo)
            __config_dict[SUBSECTION_GPIO][SERVO_GPIO] = p_servo
        else:
            raise TypeError("[CONFIG] Wrong type for p_servo, {} instead of int".format(type(p_use_gpio)))

    if p_camera_angle is not None:
        if isinstance(p_camera_angle, int):
            logging.debug("[CONFIG] Save new GPIO for the servo-motors to use: %d", p_camera_angle)
            __config_dict[SUBSECTION_GPIO][CAMERA_ANGLE] = p_camera_angle
        else:
            raise TypeError("[CONFIG] Wrong type for p_servo, {} instead of int".format(type(p_camera_angle)))


def apply_config_gpio() -> None:
    """Configure the `clearway.gpio` module.

    Configures:
    - whether the program uses GPIOs or not.
    - what are the GPIOs to use for signaling.
    - which GPIO to use for the servo motor.

    All these values are the ones provided when using `save_config_gpio`, otherwise the default values will be used
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

    Raises
    ------
    TypeError
        The type of `p_input_video_path` is not `str`
    TypeError
        The type of `p_output_video_path` is not `str`
    TypeError
        The type of `p_yolo_cfg_path` is not `str`
    TypeError
        The type of `p_yolo_weights_path` is not `str`
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

    if p_input_video_path is not None:
        if isinstance(p_input_video_path, str):
            __config_dict[SUBSECTION_AI][INPUT_PATH] = p_input_video_path
        else:
            raise TypeError(
                "[CONFIG] Wrong type for p_input_video_path, {} instead of str".format(type(p_input_video_path))
            )

    if p_output_video_path is not None:
        if isinstance(p_output_video_path, str):
            __config_dict[SUBSECTION_AI][OUTPUT_PATH] = p_output_video_path
        else:
            raise TypeError(
                "[CONFIG] Wrong type for p_output_video_path, {} instead of str".format(type(p_output_video_path))
            )

    if p_yolo_cfg_path is not None:
        if isinstance(p_yolo_cfg_path, str):
            __config_dict[SUBSECTION_AI][YOLO_CFG_PATH] = p_yolo_cfg_path
        else:
            raise TypeError("[CONFIG] Wrong type for p_yolo_cfg_path, {} instead of str".format(type(p_yolo_cfg_path)))

    if p_yolo_weights_path is not None:
        if isinstance(p_yolo_weights_path, str):
            __config_dict[SUBSECTION_AI][YOLO_WEIGHTS_PATH] = p_yolo_weights_path
        else:
            raise TypeError(
                "[CONFIG] Wrong type for p_yolo_weights_path, {} instead of str".format(type(p_yolo_weights_path))
            )


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
    """
    apply_config_logging()
    apply_config_gpio()
    apply_config_ai()
