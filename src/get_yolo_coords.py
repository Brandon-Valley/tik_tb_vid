# To use AI to find the interesting part of a frame, you can use a pre-trained object detection model such as YOLO (You Only Look Once). YOLO is a fast object detection model that can identify multiple objects in an image and predict their bounding boxes.

# Here is an example of how you can use YOLO to find the interesting part of a frame:


# This code loads the YOLO model, reads an input frame, and uses the model to predict the bounding boxes and confidence scores for each object in the frame. Then, it applies non-maximum suppression to suppress weak and overlapping bounding boxes and finds the most interesting one based on the confidence scores. Finally, it crops the frame to

import cv2
import numpy as np

# Load the YOLO model
net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")

# Read the input frame
frame = cv2.imread("C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\test_pics\\fg_off_center.JPG")

# Get the height and width of the frame
height, width = frame.shape[:2]

# Create a blob from the frame
blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), (0, 0, 0), True, crop=False)

# Set the input to the YOLO model
net.setInput(blob)

# Get the output from the YOLO model
output_layers = net.forward(net.getUnconnectedOutLayersNames())

# Initialize the bounding box coordinates and confidence scores
boxes = []
confidences = []

# Loop through the output layers and extract the bounding boxes and confidence scores
for output in output_layers:
    for detection in output:
        scores = detection[5:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]
        if confidence > 0.5:
            center_x = int(detection[0] * width)
            center_y = int(detection[1] * height)
            w = int(detection[2] * width)
            h = int(detection[3] * height)
            x = center_x - w // 2
            y = center_y - h // 2
            boxes.append([x, y, w, h])
            confidences.append(float(confidence))

# Apply non-maximum suppression to suppress weak and overlapping bounding boxes
indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

# Initialize the interesting part of the frame
x, y, w, h = 0, 0, 0, 0

# Loop through the bounding boxes and find the most interesting one
for i in indices:
    i = i[0]
    box = boxes[i]
    x, y, w, h = box[0], box[1], box[2], box[3]
    # You can add additional criteria here to select the most interesting bounding box

# Crop the frame to show only the interesting part
frame = frame[y:y+h, x:x+w]

# Show the resulting frame
cv2.imshow("Frame", frame)
cv2.waitKey(0)