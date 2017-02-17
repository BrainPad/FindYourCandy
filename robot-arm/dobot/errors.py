# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals


class TimeoutError(Exception):
    pass


class DeviceNotFound(IOError):
    pass


class PacketParseError(IOError):
    pass
