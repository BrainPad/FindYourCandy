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

import serial

from dobot.errors import TimeoutError

logger = logging.getLogger(__name__)
QUEUE_SIZE = 32


def dump_hex(s):
    return ":".join("{:02x}".format(ord(c)) for c in s)


class SerialCommunicator(object):
    def __init__(self, port, baudrate, read_timeout_sec=10, serial_timeout_sec=5):
        self.serial = serial.Serial(port, baudrate, timeout=serial_timeout_sec)
        self.timeout_sec = read_timeout_sec

    def call(self, cmd):
        buf_out = cmd.build_packet()
        self.serial.write(buf_out)
        logger.debug("> {}".format(dump_hex(buf_out)))

        start_time = time.time()
        while self.serial.inWaiting() == 0:
            time.sleep(0.5)
            elapsed_sec = time.time() - start_time
            if elapsed_sec > self.timeout_sec:
                raise TimeoutError("timeout when waiting for return packet")

        bytes_to_read = self.serial.inWaiting()
        buf_in = self.serial.read(bytes_to_read)
        logger.debug("< {}".format(dump_hex(buf_in)))

        return cmd.parse_packet(buf_in)

    def close(self):
        self.serial.close()
