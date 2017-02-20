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

import logging
import time

from dobot import command
from dobot.errors import TimeoutError
from dobot.serial import SerialCommunicator

logger = logging.getLogger(__name__)
DOBOT_QUEUE_SIZE = 32


class Dobot(object):
    def __init__(self, port, baudrate, read_timeout_sec=10, serial_timeout_sec=5):
        self.serial = SerialCommunicator(
            port, baudrate, read_timeout_sec=read_timeout_sec, serial_timeout_sec=serial_timeout_sec
        )

    def get_pose(self):
        return self.serial.call(command.GetPose())

    def wait(self, timeout_sec=120):
        """dobotが内部queueを消費するまでブロック"""
        logger.debug("waiting for dobot to complete commands")
        start_time = time.time()
        while self.count_queued_command() > 0:
            time.sleep(1)
            if time.time() - start_time > timeout_sec:
                raise TimeoutError("timeout when waiting for dobot to complete commands")

    def current_command_id(self):
        # todo
        pass

    def count_queued_command(self):
        result = self.serial.call(command.GetQueuedCmdLeftSpace())
        return DOBOT_QUEUE_SIZE - result['leftSpace']

    def initialize(self):
        self.serial.call(command.ClearAllAlarmsState())
        self.serial.call(command.SetQueuedCmdClear())
        self.serial.call(command.SetHomeCmd())

    def move(self, x, y, z, velocity=200, accel=200, jump=True):
        self.serial.call(command.SetPTPJointParams(velocity, velocity, velocity, velocity, accel, accel, accel, accel))

        mode = 0
        if not jump:
            mode = 1

        self.serial.call(command.SetPTPCmd(mode, x, y, z, 0))

    def linear_move(self, x, y, z, velocity=200, accel=200):
        self.serial.call(command.SetPTPCoordinateParams(velocity, velocity, accel, accel))
        self.serial.call(command.SetPTPCmd(2, x, y, z, 0))

    def pickup(self, x, y, z_low=0, z_high=100, sleep_sec=1, velocity=200, accel=100, num_trials=1):
        self.move(x, y, z_high, velocity, accel)
        self.pump(1)
        for i in range(num_trials):
            self.linear_move(x, y, z_low, velocity, accel)
            time.sleep(sleep_sec)
            self.linear_move(x, y, z_high, velocity, accel)

    def pump(self, on):
        self.serial.call(command.SetEndEffectorSuctionCup(1, on))

    def close(self):
        self.serial.close()
