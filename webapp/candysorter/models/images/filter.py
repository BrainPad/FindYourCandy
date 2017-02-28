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

import numpy as np


def _rx_to_ax(x_robot):
    x = round(x_robot, 1)
    return int((x + 1.0) * 10)


def _ry_to_ay(y_robot):
    y = round(y_robot, 1)
    return int((y + 1.5) * 10)


def _pickable_coords():
    c = np.ones((31, 21), dtype=bool)
    c[_ry_to_ay(-1.2):_ry_to_ay(1.2) + 1, _rx_to_ax(-1.0)] = False
    c[_ry_to_ay(-1.1):_ry_to_ay(1.1) + 1, _rx_to_ax(-0.9)] = False
    c[_ry_to_ay(-1.0):_ry_to_ay(1.0) + 1, _rx_to_ax(-0.8)] = False
    c[_ry_to_ay(-0.9):_ry_to_ay(0.9) + 1, _rx_to_ax(-0.7)] = False
    c[_ry_to_ay(-0.8):_ry_to_ay(0.8) + 1, _rx_to_ax(-0.6)] = False
    c[_ry_to_ay(-0.6):_ry_to_ay(0.6) + 1, _rx_to_ax(-0.5)] = False
    c[_ry_to_ay(-0.3):_ry_to_ay(0.3) + 1, _rx_to_ax(-0.4)] = False
    c[:_ry_to_ay(-1.4) + 1, _rx_to_ax(0.5)], c[_rx_to_ax(1.4):, _rx_to_ax(0.5)] = False, False
    c[:_ry_to_ay(-1.2) + 1, _rx_to_ax(0.6)], c[_rx_to_ax(1.2):, _rx_to_ax(0.6)] = False, False
    c[:_ry_to_ay(-1.0) + 1, _rx_to_ax(0.7)], c[_rx_to_ax(1.0):, _rx_to_ax(0.7)] = False, False
    c[:_ry_to_ay(-0.6) + 1, _rx_to_ax(0.8)], c[_rx_to_ax(0.6):, _rx_to_ax(0.8)] = False, False
    c[:, _rx_to_ax(0.9)] = False
    c[:, _rx_to_ax(1.0)] = False
    return c


_PICKABLE_COORDS = _pickable_coords()


def _pickable(x_robot, y_robot):
    x_array = _rx_to_ax(x_robot)
    y_array = _ry_to_ay(y_robot)
    return (
        0 <= x_array < _PICKABLE_COORDS.shape[1] and
        0 <= y_array < _PICKABLE_COORDS.shape[0] and
        _PICKABLE_COORDS[y_array, x_array]
    )


def exclude_unpickables(calibrator, candies):
    l = []
    for c in candies:
        x, y = calibrator.get_coordinate(c.box_centroid[0], c.box_centroid[1])
        if not _pickable(x, y):
            continue
        l.append(c)
    return l
