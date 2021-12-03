import time
#from clearway.gpio import GPIO

import clearway.gpio as gpio


def servo_init(angle:int) -> None:
    servoPIN = 12
    print(gpio.GPIO)
    if gpio.GPIO is not None:
        gpio.GPIO.setmode(gpio.GPIO.BCM)
        gpio.GPIO.setup(servoPIN, gpio.GPIO.OUT)

        p = gpio.GPIO.PWM(servoPIN, 50)  # GPIO 12 for PWM with 50Hz, pin 32
        p.start(2)  # Initialization
        time.sleep(0.5)
        try:
            newposition = 1./18.*(angle % 180)+2  # % to have the module for the angle between 0 and 180°
            p.ChangeDutyCycle(newposition)
            time.sleep(0.5)
            p.ChangeDutyCycle(0)  # Stop the servo shaking
        except KeyboardInterrupt:
            p.stop()
