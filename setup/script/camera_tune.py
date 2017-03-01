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

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import time

import cv2
import numpy as np

sys.path.append('../../webapp')

from candysorter.models.images.calibrate import ImageCalibrator
from candysorter.models.images.detect import CandyDetector
from candysorter.config import get_config

calibrator = ImageCalibrator(area=(1625, 1100), scale=550)
detector = CandyDetector.from_config(get_config(os.getenv('FLASK_ENV', 'dev')))

should_exit = False


def mouse_event(event, x, y, flags, param):
    global should_exit
    if event == cv2.EVENT_LBUTTONUP:
        print("mouse_event:L-click")
        should_exit = True


def write_message(image):
    cv2.putText(image, 'Click L-button of mouse to exit', (10, 130), font, 3, (250, 30, 30), 3)


def write_ok(image):
    cv2.putText(image, 'OK', (900, 500), font, 7, (30, 250, 30), 5)


def detect_corners(image):
    try:
        corners = calibrator.detect_corners(image)
    except Exception as e:
        print(e)
        return None
    if len(corners) < 4:
        return None
    return corners


def draw_detection(image):
    candies = detector.detect(image)
    for candy in candies:
        cv2.polylines(image, np.int32([np.array(candy.box_coords)]), isClosed=True, color=(0, 0, 255),
                      lineType=cv2.LINE_AA, thickness=3)


font = cv2.FONT_HERSHEY_PLAIN
capture = cv2.VideoCapture(0)
capture.set(3, 1920)
capture.set(4, 1080)

# Attempt to display using cv2
cv2.namedWindow('Tuning Camera', cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
cv2.resizeWindow('Tuning Camera', 960, 540)
cv2.setMouseCallback('Tuning Camera', mouse_event)

w2_size = (480, 270)
cv2.namedWindow('Detection', cv2.WINDOW_KEEPRATIO | cv2.WINDOW_NORMAL)
cv2.resizeWindow('Detection', *w2_size)
cv2.setMouseCallback('Detection', mouse_event)

while True:
    time.sleep(0.3)
    if capture.isOpened:
        ret, frame = capture.read()
        if not ret:
            break
        corners = detect_corners(frame)
        if corners is not None:
            cropped = calibrator.calibrate(frame)
            draw_detection(cropped)
            cv2.imshow('Detection', cropped)
        else:
            blank = np.zeros((w2_size[1], w2_size[0], 3), np.uint8)
            cv2.imshow('Detection', blank)

        write_message(frame)
        write_ok(frame)
        cv2.imshow('Tuning Camera', frame)
        cv2.waitKey(1)

    if should_exit:
        break

print("Exit.")
cv2.destroyAllWindows()
