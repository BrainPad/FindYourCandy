# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import serial

from dobot import command
from dobot.serial import logger, SerialCommunicator


def detect_dobot_port(baudrate):
    found_port = detect_ports(baudrate)
    dobot_port = None
    for port in found_port:
        if dobot_is_on_port(port, baudrate):
            dobot_port = port

    return dobot_port


def detect_ports(baudrate):
    port_prefix = '/dev/ttyUSB'
    found_ports = []
    for i in range(5):
        port = port_prefix + str(i)
        logger.debug('scanning port: {}'.format(port))
        try:
            s = serial.Serial(port, baudrate, timeout=1)
            s.close()
        except serial.SerialException:
            continue
        found_ports.append(port)
    return found_ports


def dobot_is_on_port(port, baudrate):
    try:
        ser = SerialCommunicator(port, baudrate)
        ser.call(command.GetPose())
    except IOError as e:
        print(e)
        return False
    return True
