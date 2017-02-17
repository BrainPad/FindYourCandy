# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os

from flask import Flask

from web.api import api
from web.config import get_config


def create_app(dobot_port, tuner_file):
    config = get_config(os.getenv('FLASK_ENV', 'dev'), dobot_port, tuner_file)

    app = Flask(__name__)

    app.config.from_object(config)
    app.register_blueprint(api, url_prefix='/api')
    return app
