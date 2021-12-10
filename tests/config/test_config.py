"""Allows you to test the module `clearway.config`."""

import logging
from typing import Any, Dict

import pytest  # noqa: E402 module level import not at top of file
from pytest_mock.plugin import MockerFixture  # noqa: E402 module level import not at top of file
import clearway.gpio as gpio  # noqa: E402 module level import not at top of file
from clearway.gpio import servo, stateMachinePanel  # noqa: E402 module level import not at top of file
from clearway.ai import ai  # noqa: E402 module level import not at top of file
import clearway.config as config  # noqa: E402 module level import not at top of file

default_config: Dict[str, Any] = dict()

VALUE_NOMINAL: Dict[str, Any] = {
    config.USE_GPIO: False,
    config.PANEL_GPIOS: [5, 6],
    config.INPUT_PATH: "input/video1.mp4",
    config.OUTPUT_PATH: "output/video1.mp4",
    config.YOLO_CFG_PATH: "yolo_cfg",
    config.YOLO_WEIGHTS_PATH: "yolo_weights",
    config.LOG_VERBOSITY_LEVEL: "DEBUG",
    config.CAMERA_ANGLE: 75,
    config.SERVO_GPIO: 12,
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
    gpio.use_gpio.assert_called_with(VALUE_NOMINAL[config.USE_GPIO])
    stateMachinePanel.config.assert_called_with(VALUE_NOMINAL[config.PANEL_GPIOS])
    servo.config.assert_called_with(VALUE_NOMINAL[config.CAMERA_ANGLE], VALUE_NOMINAL[config.SERVO_GPIO])

    # ai
    ai.config.assert_called_with(
        VALUE_NOMINAL[config.YOLO_WEIGHTS_PATH],
        VALUE_NOMINAL[config.YOLO_CFG_PATH],
        VALUE_NOMINAL[config.INPUT_PATH],
        VALUE_NOMINAL[config.OUTPUT_PATH],
    )

    # logging
    assert logging.basicConfig.call_args[1]["level"] == logging.DEBUG


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
    gpio.use_gpio.assert_called_with(default_config[config.USE_GPIO])
    stateMachinePanel.config.assert_called_with(default_config[config.PANEL_GPIOS])
    servo.config.assert_called_with(default_config[config.CAMERA_ANGLE], default_config[config.SERVO_GPIO])

    # ai
    ai.config.assert_called_with(
        default_config[config.YOLO_WEIGHTS_PATH],
        default_config[config.YOLO_CFG_PATH],
        default_config[config.INPUT_PATH],
        default_config[config.OUTPUT_PATH],
    )

    # logging
    assert logging.basicConfig.call_args.kwargs["level"] == logging.INFO


def test_wrong_key() -> None:
    """Test if the configuration file contains non-recognized keys.

    The file keys are the expected ones but written in capital, the keys are case sensitive.
    An exception is expected.
    """
    l_file = "tests/config/toml_files/wrong_key.toml"

    with pytest.raises(KeyError):
        config.save_config_from_file(l_file)
