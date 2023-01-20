# import cv2 as cv
# import numpy as np
# import time

# # img = cv.imread('images/horse.jpg')
# img = cv.imread("C:\\Users\\Brandon\\Documents\\Personal_Projects\\tik_tb_vid_big_data\\test_pics\\fg_off_center.JPG")
# cv.imshow('window',  img)
# cv.waitKey(1)

from pathlib import Path


p = "C:/p/tik_tb_vid_big_data/working/bottom__time_trimmed.mp4"


def file_not_exist_msg(file_path):
    if Path(file_path).exists():
        return False
    return f"ERROR: File doesn't exist: {file_path}"


if not_exist_msg(p): raise Exception(not_exist_msg(p))
print("Done")