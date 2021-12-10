"""OpenCV object detection using picamera."""
import time
import logging
from enum import IntEnum, auto, unique
import os
from typing import List, Optional, Tuple, Union

import numpy
from imutils.video import VideoStream, FPS
import cv2
from clearway.gpio import stateMachinePanel


@unique
class __IdYoloOutputLayer(IntEnum):
    """ID related to the three output layers of YOLO.

    The first four ID represent the location of detected objects.
    The other IDs represent the detection confidence for 80 different objects.
    Here we are only interested in detecting persons and bicycles.
    """

    CENTER_X = 0
    CENTER_Y = auto()
    WIDTH = auto()
    HEIGHT = auto()
    PERSON = 5
    BICYCLE = auto()


__object_detection_id: __IdYoloOutputLayer = __IdYoloOutputLayer.PERSON
__network: cv2.dnn_Net
__output_layers: List[str]
__video_stream: Union[cv2.VideoCapture, VideoStream]
__path_to_input_video: Optional[str] = None
__path_to_output_video: Optional[str] = None
__output_video: cv2.VideoWriter
__output_color: Tuple[int, int, int] = (0, 0, 255)  # Blue
__prob_threshold: float = 0.5
__detect: bool = False
__detect_old: bool = False


def config(
    yolo_weights: str,
    yolo_cfg: str,
    path_to_input_video: Optional[str] = None,
    path_to_output_video: Optional[str] = None,
) -> None:
    """Get the three output layers of YOLO and start the video stream.

    Parameters
    ----------
    path_to_input_video : string, optional
        The path to the input video that is going to be processed, by default None.
    """
    global __network, __output_layers, __path_to_input_video, __path_to_output_video, __video_stream, __output_video

    # Read the deep learning network Yolo
    __network = cv2.dnn.readNet(yolo_weights, yolo_cfg)

    # Find names of all layers of the YOLO model architecture
    layer_names = __network.getLayerNames()
    __output_layers = [layer_names[i[0] - 1] for i in __network.getUnconnectedOutLayers()]

    if path_to_input_video is None:
        __video_stream = VideoStream(usePiCamera=True).start()
        # Very important! Otherwise, video_stream.read() gives a NonType
        time.sleep(2.0)
        logging.info("[AI] Camera ready to detect")
    else:
        __path_to_input_video = path_to_input_video
        __video_stream = cv2.VideoCapture(path_to_input_video)

    if path_to_output_video is not None:
        # execution_path = os.getcwd()
        __path_to_output_video = path_to_output_video
        output_video_file = os.path.join(path_to_output_video, "video_processed.mp4")
        x_shape = int(__video_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
        y_shape = int(__video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
        four_cc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
        __output_video = cv2.VideoWriter(output_video_file, four_cc, fps=1, frameSize=(x_shape, y_shape))


def bicycle_detector(gpio_led: int) -> None:
    """Detect cyclists on a video stream frame by frame.

    Get the video stream from the Raspberry Pi camera.
    Process the stream to detect cyclists using a YOLO algorithm and the openCV library.
    """
    global __path_to_input_video, __path_to_output_video, __video_stream, __network, __output_video, __output_layers

    # Start the frames per second
    fps = FPS().start()

    if __path_to_input_video is None:
        read_ok = True
        img = __video_stream.read()
    else:
        read_ok, img = __video_stream.read()

    while read_ok:
        # Get dimensions of image
        height, width, channels = img.shape

        # Convert image to Blob
        # Scalefactor of 1/255 to scale the pixel values to [0..1]
        blob = cv2.dnn.blobFromImage(img, scalefactor=1 / 255, size=(416, 416), mean=(0, 0, 0), swapRB=True, crop=False)
        # Set input for YOLO object detection
        __network.setInput(blob)
        # Send Blob image data to the three output layers
        outs = __network.forward(__output_layers)

        confidences = []
        boxes = []

        for out in outs:
            for detection in out:
                confidence = detection[__object_detection_id]
                if confidence > __prob_threshold:
                    # Object detected
                    center_x = int(detection[__IdYoloOutputLayer.CENTER_X] * width)
                    center_y = int(detection[__IdYoloOutputLayer.CENTER_Y] * height)
                    w = int(detection[__IdYoloOutputLayer.WIDTH] * width)
                    h = int(detection[__IdYoloOutputLayer.HEIGHT] * height)
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))

        # To remove multiple boxes that refer to the same object and keep one by Non Maximum Supression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)

        img = dram_boxes_and_call_state_machine(indexes, boxes, confidences, img, gpio_led)

        # Update the FPS counter
        fps.update()

        if __path_to_input_video is None:
            img = __video_stream.read()
        else:
            read_ok, img = __video_stream.read()

        if __path_to_output_video is not None:
            __output_video.write(img)

    # Stop the timer and display FPS information
    fps.stop()
    logging.debug("[IA] elapsed time: {:.2f}".format(fps.elapsed()))
    logging.debug("[IA] approx. FPS: {:.2f}".format(fps.fps()))

    if __path_to_input_video is None:
        __video_stream.stop()


def dram_boxes_and_call_state_machine(
    indexes: List[int], boxes: List[List[int]], confidences: List[float], img: numpy.ndarray, gpio_led: int
) -> numpy.ndarray:
    """Draw boxes around object detected and inform the gpio stateMachinePanel if a cyclist is detected or not.

    Parameters
    ----------
    indexes : List[int]
        List of object indexes used to remove multiple boxes that refer to the same object.
    boxes : List[List[int]]
        List of boxes with their information (center_x, center_y, width, height).
    confidences : List[float]
        List of detection confidences concerning objects on the image being processed.
    img : numpy.ndarray
        The image being processed.
    """
    global __detect, __detect_old
    font = cv2.FONT_HERSHEY_DUPLEX
    __detect = len(boxes) != 0
    # If something is newly detected (rising edge)
    if __detect and not __detect_old:
        for i in range(len(boxes)):
            if i in indexes:
                logging.info(
                    "[AI] {} detected with a probability of: {:.2f} %".format(
                        __object_detection_id.name, confidences[i] * 100
                    )
                )

                stateMachinePanel.signal(gpio_led)

                x, y, w, h = boxes[i]
                confidence_label = int(confidences[i] * 100)
                cv2.rectangle(img, (x, y), (x + w, y + h), __output_color, 2)
                cv2.putText(
                    img, f"{__object_detection_id.name, confidence_label}", (x - 25, y + 75), font, 2, __output_color, 2
                )
    # Else if something is not detected but it was before (falling edge)
    elif __detect_old and not __detect:
        stateMachinePanel.end_signal(gpio_led)
    __detect_old = __detect

    return img
