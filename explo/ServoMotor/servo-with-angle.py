import RPi.GPIO as GPIO
import time

servoPIN = 12
desirePosition = 90

GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)

p = GPIO.PWM(servoPIN, 50)  # GPIO 12 for PWM with 50Hz, pin 32
p.start(2)  # Initialization
time.sleep(0.5)
try:
    newposition = 1./18.*(desirePosition % 180)+2 #% to have the module for the angle between 0 and 180°
    p.ChangeDutyCycle(newposition)
    time.sleep(0.5)
    p.ChangeDutyCycle(0) #Stop the servo shaking
except KeyboardInterrupt:
    p.stop()