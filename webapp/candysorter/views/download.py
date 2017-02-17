# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from flask import Blueprint, send_from_directory

from candysorter.config import Config

download = Blueprint('download', __name__)


@download.route('/image/<path:filename>')
def download_image(filename):
    return send_from_directory(Config.DOWNLOAD_IMAGE_DIR, filename)
