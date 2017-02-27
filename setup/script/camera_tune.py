# Copyright 2017 BrainPad Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import cv2
import sys
import time

sys.path.append('../../webapp')
from candysorter.models.images.calibrate import ImageCalibrator


calibrator = ImageCalibrator(area=(1100, 1625), scale=550)

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


# Attempt to display using cv2
cv2.namedWindow('Tuning Camera',cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
cv2.resizeWindow('Tuning Camera', 960, 540)
cv2.setMouseCallback('Tuning Camera', mouse_event)


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
