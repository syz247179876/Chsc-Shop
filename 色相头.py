# -*- coding: utf-8 -*- 
# @Time : 2020/5/14 20:22 
# @Author : 司云中 
# @File : 色相头.py 
# @Software: PyCharm

import cv2

import os

# 打开摄像头
capture = cv2.VideoCapture(0)
while True:

    # ret为是否拍摄成功，frame为图片
    ret, frame = capture.read()

    # 对图片frame转为二进制
    frame_data = cv2.imencode('.png', frame)[1].tobytes()

    cv2.imshow('face', frame)

    if cv2.waitKey(1) == ord('q'):
        os.kill(os.getpid(), 9)
