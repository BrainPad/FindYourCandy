# -*- coding: utf-8 -*-

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
