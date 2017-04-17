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

import argparse

from web.app import create_app
from dobot.utils import detect_dobot_port, dobot_is_on_port

DEFAULT_BAUDRATE = 115200

parser = argparse.ArgumentParser(description='Run Dobot WebAPI.')
parser.add_argument('--port', type=int, default=18001)
parser.add_argument('--host', type=str, default='0.0.0.0')
parser.add_argument('--dobot-port', type=str, default=None)
parser.add_argument('--tuner-file', type=str, default='/var/tmp/robot_tuner.dat')
parser.add_argument('--instance_path', type=str, default=None)

args = parser.parse_args()

if not args.dobot_port:
    dobot_port = detect_dobot_port(DEFAULT_BAUDRATE)
    if dobot_port is None:
        print('dobot offline')
        exit(1)
else:
    dobot_port = args.dobot_port
    if not dobot_is_on_port(dobot_port, DEFAULT_BAUDRATE):
        print('dobot is not detected on port {}'.format(dobot_port))
        exit(1)

app = create_app(dobot_port, args.tuner_file, args.instance_path)

if __name__ == '__main__':
    app.run(port=args.port, host=args.host)
