""" Module to control the camera angle using a servo motor."""
import time
import clearway.gpio as gpio


def servo_init(angle: int, servoPIN: int) -> None:
    """Initialize the servo motor to fit with the given parameter.

    Parameters
    ----------
    angle : int
        The angle of the camera between 0° to 180°.
    servoPIN : int
        The GPIO pin of the raspberry Pi
    """
    print(gpio.GPIO)
    if gpio.GPIO is not None:
        gpio.GPIO.setmode(gpio.GPIO.BCM)
        gpio.GPIO.setup(servoPIN, gpio.GPIO.OUT)

        p = gpio.GPIO.PWM(servoPIN, 50)  # GPIO 12 for PWM with 50Hz, pin 32
        p.start(2)  # Initialization
        time.sleep(0.5)
        try:
            newposition = 1.0 / 18.0 * (angle % 180) + 2  # % to have the module for the angle between 0 and 180°
            p.ChangeDutyCycle(newposition)
            time.sleep(0.5)
            p.ChangeDutyCycle(0)  # Stop the servo shaking
        except KeyboardInterrupt:
            p.stop()
