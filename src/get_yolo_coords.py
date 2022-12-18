# To use AI to find the interesting part of a frame, you can use a pre-trained object detection model such as YOLO (You Only Look Once). YOLO is a fast object detection model that can identify multiple objects in an image and predict their bounding boxes.

# Here is an example of how you can use YOLO to find the interesting part of a frame:


# This code loads the YOLO model, reads an input frame, and uses the model to predict the bounding boxes and confidence scores for each object in the frame. Then, it applies non-maximum suppression to suppress weak and overlapping bounding boxes and finds the most interesting one based on the confidence scores. Finally, it crops the frame to

import cv2
# import numpy as np
# import os



# import cv2 as cv
import numpy as np
import time
import os


SCRIPT_PARENT_DIR_PATH = os.path.abspath(os.path.dirname(__file__)) # src
REPO_ROOT_DIR_PATH = os.path.dirname(SCRIPT_PARENT_DIR_PATH)
BIG_DATA_DIR_PATH = os.path.join(os.path.dirname(REPO_ROOT_DIR_PATH), "tik_tb_vid_big_data")
BIG_DATA_IGNORE_DIR_PATH = os.path.join(os.path.dirname(BIG_DATA_DIR_PATH), "ignore")
BIG_DATA_TEST_PICS_DIR_PATH = os.path.join(os.path.dirname(BIG_DATA_DIR_PATH), "test_pics")

TEST_IMG_PATH = os.path.join(BIG_DATA_TEST_PICS_DIR_PATH, "fg_off_center.JPG")

CFG_PATH = os.path.join(SCRIPT_PARENT_DIR_PATH, "yolov3.cfg")
WEIGHTS_PATH = os.path.join(BIG_DATA_IGNORE_DIR_PATH, "yolov3.weights")
print(f"{WEIGHTS_PATH}")
print(f"{CFG_PATH}")



# # img = cv.imread(TEST_IMG_PATH)
# # img = cv.imread(os.path.abspath("\\C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\test_pics\\fg_off_center.jpg"))
# # img = cv.imread(os.path.abspath(img = cv.imread("C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\test_pics\\fg_off_center.JPG")))
# img = cv.imread("C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\test_pics\\fg_off_center.JPG")
# # img = cv.imread('images/horse.jpg')
# cv.imshow('window',  img)
# cv.waitKey(1)

# # Give the configuration and weight files for the model and load the network.
# # net = cv.dnn.readNetFromDarknet('yolov3.cfg', 'yolov3.weights')
# net = cv.dnn.readNetFromDarknet(CFG_PATH, "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\ignore\\yolov3.weights")

# net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
# # net.setPreferableTarget(cv.dnn.DNN_TARGET_CPU)

# ln = net.getLayerNames()
# print(len(ln), ln)

# # construct a blob from the image
# blob = cv.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
# r = blob[0, 0, :, :]

# cv.imshow('blob', r)
# text = f'Blob shape={blob.shape}'
# # cv.displayOverlay('blob', text)
# cv.waitKey(1)

# net.setInput(blob)
# t0 = time.time()
# outputs = net.forward(ln)
# t = time.time()

# # cv.displayOverlay('window', f'forward propagation time={t-t0}')
# cv.imshow('window',  img)
# cv.waitKey(0)
# cv.destroyAllWindows()






# Load the YOLO model
# net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")
# net = cv2.dnn.readNetFromDarknet(CFG_PATH, WEIGHTS_PATH)
net = cv2.dnn.readNetFromDarknet(CFG_PATH, "C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\ignore\\yolov3.weights")

# Read the input frame
# frame = cv2.imread(os.path.abspath("\\C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\test_pics\\fg_off_center.jpg"))
# frame = cv2.imread("C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\test_pics\\fg_off_center.JPG")
frame = cv2.imread("C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\test_pics\\fg_credits_center.JPG")
cv2.imshow('window',  frame)
cv2.waitKey(1)
# frame = cv2.imread(TEST_IMG_PATH)

# Get the height and width of the frame
height, width = frame.shape[:2]
print("hw = ", height, width)

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
        # print(f"{detection=}")
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

print(f"{boxes=}")
print(f"{confidences=}")

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

print('crop to coords: ', [y+h, x+w])
# Crop the frame to show only the interesting part
frame = frame[y:y+h, x:x+w]

# Show the resulting frame
cv2.imshow("Frame", frame)
cv2.waitKey(0)