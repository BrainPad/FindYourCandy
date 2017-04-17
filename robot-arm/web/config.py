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
import os

from calibration.converter import CoordinateConverter


class DefaultConfig(object):
    DEBUG = False

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))

    LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
    LOG_LEVEL = logging.INFO

    DOBOT_SERIAL_PORT = None
    DOBOT_DEFAULT_BAUDRATE = 115200
    DOBOT_Z_HIGH = 0.
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


def get_config(env, dobot_port, tuner_file):
    config = _ENV_TO_CONFIG[env]()

    config.DOBOT_SERIAL_PORT = dobot_port
    config.DOBOT_COORDINATE_CONVERTER = CoordinateConverter.from_tuning_file(tuner_file)

    return config
