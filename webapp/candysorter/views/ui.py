# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime
import os

import cv2
from flask import Blueprint, current_app, send_file, send_from_directory

from candysorter.config import Config
from candysorter.decorators import after_this_request
from candysorter.utils import load_class

ui = Blueprint('ui', __name__)


@ui.route('/predict')
def predict():
    return current_app.send_static_file('predict.html')


@ui.route('/learn')
def learn():
    return current_app.send_static_file('learn.html')


@ui.route('/image/<path:filename>')
def image(filename):
    return send_from_directory(Config.DOWNLOAD_IMAGE_DIR, filename)


@ui.route('/_capture')
def capture():
    tmp_dir = os.path.join(Config.DOWNLOAD_IMAGE_DIR, 'tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    tmp_file = os.path.join(tmp_dir, '{}.jpg'.format(datetime.now().strftime('%Y%m%d_%H%M%S')))

    @after_this_request
    def remove_tmp_file(response):
        os.remove(tmp_file)

    image_capture = load_class(Config.CLASS_IMAGE_CAPTURE).from_config(Config)
    img = image_capture.capture()

    cv2.imwrite(tmp_file, img)
    return send_file(tmp_file)
