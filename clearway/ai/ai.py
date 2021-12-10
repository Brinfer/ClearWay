"""OpenCV object detection using picamera."""
import time
import logging
from enum import IntEnum, auto, unique
import os

from imutils.video import VideoStream
from imutils.video import FPS
import cv2
from clearway.gpio import stateMachinePanel


@unique
class _IdYoloOutputLayer(IntEnum):
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


class Ai:
    """[summary].

    Returns
    -------
    [type]
        [description]
    """

    # Class variables shared by all instances
    __object_detection_id = _IdYoloOutputLayer.BICYCLE
    __output_color = (0, 0, 255)  # Blue
    __prob_threshold = 0.5
    __object_detection_counter = 0
    __font = cv2.FONT_HERSHEY_DUPLEX

    def __init__(self, yolo_weights, yolo_cfg, path_to_input_video=None, path_to_output_video=None) -> None:
        """Get the three output layers of YOLO and start the video stream.

        Parameters
        ----------
        path_to_input_video : string, optional
            The path to the input video that is going to be processed, by default None.
        """
        # Read the deep learning network Yolo
        self.__network = cv2.dnn.readNet(yolo_weights, yolo_cfg)
        # Find names of all layers of the YOLO model architecture
        layer_names = self.__network.getLayerNames()
        self.__output_layers = [layer_names[i[0] - 1] for i in self.__network.getUnconnectedOutLayers()]

        self.__path_to_input_video = path_to_input_video
        self.__path_to_output_video = path_to_output_video
        self.__detect_old = False

        if self.__path_to_input_video is None:
            self.__video_stream = VideoStream(usePiCamera=True).start()
            # Very important! Otherwise, video_stream.read() gives a NonType
            time.sleep(2.0)
            logging.info("[AI] Camera ready to detect")
        else:
            self.__video_stream = cv2.VideoCapture(path_to_input_video)
            # self.__video_stream = cv2.VideoCapture("/dev/video0")

        if self.__path_to_output_video is not None:
            output_video_file = os.path.join(path_to_output_video, "video_processed.mp4")
            x_shape = int(self.__video_stream.get(cv2.CAP_PROP_FRAME_WIDTH))
            y_shape = int(self.__video_stream.get(cv2.CAP_PROP_FRAME_HEIGHT))
            four_cc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
            self.__output_video = cv2.VideoWriter(output_video_file, four_cc, fps=15, frameSize=(x_shape, y_shape))

    def bicycle_detector(self, gpio_led) -> None:
        """Detect cyclists on a video stream frame by frame.

        Get the video stream from the Raspberry Pi camera.
        Process the stream to detect cyclists using a YOLO algorithm and the openCV library.
        """
        start_time = time.time()

        # Start the frames per second
        fps = FPS().start()

        if self.__path_to_input_video is None:
            read_ok = True
            img = self.__video_stream.read()
        else:
            read_ok, img = self.__video_stream.read()

        while read_ok:
            # Get dimensions of image
            height, width, channels = img.shape

            # Convert image to Blob
            # Scalefactor of 1/255 to scale the pixel values to [0..1]
            blob = cv2.dnn.blobFromImage(
                img, scalefactor=1 / 255, size=(320, 320), mean=(0, 0, 0), swapRB=True, crop=False
            )
            # Set input for YOLO object detection
            self.__network.setInput(blob)
            # Send Blob image data to the three output layers
            outs = self.__network.forward(self.__output_layers)

            confidences = []
            boxes = []

            # Table of 85 columns for the 3 output layers: outs[0] (507 rows), outs[1] (2028 r) et outs[2] (8112 r)
            # For each row: Cx, Cy, w, h, confidence + probability for each class
            for out in outs:
                for detection in out:
                    confidence = detection[Ai.__object_detection_id]
                    if confidence > Ai.__prob_threshold:
                        # Object detected
                        center_x = int(detection[_IdYoloOutputLayer.CENTER_X] * width)
                        center_y = int(detection[_IdYoloOutputLayer.CENTER_Y] * height)
                        w = int(detection[_IdYoloOutputLayer.WIDTH] * width)
                        h = int(detection[_IdYoloOutputLayer.HEIGHT] * height)
                        # Rectangle coordinates
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))

            # To remove multiple boxes that refer to the same object and keep one by Non Maximum Supression
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.5, nms_threshold=0.4)

            img = Ai.dram_boxes_and_call_state_machine(self, indexes, boxes, confidences, img, gpio_led)

            # Update the FPS counter
            fps.update()

            cv2.imshow("Image", img)
            # Close video window by pressing 'x'
            if cv2.waitKey(1) & 0xFF == ord("x"):
                break

            # Write the image to the output video
            if self.__path_to_output_video is not None:
                self.__output_video.write(img)

            # Read the next frame
            if self.__path_to_input_video is None:
                img = self.__video_stream.read()
            else:
                read_ok, img = self.__video_stream.read()

        # Stop the timer and display FPS information
        fps.stop()
        program_time = time.time() - start_time
        logging.debug("--- {:.2f} seconds ---".format(program_time))
        logging.debug("[IA] elapsed time: {:.2f}".format(fps.elapsed()))
        logging.debug("[IA] approx. FPS: {:.2f}".format(fps.fps()))
        logging.debug("[IA] Nb of object detected: " + str(Ai.__object_detection_counter))

        if self.__path_to_input_video is None:
            self.__video_stream.stop()

    def dram_boxes_and_call_state_machine(self, indexes, boxes, confidences, img, gpio_led):
        """Draw boxes around object detected and inform the gpio stateMachinePanel if a cyclist is detected or not.

        Parameters
        ----------
        indexes : [[int]]
            List of object indexes used to remove multiple boxes that refer to the same object.
        boxes : [[int]]
            List of boxes with their information (center_x, center_y, width, height).
        confidences : int[]
            List of detection confidences concerning objects on the image being processed.
        img : numpy.ndarray
            The image being processed.
        """
        detect = len(boxes) != 0
        # If something is newly detected (rising edge)
        if detect and not self.__detect_old:
            Ai._detect_old = True
            for i in range(len(boxes)):
                if i in indexes:
                    Ai.__object_detection_counter += 1
                    logging.info(
                        "[AI] {} detected with a probability of: {:.2f} %".format(
                            Ai.__object_detection_id.name, confidences[i] * 100
                        )
                    )

                    stateMachinePanel.signal(gpio_led)

                    if self.__path_to_output_video is not None:
                        x, y, w, h = boxes[i]
                        confidence_label = int(confidences[i] * 100)
                        cv2.rectangle(img, (x, y), (x + w, y + h), Ai.__output_color, 2)
                        cv2.putText(
                            img,
                            f"{Ai.__object_detection_id.name, confidence_label}",
                            (x - 25, y + 75),
                            Ai.__font,
                            2,
                            Ai.__output_color,
                            2,
                        )
        # Else if something is not detected but it was before (falling edge)
        elif self.__detect_old and not detect:
            self.__detect_old = False
            stateMachinePanel.end_signal(gpio_led)

        return img
