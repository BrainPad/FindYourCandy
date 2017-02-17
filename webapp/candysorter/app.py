# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import logging.config
import os

from flask import Flask, g, jsonify

from candysorter.config import get_config


def create_app():
    config = get_config(os.getenv('FLASK_ENV', 'dev'))

    app = Flask('candysorter')

    _configure_app(app, config)
    _configure_logging(app, config)
    _configure_blueprints(app)
    _configure_errorhandlers(app)
    _configure_hooks(app)

    return app


def _configure_app(app, config):
    app.config.from_object(config)


def _configure_blueprints(app):
    from candysorter.views.api import api
    from candysorter.views.download import download
    from candysorter.views.ui import ui

    app.register_blueprint(api)
    app.register_blueprint(download)
    app.register_blueprint(ui)


def _configure_logging(app, config):
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
                'filename': os.path.join(config.LOG_DIR, 'app.log'),
                'when': 'd',
                'interval': 1,
                'backupCount': 14,
            },
            'file_access': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'access',
                'filename': os.path.join(config.LOG_DIR, 'access.log'),
                'when': 'd',
                'interval': 1,
                'backupCount': 14,
            },

        },
        'loggers': {
            'candysorter': {
                'level': config.LOG_LEVEL,
                'handlers': ['file_app'] if not app.debug else ['console_app'],
                'propagate': False,
            },
            'werkzeug': {
                'level': config.LOG_LEVEL,
                'handlers': ['file_access'] if not app.debug else ['console_access'],
                'propagate': False,
            },
        },
        'root': {
            'level': config.LOG_LEVEL,
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
