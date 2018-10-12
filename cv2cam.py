import numpy as np
import cv2
import time

class camera:
    def __init__():
        self.capture = cv2.VideoCapture(0)
        
    def get_image(self):
        ret, frame = self.capture.read()
        return image
        
    def deinit(self):
        self.capture.release()
        
    def show_img(self,frame):
        cv2.imshow('frame',frame)
        cv2.waitKey(0)

    def save_img(self,frame, name=""):
        timestamp = time.strftime('%Y_%m_%d-%H_%M_%S')
        cv2.imwrite(frame, timestamp + name + ".png")

