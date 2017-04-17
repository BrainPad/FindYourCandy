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

import cv2
import numpy as np


class ImageCalibrator(object):
    def __init__(self, thres=10, dictionary=cv2.aruco.DICT_6X6_250, area=(1000, 1519), scale=500):
        self.thres = thres
        self.dictionary = cv2.aruco.Dictionary_get(dictionary)
        self.area = area
        self.scale = scale

        self.corner_coords = np.array([
            [0, 0],
            [0, area[1]],
            [area[0], area[1]],
            [area[0], 0]
        ], dtype=np.float32)
        self._prev_valid_corners = None

    @classmethod
    def from_config(cls, config):
        return cls(area=config['IMAGE_CALIBRATOR_AREA'],
                   scale=config['IMAGE_CALIBRATOR_SCALE'])

    def calibrate(self, img):
        corners = self.detect_corners(img)
        transform_matrix = cv2.getPerspectiveTransform(corners, self.corner_coords)
        return cv2.warpPerspective(img, transform_matrix, self.area)

    def detect_corners(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        marker_coords, marker_labels, _ = cv2.aruco.detectMarkers(gray, self.dictionary)
        marker_labels = marker_labels.flatten() if marker_labels is not None else []

        # Can detect
        if len(marker_coords) == 4:
            corners = np.zeros((4, 2), dtype=np.float32)
            for label, coord in zip(marker_labels, marker_coords):
                corners[label] = coord[0, 0]
            self._prev_valid_corners = corners
            return corners

        # Use _prev_valid_corners if exists
        if self._prev_valid_corners is not None:
            # Check the camera is not moved
            for label, coord in zip(marker_labels, marker_coords):
                corner = coord[0, 0]
                if self._norm(self._prev_valid_corners[label], corner) > self.thres:
                    raise RuntimeError('Failed to detect markers and camera was moved.')
            return self._prev_valid_corners

        raise RuntimeError('Failed to detect markers and found no successful record.')

    def get_coordinate(self, x, y):
        return (self.area[1] / 2. - y) / self.scale, (self.area[0] / 2. - x) / self.scale

    @staticmethod
    def _norm(a, b):
        return sum((a - b) ** 2) ** 0.5
