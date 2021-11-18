# Damien Frissant
# This file aim to take multiple pictures

import time
import picamera

frames = 60

with picamera.PiCamera() as camera:
    # Resolution of the picture
    camera.resolution = (1024, 768)
    # number of fps
    camera.framerate = 2
    # camera.start_preview()
    # Give the camera some warm-up time
    time.sleep(2)

    # Start the 'clock'
    start = time.time()

    camera.capture_sequence([
        'image%02d.jpg' % i
        for i in range(frames)
    ], use_video_port=True)

    # Stop the clock
    finish = time.time()

print('Take %d images at %.2ffps' % (
    frames,
    frames / (finish - start)))
