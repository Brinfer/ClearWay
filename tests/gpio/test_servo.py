"""Test the servo motor function.

 See Also
    --------
    clearway.gpio.servo: File Under Test
"""

from clearway.gpio import servo
import clearway.gpio as gpio
import pytest

gpio_pin = 12


def setup() -> None:
    """Set up the test.

    The function is called before every test.
    """
    gpio.use_gpio(False)


@pytest.mark.parametrize(('input_angle', 'output_result'), [
    (180, 2.0),
    (0, 2.0),
    (-180, 2.0),
    (-45, 9.5),
    (45, 4.5),
    (77.5, 6.3)])
def test_servo_motor(input_angle, output_result):
    """Test the function of the servo motor.

    Parameters
    ----------
    input_angle : [int]
        An angle between 0° and 180°.
        If this angle is out of range a 180° modulo is apply
    output_result : [float]
        The dutyCycle of the servo motor
    """
    servo.servo_init(input_angle, gpio_pin)
    assert round(servo.newposition, 1) == output_result
