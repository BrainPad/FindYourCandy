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
import logging.config

import os

from flask import Flask

from web.api import api
from web.config import get_config


def create_app(dobot_port, tuner_file, instance_path):
    app = Flask(__name__, instance_path=instance_path, instance_relative_config=True)

    app.config.from_object(get_config(os.getenv('FLASK_ENV', 'dev'), dobot_port, tuner_file))
    app.config.from_pyfile('config.py', silent=True)
    _configure_logging(app)
    app.register_blueprint(api, url_prefix='/api')

    return app


def _configure_logging(app):
    app.logger
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'default': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
            'access': {
                'format': '%(message)s',
            },
        },
        'handlers': {
            'console_app': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
            },
            'console_access': {
                'class': 'logging.StreamHandler',
                'formatter': 'access',
            },
            'file_app': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': os.path.join(app.config['LOG_DIR'], 'app.log'),
                'when': 'd',
                'interval': 1,
                'backupCount': 14,
            },
            'file_access': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'access',
                'filename': os.path.join(app.config['LOG_DIR'], 'access.log'),
                'when': 'd',
                'interval': 1,
                'backupCount': 14,
            },

        },
        'loggers': {
            '': {
                'level': app.config['LOG_LEVEL'],
                'handlers': ['file_app'] if not app.debug else ['console_app'],
                'propagate': False,
            },
            'werkzeug': {
                'level': app.config['LOG_LEVEL'],
                'handlers': ['file_access'] if not app.debug else ['console_access'],
                'propagate': False,
            },
        },
        'root': {
            'level': app.config['LOG_LEVEL'],
            'handlers': ['file_app'] if not app.debug else ['console_app'],
        },
    })
