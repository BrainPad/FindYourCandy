# -*- coding: utf-8 -*-
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
import json
import numpy

class AdjustForPictureToRobot(object):

    def __init__(self):

        in_data_json = os.path.join(os.path.dirname(__file__), 'adjust_data.json')
        if not os.path.isfile(in_data_json):
            self.make_adjust_data()

        try:
            in_data = open(in_data_json).read()
        except Exception as e:
            raise e
        self.adjust_data = json.loads(in_data)

    def make_adjust_data(self):

        try:
            in_meas_json = os.path.join(os.path.dirname(__file__), 'adjust_measurement.json')
            in_data = open(in_meas_json).read()
        except Exception as e:
            raise e
        measurement = json.loads(in_data)

        from_point = numpy.array([[-0.3, 1.5, 1],
                                  [-0.3, -1.5, 1],
                                  [0.3, 0, 1]])

        to_point = numpy.array([[measurement['-0.3,1.5']['x'], measurement['-0.3,1.5']['y'], 1],
                                [measurement['-0.3,-1.5']['x'], measurement['-0.3,-1.5']['y'], 1],
                                [measurement['0.3,0']['x'], measurement['0.3,0']['y'], 1]])

        inv_to_point = numpy.linalg.inv(to_point.T)

        trans = numpy.dot(from_point.T, inv_to_point)

        out_data = {}

        for key, value in sorted(measurement.items()):

            x_in, y_in = key.split(',')
            x_picture = float(x_in)
            y_picture = float(y_in)

            new_key = '%s,%s' % (round(x_picture, 1), round(y_picture, 1))

            if value:

                x_robot = value['x']
                y_robot = value['y']

                temp_point = numpy.dot(numpy.array([x_robot, y_robot, 1]), trans.T)
                x_picture_conv = float(temp_point[0])
                y_picture_conv = float(temp_point[1])

                x_picture_diff = float(x_picture - x_picture_conv)
                y_picture_diff = float(y_picture - y_picture_conv)

                out_data.update({new_key: {'x_picture': x_picture,
                                           'x_picture_conv': x_picture_conv,
                                           'x_picture_diff': x_picture_diff,
                                           'x_robot': x_robot,
                                           'y_picture': y_picture,
                                           'y_picture_conv': y_picture_conv,
                                           'y_picture_diff': y_picture_diff,
                                           'y_robot': y_robot}})
            else:
                out_data.update({new_key: None})

        try:
            out_data_json = os.path.join(os.path.dirname(__file__), 'adjust_data.json')
            f = open(out_data_json, 'w')
            f.write(json.dumps(out_data, sort_keys=True, indent=4))
            f.close()
        except Exception as e:
            raise e

    def adjust(self, x, y):

        if -1 <= x <= 1 and -1.5 <= y <= 1.5:
            pass
        else:
            message = "Error: x=%s y=%s coordinate is out of range in sheet." % (x, y)
            raise Exception(message)

        x_round = round(x, 1)
        y_round = round(y, 1)

        if x_round == -0.0:
            x_round = 0.0

        if y_round == -0.0:
            y_round = 0.0

        key = '%s,%s' % (x_round, y_round)

        try:
            self.adjust_data[key]
        except:
            message = "Error: x=%s y=%s coordinate is out of range in robot arm." % (x_round, y_round)
            raise Exception(message)

        x_diff = self.adjust_data[key]['x_picture_diff']
        y_diff = self.adjust_data[key]['y_picture_diff']

        x_adjust = x - x_diff
        y_adjust = y - y_diff

        return x_adjust, y_adjust
