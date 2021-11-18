### Damien Frissant
### This file aim to take 6 pictures and save them.
### A new picture erease the previous one

import time
import picamera

with picamera.PiCamera() as camera:
    for x in range(0,6):
        # Max résolution 2592, 1944
        camera.resolution = (1024, 768)
        #camera.start_preview()
        camera.capture('foo.jpg')