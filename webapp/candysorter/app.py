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
import sys

from flask import Flask, g, jsonify

from candysorter.config import get_config


def create_app(instance_path):
    app = Flask('candysorter', instance_path=instance_path, instance_relative_config=True)

    _configure_app(app)
    _configure_logging(app)
    _configure_blueprints(app)
    _configure_errorhandlers(app)
    _configure_hooks(app)

    return app


def _configure_app(app):
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../train'))
    app.config.from_object(get_config(os.getenv('FLASK_ENV', 'dev')))
    app.config.from_pyfile('config.py', silent=True)


def _configure_blueprints(app):
    from candysorter.views.api import api
    from candysorter.views.ui import ui

    app.register_blueprint(api)
    app.register_blueprint(ui)


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
            'candysorter': {
                'level': app.config['LOG_LEVEL'],
                'handlers': ['file_app'] if not app.debug else ['console_app'],
                'propagate': False,
            },
            'tensorflow': {
                'level': logging.ERROR,
                'handlers': ['file_access'] if not app.debug else ['console_access'],
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


def _configure_errorhandlers(app):
    @app.errorhandler(404)
    @app.errorhandler(405)
    def handle_error(e):
        # TODO: blueprints
        return jsonify(error=e.code, message=e.name.lower()), e.code


def _configure_hooks(app):
    @app.after_request
    def call_after_request_callbacks(response):
        for callback in getattr(g, 'after_request_callbacks', ()):
            callback(response)
        return response
