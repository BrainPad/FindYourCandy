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

import cmd

from dobot.client import Dobot

DEFAULT_BAUDRATE = 115200


class DobotCUI(cmd.Cmd):
    prompt = "> "
    intro = "============ dobot cui ============"

    def __init__(self, dobot):
        cmd.Cmd.__init__(self)
        self.dobot = dobot

    def do_init(self, _):
        print("initializing dobot")
        self.dobot.initialize()
        self.dobot.wait()

    def do_move(self, line):
        print(line)
        args = line.split(' ')
        self.dobot.move(float(args[0]), float(args[1]), float(args[2]))

    def do_lmove(self, line):
        print(line)
        args = line.split(' ')
        self.dobot.linear_move(float(args[0]), float(args[1]), float(args[2]))

    def do_getpose(self, _):
        print(self.dobot.get_pose())

    # todo: キャリブレーション用コマンド

    def do_EOF(self, _):
        self.dobot.close()
        return True

if __name__ == '__main__':
    c = DobotCUI(Dobot('/dev/ttyUSB0', DEFAULT_BAUDRATE))
    c.cmdloop()
