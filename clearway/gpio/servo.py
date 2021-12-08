"""Module to control the camera angle using a servo motor."""

import time
import logging

import clearway.gpio as gpio


def config(angle: int, servo_gpio: int) -> None:
    """Initialize the servo motor to fit with the given parameter.

    Parameters
    ----------
    angle : int
        The angle of the camera between 0° to 180°.
    servo_gpio : int
        The GPIO pin of the raspberry Pi
    """
    logging.info("[SERVO-%d] Set angle to %d", servo_gpio, angle)

    if gpio.GPIO is not None:
        gpio.GPIO.setup(servo_gpio, gpio.GPIO.OUT)
        p = gpio.GPIO.PWM(servo_gpio, 50)

        # Initialization
        p.start(2)
        time.sleep(0.5)
        try:
            # % to have the module for the angle between 0 and 180°
            newposition = 1.0 / 18.0 * (angle % 180) + 2
            p.ChangeDutyCycle(newposition)
            time.sleep(0.5)
            # Stop the servo shaking
            p.ChangeDutyCycle(0)
        except KeyboardInterrupt:
            p.stop()
