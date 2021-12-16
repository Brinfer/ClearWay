"""Allows you to test the module `clearway.config`."""

import logging
from typing import Any, Dict

import toml
import pytest
from pytest_mock.plugin import MockerFixture
import clearway.gpio as gpio
from clearway.gpio import servo, stateMachinePanel
from clearway.ai import ai
import clearway.config as config

default_config: Dict[str, Any] = dict()

VALUE_NOMINAL: Dict[str, Any] = {
    config.SUBSECTION_AI: {
        config.INPUT_PATH: "input/video1.mp4",
        config.OUTPUT_PATH: "output/video1.mp4",
        config.YOLO_CFG_PATH: "yolo_cfg",
        config.YOLO_WEIGHTS_PATH: "yolo_weights",
    },
    config.SUBSECTION_GPIO: {
        config.USE_GPIO: False,
        config.PANEL_GPIOS: [5, 6],
        config.CAMERA_ANGLE: 75,
        config.SERVO_GPIO: 12,
    },
    config.SUBSECTION_LOG: {
        config.LOG_VERBOSITY_LEVEL: logging.DEBUG,
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
def test_nominal(p_file: str, mocker: MockerFixture) -> None:
    """Test the application of the configuration with the parameters.

    The test file contains all the parameters and is in the correct format.
    The `multiple_sections.toml` file contains other sections that have nothing
    to do with the program but the parameters are the same as for the nominal file.

    All parameters are in `VALUE_NOMINAL`.

    Parameters
    ----------
    p_file : `str`
        The path to the configuration file.
    mocker : `MockerFixture`
        The interface for the mock module functions.
    """
    mocker.patch("clearway.gpio.use_gpio")
    mocker.patch("clearway.gpio.stateMachinePanel.config")
    mocker.patch("clearway.gpio.servo.config")
    mocker.patch("clearway.ai.ai.config")
    mocker.patch("logging.basicConfig")

    config.save_config_from_file(p_file)
    config.apply_config_all()

    # gpio
    gpio.use_gpio.assert_called_with(VALUE_NOMINAL[config.SUBSECTION_GPIO][config.USE_GPIO])
    stateMachinePanel.config.assert_called_with(VALUE_NOMINAL[config.SUBSECTION_GPIO][config.PANEL_GPIOS])
    servo.config.assert_called_with(
        VALUE_NOMINAL[config.SUBSECTION_GPIO][config.CAMERA_ANGLE],
        VALUE_NOMINAL[config.SUBSECTION_GPIO][config.SERVO_GPIO],
    )

    # ai
    ai.config.assert_called_with(
        VALUE_NOMINAL[config.SUBSECTION_AI][config.YOLO_WEIGHTS_PATH],
        VALUE_NOMINAL[config.SUBSECTION_AI][config.YOLO_CFG_PATH],
        VALUE_NOMINAL[config.SUBSECTION_AI][config.INPUT_PATH],
        VALUE_NOMINAL[config.SUBSECTION_AI][config.OUTPUT_PATH],
    )

    # logging
    assert logging.basicConfig.call_args[1]["level"] == VALUE_NOMINAL[config.SUBSECTION_LOG][config.LOG_VERBOSITY_LEVEL]


@pytest.mark.parametrize("p_file", ["tests/config/toml_files/empty.toml", "tests/config/toml_files/no_section.toml"])
def test_no_section(p_file: str, mocker: MockerFixture) -> None:
    """Test the application of the configuration with the parameters.

    The test files do not contain any parameters or even a section for the program
    The `no_section.toml` file contains other sections that have nothing
    to do with the program.

    All parameters are in `save_old_config`.

    Parameters
    ----------
    p_file : `str`
        The path to the configuration file.
    mocker : `MockerFixture`
        The interface for the mock module functions.
    """
    mocker.patch("clearway.gpio.use_gpio")
    mocker.patch("clearway.gpio.stateMachinePanel.config")
    mocker.patch("clearway.gpio.servo.config")
    mocker.patch("clearway.ai.ai.config")
    mocker.patch("logging.basicConfig")

    config.save_config_from_file(p_file)
    config.apply_config_all()

    # gpio
    gpio.use_gpio.assert_called_with(default_config[config.SUBSECTION_GPIO][config.USE_GPIO])
    stateMachinePanel.config.assert_called_with(default_config[config.SUBSECTION_GPIO][config.PANEL_GPIOS])
    servo.config.assert_called_with(
        default_config[config.SUBSECTION_GPIO][config.CAMERA_ANGLE],
        default_config[config.SUBSECTION_GPIO][config.SERVO_GPIO],
    )

    # ai
    ai.config.assert_called_with(
        default_config[config.SUBSECTION_AI][config.YOLO_WEIGHTS_PATH],
        default_config[config.SUBSECTION_AI][config.YOLO_CFG_PATH],
        default_config[config.SUBSECTION_AI][config.INPUT_PATH],
        default_config[config.SUBSECTION_AI][config.OUTPUT_PATH],
    )

    # logging
    assert logging.basicConfig.call_args[1]["level"] == default_config[config.SUBSECTION_LOG][config.LOG_VERBOSITY_LEVEL]


def test_wrong_key(mocker: MockerFixture) -> None:
    """Test if the configuration file contains non-recognized keys.

    The file keys are the expected ones but written in capital, the keys are case sensitive.
    An exception is expected.
    """
    l_file = "tests/config/toml_files/wrong_key.toml"

    mocker.patch("clearway.gpio.use_gpio")
    mocker.patch("clearway.gpio.stateMachinePanel.config")
    mocker.patch("clearway.gpio.servo.config")
    mocker.patch("clearway.ai.ai.config")
    mocker.patch("logging.basicConfig")

    config.save_config_from_file(l_file)
    config.apply_config_all()

    # gpio
    gpio.use_gpio.assert_called_with(default_config[config.SUBSECTION_GPIO][config.USE_GPIO])
    stateMachinePanel.config.assert_called_with(default_config[config.SUBSECTION_GPIO][config.PANEL_GPIOS])
    servo.config.assert_called_with(
        default_config[config.SUBSECTION_GPIO][config.CAMERA_ANGLE],
        default_config[config.SUBSECTION_GPIO][config.SERVO_GPIO],
    )

    # ai
    ai.config.assert_called_with(
        default_config[config.SUBSECTION_AI][config.YOLO_WEIGHTS_PATH],
        default_config[config.SUBSECTION_AI][config.YOLO_CFG_PATH],
        default_config[config.SUBSECTION_AI][config.INPUT_PATH],
        default_config[config.SUBSECTION_AI][config.OUTPUT_PATH],
    )

    # logging
    assert logging.basicConfig.call_args[1]["level"] == default_config[config.SUBSECTION_LOG][config.LOG_VERBOSITY_LEVEL]


@pytest.mark.parametrize(
    ("p_file, p_error_type"),
    [
        ("tests/config/toml_files/wrong_value_gpio_A.toml", TypeError),
        ("tests/config/toml_files/wrong_value_gpio_B.toml", TypeError),
        ("tests/config/toml_files/wrong_value_gpio_C.toml", toml.TomlDecodeError),
        ("tests/config/toml_files/wrong_value_gpio_D.toml", TypeError),
        ("tests/config/toml_files/wrong_value_gpio_E.toml", TypeError)
    ],
)
def test_wrong_value_gpio(p_file: str, p_error_type: Exception, mocker: MockerFixture) -> None:
    with pytest.raises((p_error_type)):
        config.save_config_from_file(p_file)
