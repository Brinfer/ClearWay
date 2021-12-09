"""Module to control the camera angle using a servo motor."""

import time
import logging

import clearway.gpio as gpio

newposition = None


def config(angle: int, servo_gpio: int) -> None:
    """Initialize the servo motor to fit with the given parameter.

    Parameters
    ----------
    angle : int
        The angle of the camera between 0° to 180°.
    servo_gpio : int
        The GPIO pin of the raspberry Pi
    """
    global newposition

    logging.info("[SERVO-%d] Set angle to %d", servo_gpio, angle)

    gpio.GPIO.setup(servo_gpio, gpio.GPIO.OUT)
    # GPIO 12 for PWM with 50Hz, pin 32
    p = gpio.GPIO.PWM(servo_gpio, 50)
    # Initialization
    p.start(2)
    time.sleep(0.5)
    try:
        # % to have the module for the angle between 0 and 180°
        newposition = servo_angle_calculator(angle)
        p.ChangeDutyCycle(newposition)
        time.sleep(0.5)
        # Stop the servo shaking
        p.ChangeDutyCycle(0)
    except KeyboardInterrupt:
        p.stop()


def servo_angle_calculator(angle: int):
    """Calculate the duty cycle of the servo motor from an angle.

    Parameters
    ----------
    angle : int
        The angle of the camera between 0° to 180°
        If the value is out of range, a modulo of 180° will be apply

    Returns
    -------
    [int]
        The Duty cycle for the servo motor
    """
    return 1.0 / 18.0 * (angle % 180) + 2
