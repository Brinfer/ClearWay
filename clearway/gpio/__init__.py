"""Module to control the inputs and outputs of the card."""

"""Variable linking to the package RPi.GPIO."""
from logging import log
import logging


GPIO = None


def use_gpio(p_value: bool) -> None:
    """Tells the rest of the module if they can modify the GPIO level.

    If the passed parameter is `True`, then the module `RPi.GPIO` is imported.
    This function must be called at the beginning of the program.

    Parameters
    ----------
    p_value : `bool`
        `True` if you want to use GPIOs, `False` otherwise.
    """
    global GPIO

    logging.info("[GPIO] GPIO will be %s", "used" if p_value else "not used")

    if p_value is True:
        # Import RPi.GPIO and save it in a global variable
        import RPi.GPIO as GPIO  # noqa: N814: camelcase 'RPi.GPIO' imported as constant 'GPIO'

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)  # Disable warning messages
    else:
        GPIO = None
