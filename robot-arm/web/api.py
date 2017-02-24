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

from flask import Blueprint, jsonify, request, current_app

from dobot.client import Dobot

DEFAULT_BAUDRATE = 115200

api = Blueprint('dobot', __name__)


def get_dobot(port):
    return Dobot(port, DEFAULT_BAUDRATE)


@api.route("/init", methods=['POST'])
def initialize():
    dobot = get_dobot(current_app.config['DOBOT_SERIAL_PORT'])
    dobot.initialize()
    dobot.wait()
    dobot.close()

    return jsonify()


@api.route("/pickup", methods=['POST'])
def pickup():
    body = request.get_json(silent=True)
    x = float(body["x"])
    y = float(body["y"])

    cfg = current_app.config

    cv = cfg['DOBOT_COORDINATE_CONVERTER']

    dest = cfg['DOBOT_SERVE_XY']
    z_high = cfg['DOBOT_Z_HIGH']
    z_low = cfg['DOBOT_Z_LOW']
    v = cfg['DOBOT_MAX_VELOCITY']
    a = cfg['DOBOT_MAX_ACCERALATION']

    xy_conv = cv.convert(x, y)

    dobot = get_dobot(current_app.config['DOBOT_SERIAL_PORT'])
    dobot.adjust_z(z_high)
    dobot.pickup(xy_conv[0], xy_conv[1], z_low=z_low, z_high=z_high, velocity=v, accel=a)
    dobot.move(dest[0], dest[1], 0,  velocity=v, accel=a)
    dobot.pump(0)
    dobot.close()

    return jsonify()


@api.route("/status", methods=['GET'])
def get_state():
    dobot = get_dobot(current_app.config['DOBOT_SERIAL_PORT'])
    status = {}

    pose = dobot.get_pose()
    status["queue_count"] = dobot.count_queued_command()
    dobot.close()

    for key in ['x', 'y', 'z', 'r', 'basement', 'fore', 'rear', 'end']:
        status[key] = pose[key]

    return jsonify(status)
