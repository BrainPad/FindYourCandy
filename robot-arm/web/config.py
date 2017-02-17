# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os
from calibration.converter import CoordinateConverter


class DefaultConfig(object):
    DEBUG = False

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))

    LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')

    DOBOT_SERIAL_PORT = None
    DOBOT_DEFAULT_BAUDRATE = 115200
    DOBOT_Z_HIGH = 50.
    DOBOT_Z_LOW = -72.
    DOBOT_SERVE_XY = (0., -150.)
    DOBOT_MAX_VELOCITY = 300
    DOBOT_MAX_ACCERALATION = 300

    DOBOT_COORDINATE_CONVERTER = None


class DevelopmentConfig(DefaultConfig):
    DEBUG = True


class StagingConfig(DefaultConfig):
    pass


class ProductionConfig(DefaultConfig):
    pass


_ENV_TO_CONFIG = {
    'dev': DevelopmentConfig,
    'stg': StagingConfig,
    'prd': ProductionConfig,
}

Config = None


def get_config(env, dobot_port, tuning_file):
    global Config
    Config = _ENV_TO_CONFIG[env]()

    Config.DOBOT_SERIAL_PORT = dobot_port
    # todo: 微妙
    Config.DOBOT_COORDINATE_CONVERTER = CoordinateConverter.from_tuning_file(tuning_file)

    return Config
