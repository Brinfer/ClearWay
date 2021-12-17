"""Allows you to test the module `clearway.config`."""

import logging
from typing import Any, Dict

import pytest
from pytest_mock.plugin import MockerFixture
import clearway.config as config

default_config: Dict[str, Any] = dict()

VALUE_NOMINAL: Dict[str, Any] = {
    config.MODULE_AI: {
        config.INPUT_PATH: "input/video1.mp4",
        config.OUTPUT_PATH: "output/video1.mp4",
        config.YOLO_CFG_PATH: "yolo_cfg",
        config.YOLO_WEIGHTS_PATH: "yolo_weights",
        config.ON_RASPBERRY: True,
        config.IMG_SIZE: 416,
        config.SEE_REAL_TIME_PROCESS: True,
    },
    config.MODULE_GPIO: {
        config.USE_GPIO: False,
        config.PANEL_GPIOS: [5, 6],
        config.CAMERA_ANGLE: 75,
        config.SERVO_GPIO: 12,
    },
    config.MODULE_LOGGING: {
        config.LOG_VERBOSITY_LEVEL: logging.DEBUG,
        config.LOG_FORMAT: "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s >> %(message)s",
        config.LOG_PATH: "ClearWay.log",
    },
}
"""Contains the values of the parameters of the files `nominal.toml` and `multiple_sections.toml`."""


def setup() -> None:
    """Set up the environnement for the tests.

    Save the default configuration saved.
    """
    global default_config

    default_config = config.__config_dict.copy()


def teardown() -> None:
    """Reset the environnement of the tests.

    Restore the default configuration saved.
    """
    global default_config

    config.__config_dict = default_config.copy()


@pytest.mark.parametrize(
    "p_file", ["tests/config/toml_files/nominal.toml", "tests/config/toml_files/multiple_sections.toml"]
)
def test_nominal(p_file: str) -> None:
    """Test the application of the configuration with the parameters.

    The test file contains all the parameters and is in the correct format.
    The `multiple_sections.toml` file contains other sections that have nothing
    to do with the program but the parameters are the same as for the nominal file.

    All parameters are in `VALUE_NOMINAL`.

    Parameters
    ----------
    p_file : `str`
        The path to the configuration file.
    """
    config.save_config_from_file(p_file)

    assert config.__config_dict[config.MODULE_GPIO] == VALUE_NOMINAL[config.MODULE_GPIO]
    assert config.__config_dict[config.MODULE_AI] == VALUE_NOMINAL[config.MODULE_AI]
    assert config.__config_dict[config.MODULE_LOGGING] == VALUE_NOMINAL[config.MODULE_LOGGING]


@pytest.mark.parametrize("p_file", ["tests/config/toml_files/empty.toml", "tests/config/toml_files/no_section.toml"])
def test_no_section(p_file: str) -> None:
    """Test the application of the configuration with the parameters.

    The test files do not contain any parameters or even a section for the program
    The `no_section.toml` file contains other sections that have nothing
    to do with the program.

    All parameters are in `save_old_config`.

    Parameters
    ----------
    p_file : `str`
        The path to the configuration file.
    """
    config.save_config_from_file(p_file)

    assert config.__config_dict[config.MODULE_GPIO] == default_config[config.MODULE_GPIO]
    assert config.__config_dict[config.MODULE_AI] == default_config[config.MODULE_AI]
    assert config.__config_dict[config.MODULE_LOGGING] == default_config[config.MODULE_LOGGING]


def test_wrong_key(mocker: MockerFixture) -> None:
    """Test if the configuration file contains non-recognized keys.

    The file keys are the expected ones but written in capital, the keys are case sensitive.
    An exception is expected.
    """
    l_file = "tests/config/toml_files/wrong_key.toml"

    config.save_config_from_file(l_file)

    assert config.__config_dict[config.MODULE_GPIO] == default_config[config.MODULE_GPIO]
    assert config.__config_dict[config.MODULE_AI] == default_config[config.MODULE_AI]
    assert config.__config_dict[config.MODULE_LOGGING] == default_config[config.MODULE_LOGGING]


@pytest.mark.parametrize(
    "p_file",
    [
        "tests/config/toml_files/wrong_value_gpio_A.toml",
        "tests/config/toml_files/wrong_value_gpio_B.toml",
        "tests/config/toml_files/wrong_value_gpio_C.toml",
    ],
)
def test_wrong_value_gpio(p_file: str) -> None:
    """Test if the file contains invalid values.

    If a value is invalid, then the configuration associated with the key must remain the same as the default.

    Parameters
    ----------
    p_file : `str`
        The path to the configuration file.
    """
    config.save_config_from_file(p_file)

    assert config.__config_dict[config.MODULE_GPIO] == default_config[config.MODULE_GPIO]
    assert config.__config_dict[config.MODULE_AI] == default_config[config.MODULE_AI]
    assert config.__config_dict[config.MODULE_LOGGING] == default_config[config.MODULE_LOGGING]
