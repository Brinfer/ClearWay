"""Module to control the camera angle using a servo motor."""

import time
import logging
from typing import Optional

import clearway.gpio as gpio
import clearway.config as config

newposition = None


def set_angle(p_angle: Optional[int] = None, p_servo_gpio: Optional[int] = None) -> None:
    """Initialize the servo motor to fit with the given parameter.

    Parameters
    ----------
    angle : int
        The angle of the camera between 0° to 180°.
    servo_gpio : int
        The GPIO pin of the raspberry Pi
    """
    global newposition

    angle: int
    servo_gpio: int

    if p_angle is None:
        angle = config.get_config(config.MODULE_GPIO, config.CAMERA_ANGLE)
    else:
        angle = p_angle

    if p_servo_gpio is None:
        servo_gpio = config.get_config(config.MODULE_GPIO, config.SERVO_GPIO)
    else:
        servo_gpio = p_servo_gpio

    logging.info("[SERVO-%d] Set angle to %d", servo_gpio, angle)

    gpio.GPIO.setup(servo_gpio, gpio.GPIO.OUT)
    # GPIO 12 for PWM with 50Hz, pin 32
    p = gpio.GPIO.PWM(servo_gpio, 50)
    # Initialization
    p.start(2)
    time.sleep(0.5)
    try:
        # % to have the module for the angle between 0 and 180°
        newposition = angle_calculator(angle)
        p.ChangeDutyCycle(newposition)
        time.sleep(0.5)
        # Stop the servo shaking
        p.ChangeDutyCycle(0)
    except KeyboardInterrupt:
        p.stop()


def angle_calculator(angle: int) -> float:
    """Calculate the duty cycle of the servo motor from an angle.

    Parameters
    ----------
    angle : int
        The angle of the camera between 0° to 180°
        If the value is out of range, a modulo of 180° will be apply

    Returns
    -------
    `float`
        The Duty cycle for the servo motor
    """
    return 1.0 / 18.0 * (angle % 180) + 2
