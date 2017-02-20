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

import struct
import logging
from collections import OrderedDict

from dobot.errors import PacketParseError

logger = logging.getLogger(__name__)


class Command(object):
    def __init__(self, id_, rw, is_queued, param_format=None, param_names=None):
        """

        Args:
            id_(int): dobot protocol command id
            rw(int): 0 or 1. dobot protocol rw
            is_queued(int): 0 or 1. dobot protocol is_queued
            param_format(unicode): param binary format
            param_names(list of unicode): param names
        """
        self.builder = PacketBuilder(id_, rw, is_queued)
        self.parser = None
        self.params = None
        if param_format:
            self.parser = PacketParser(param_format, param_names)

    def build_packet(self):
        return self.builder.build(self.params)

    def parse_packet(self, return_packet):
        if self.parser is None:
            return None
        if self.parser.param_names is None:
            return self.parser.parse(return_packet)
        return self.parser.parse_to_dict(return_packet)


class PacketBuilder(object):
    def __init__(self, id_, rw, is_queued):
        self.cmd_id = id_
        self.ctrl = ctrl(rw, is_queued)
        self.params = None

    def build(self, params):
        """
         Header(2bytes), Len(1byte), ID(1byte), ctrl(1byte), Params, Checksum(1byte)
        """
        payload = self._payload(params)
        payload_len = len(payload)

        # header, payload, checksum
        pkt = struct.pack('<HB', 0xAAAA, payload_len)
        pkt += payload
        pkt += struct.pack('<B', checksum(payload))

        return pkt

    def _payload(self, params):
        pl = struct.pack('<BB', self.cmd_id, self.ctrl)
        if params is not None:
            pl += params
        return pl


class PacketParser(object):
    def __init__(self, param_format, param_names=None):
        self.param_format = param_format
        self.param_names = param_names

    def parse(self, packet):
        try:
            parsed = struct.unpack("<HBBB" + self.param_format + "B", packet)
        except struct.error as e:
            raise PacketParseError(e.message)

        return parsed

    def parse_to_dict(self, packet):
        d = OrderedDict()
        names = ['header', 'len', 'id', 'ctrl'] + self.param_names + ['checksum']
        for i, name in enumerate(names):
            d[name] = self.parse(packet)[i]

        return d


def checksum(payload):
    return 0xFF & (0x100 - (sum([ord(c) for c in payload])))


def ctrl(rw, is_queued):
    """
    rw(byte0), isQueued(byte1)
    """
    c = 0
    c |= rw & 0x01
    c |= (is_queued << 1) & 0x02
    return c


####################################################
# dobot command definition                         #
####################################################


class GetPose(Command):
    def __init__(self):
        super(GetPose, self).__init__(
            10, 0, 0, '8f', ['x', 'y', 'z', 'r', 'basement', 'rear', 'fore', 'end']
        )


class GetAlarmsState(Command):
    def __init__(self):
        super(GetAlarmsState, self).__init__(20, 0, 0)


class ClearAllAlarmsState(Command):
    def __init__(self):
        super(ClearAllAlarmsState, self).__init__(21, 1, 0)


class SetHomeCmd(Command):
    def __init__(self):
        super(SetHomeCmd, self).__init__(31, 1, 1)
        self.params = struct.pack('I', 0)


class SetPTPJointParams(Command):
    def __init__(self, v_basement, v_rear, v_fore, v_end, a_basement, a_rear, a_fore, a_end, is_queued=True):
        params_fmt = None
        params_name = None
        if is_queued:
            params_fmt = 'Q'
            params_name = ['queuedCmdIndex']

        super(SetPTPJointParams, self).__init__(
            80, 1, 1 if is_queued else 0, params_fmt, params_name
        )
        self.params = struct.pack('8f', v_basement, v_rear, v_fore, v_end, a_basement, a_rear, a_fore, a_end)


class GetPTPJointParams(Command):
    def __init__(self):
        super(GetPTPJointParams, self).__init__(
            80, 0, 0, '8f', ['v_basement', 'v_rear', 'v_fore', 'v_end', 'a_basement', 'a_rear', 'a_fore', 'a_end']
        )


class SetPTPCoordinateParams(Command):
    def __init__(self, v_xyz, v_r, acc_xyz, acc_r, is_queued=True):
        params_fmt = None
        params_name = None
        if is_queued:
            params_fmt = 'Q'
            params_name = ['queuedCmdIndex']

        super(SetPTPCoordinateParams, self).__init__(
            81, 1, 1 if is_queued else 0, params_fmt, params_name
        )
        self.params = struct.pack('ffff', v_xyz, v_r, acc_xyz, acc_r)


class GetPTPCoordinateParams(Command):
    def __init__(self):
        super(GetPTPCoordinateParams, self).__init__(
            81, 0, 0, 'ffff', ['v_xyz', 'v_r', 'acc_xyz', 'acc_r']
        )


class SetPTPCmd(Command):
    def __init__(self, ptp_mode, x, y, z, r):
        super(SetPTPCmd, self).__init__(
            84, 1, 1, 'Q', ['queuedCmdIndex']
        )
        self.params = struct.pack('<Bffff', ptp_mode, x, y, z, r)


class SetEndEffectorSuctionCup(Command):
    def __init__(self, is_ctrl_enabled, is_sucked):
        super(SetEndEffectorSuctionCup, self).__init__(62, 1, 1)
        self.params = struct.pack('<BB', is_ctrl_enabled, is_sucked)


class SetQueuedCmdStartExec(Command):
    def __init__(self):
        super(SetQueuedCmdStartExec, self).__init__(240, 1, 0)


class SetQueuedCmdStopExec(Command):
    def __init__(self):
        super(SetQueuedCmdStopExec, self).__init__(241, 1, 0)


class SetQueuedCmdForceStopExec(Command):
    def __init__(self):
        super(SetQueuedCmdForceStopExec, self).__init__(242, 1, 0)


class SetQueuedCmdClear(Command):
    def __init__(self):
        super(SetQueuedCmdClear, self).__init__(245, 1, 0)


class GetQueuedCmdCurrentIndex(Command):
    def __init__(self):
        super(GetQueuedCmdCurrentIndex, self).__init__(246, 0, 0, 'Q', ['queuedCmdCurrentIndex'])


class GetQueuedCmdLeftSpace(Command):
    def __init__(self):
        super(GetQueuedCmdLeftSpace, self).__init__(247, 0, 0, 'L', ['leftSpace'])
