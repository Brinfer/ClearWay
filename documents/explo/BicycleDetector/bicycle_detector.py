# opencv object tracking
# object detection and tracking opencv
import cv2
import numpy as np
import os
from imutils.video import VideoStream
import imutils
import time

# Load Yolo
yolo_weight = "yolov3_320.weights"
yolo_config = "yolov3_320.cfg"
net = cv2.dnn.readNet(yolo_weight, yolo_config)
label = "bicycle"
color = np.random.uniform(0, 255, size=3)
# Find names of all layers of the YOLO model architecture
layer_names = net.getLayerNames()
# Find names of three output layers (['yolo_82', 'yolo_94', 'yolo_106'])
output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

vs = VideoStream(usePiCamera=True).start()
# Very important! Otherwize, vs.read() gives a NonType
time.sleep(2.0)

while True:
    img = vs.read()

    # get dimensions of image
    height = img.shape[0]
    width = img.shape[1]

    #orig = imutils.resize(orig, width=500)
    # Detecting objects
    #scalefactor of 1/255 to scale the pixel values to [0..1]
    blob = cv2.dnn.blobFromImage(img, scalefactor=1/255, size=(320,320), mean=(0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)
    # Send Blob image data to the three output layers
    outs = net.forward(output_layers)

    confidences = []
    boxes = []

    ##table of 85 columns for the 3 output layers: outs[0] (507 rows), outs[1] (2028 rows) et outs[2] (8112 rows)
    #for each row: Cx, Cy, w, h, confidence + probability for each class
    for out in outs:
        for detection in out:
            #bicycle
            confidence = detection[5]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                #boxes: [[270, 91, 342, 347]]
                boxes.append([x, y, w, h])
                #confidences: [0.991836428642273]
                confidences.append(float(confidence))

    #To remove multiple boxes that refer to the same object and keep one by Non Maximum Supression
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw bounding box with text for each object
    font = cv2.FONT_HERSHEY_DUPLEX
    for i in range(len(boxes)):
        if i in indexes:
            print("Vélo détecté avec une probabilité de : {:.2f} %".format(confidences[i]*100))
            x, y, w, h = boxes[i]
            confidence_label = int(confidences[i] * 100)
            cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv2.putText(img, f'{label, confidence_label}', (x-25, y + 75), font, 2, color, 2)

    cv2.imshow("Image", img)
    # Close video window by pressing 'x'
    if cv2.waitKey(1) & 0xFF == ord('x'):
        break
    
    #sortie.write(img)

vs.stop()
cv2.destroyAllWindows()
