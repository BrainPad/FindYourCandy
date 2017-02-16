#!/usr/bin/python2
# -*- coding: utf-8 -*-
import cv2
import sys
import time

# TODO: this path should be changed accordingly.
sys.path.append('/home/brainpad/candy-sorter-old/webapp')
from candysorter.models.images.calibrate import ImageCalibrator



'Python needs class definition to make valuables volatile'
class Flag:
  b_exit = False

def mouse_event(event, x, y, flags, param):
  if event == cv2.EVENT_LBUTTONUP:
    print "mouse_event:L-click"
    flag.b_exit = True

def write_message(image):
  #cv2.line(image, (300, 300), (640, 480),(0,255,0), 3)
  cv2.putText(image,'Click L-button of mouse to exit',(10,130),font,3,(250,30,30),3)

def write_OK(image):
  cv2.putText(image,'OK',(900,500),font,7,(30,250,30),5)

def is_OK(image):
  try:
    calibrator = ImageCalibrator(area=(1100, 1625), scale=550)
    #image_check = calibrator.calibrate(image)
    corners = calibrator.detect_corners(image)
    #print corners
  except Exception as e:
    print e
    return False
  if len(corners)<4: 
    return False
  return True
  

flag = Flag()
font = cv2.FONT_HERSHEY_PLAIN
capture =  cv2.VideoCapture(0)
capture.set(3,1920)
capture.set(4,1080)


# Attempt to display using cv2 (doesn't work)
cv2.namedWindow('Tuning Camera',cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
cv2.resizeWindow('Tuning Camera', 960, 540)
cv2.setMouseCallback('Tuning Camera', mouse_event)

#for i in range(0, 10):
while True :
  time.sleep(0.3)
  if ( capture.isOpened ):
    ret, frame = capture.read()
    if not ret:
      break
    if is_OK(frame):
      write_OK(frame)
    write_message(frame)
    cv2.imshow('Tuning Camera', frame)
    cv2.waitKey(1)
  if ( flag.b_exit ):
    break

print "Exit."
cv2.destroyAllWindows()

