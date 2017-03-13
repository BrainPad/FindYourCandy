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

import json
import numpy as np

from calibration.adjust import AdjustForPictureToRobot


class CoordinateConverter(object):
    def __init__(self, from_points, to_points, z_low=-69):
        """
        find T that meets x_robot = T x_logical
        """

        self.mat_x_from = np.array([[from_points[0][0], from_points[0][1], 1],
                                    [from_points[1][0], from_points[1][1], 1],
                                    [from_points[2][0], from_points[2][1], 1]])

        self.mat_x_to = np.array([[to_points[0][0], to_points[0][1], 1],
                                  [to_points[1][0], to_points[1][1], 1],
                                  [to_points[2][0], to_points[2][1], 1]])

        inv_x = np.linalg.inv(self.mat_x_from.T)

        self.mat_transform = np.dot(self.mat_x_to.T, inv_x)
        self.z_low = z_low

    def convert(self, x, y):
        xy_trans = AdjustForPictureToRobot()
        x, y = xy_trans.adjust(x, y)

        from_vector = np.array([x, y, 1])
        transformed = np.dot(from_vector, self.mat_transform.T)

        return transformed[0], transformed[1]

    @classmethod
    def from_tuning_file(cls, file_, z_low_pad=5):
        tuner_data = []
        with open(file_, 'r') as readfile:
            for line in readfile:
                if not line:
                    break
                data = json.loads(line)
                tuner_data.append(data)

        z_low = sum([d['z'] for d in tuner_data])/3 + z_low_pad
        return cls(
            [(-0.3, 1.5), (-0.3, -1.5), (0.3, 0)],
            [(tuner_data[0]['x'], tuner_data[0]['y']),
             (tuner_data[1]['x'], tuner_data[1]['y']),
             (tuner_data[2]['x'], tuner_data[2]['y'])],
            z_low=z_low
        )
