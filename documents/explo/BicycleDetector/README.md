# BicycleDetector
_Author : Léo Chauvin_
## Description
The program bicycle_detector.py gets the video stream of the Raspberry camera.

Then it checks frame by frame if there is a bicycle in front of the camera.

It shows the frames to the user with the bicycles framed in boxes if they are detected with a probability of a least 0,5.

## Requirements
To be able to run this program, you need to add the files "yolov3_320.weights" and "yolov3_320.cfg" at the same level of bicycle_detector.py.

They are located at the following link, in the openCV_algorithm folder: https://drive.google.com/drive/folders/1FnClVPYMw08y6uTTWVsTBuglmnP5qvyR

## Run the program
At the home folder of the Raspberry, write the following commands
```bash
workon cv
python3 bicycle_detector.py
```