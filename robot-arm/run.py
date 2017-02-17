# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse

from web.app import create_app
from dobot.utils import detect_dobot_port, dobot_is_on_port

DEFAULT_BAUDRATE = 115200

parser = argparse.ArgumentParser(description='Run Dobot WebAPI.')
parser.add_argument('--port', type=int, default=8000)
parser.add_argument('--host', type=str, default='0.0.0.0')
parser.add_argument('--dobot-port', type=str, default=None)
parser.add_argument('--tuner-file', type=str, default='/tmp/robot_tuner.dat')

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

app = create_app(dobot_port, args.tuner_file)

if __name__ == '__main__':
    app.run(port=args.port, host=args.host)
