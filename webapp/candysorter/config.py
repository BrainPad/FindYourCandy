# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os


class DefaultConfig(object):
    DEBUG = False
    TESTING = False

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    RESOURCE_DIR = os.path.join(APP_ROOT, 'resources')

    DOWNLOAD_DIR = os.path.join(PROJECT_ROOT, 'tmp', 'download')
    DOWNLOAD_IMAGE_DIR = os.path.join(DOWNLOAD_DIR, 'image')

    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    LOG_DIR = os.path.join(PROJECT_ROOT, 'logs')
    LOG_LEVEL = logging.INFO

    CLASS_TEXT_ANALYZER = 'candysorter.models.texts.TextAnalyzer'
    CLASS_IMAGE_CAPTURE = 'candysorter.models.images.capture.ImageCapture'

    WORD2VEC_MODEL_FILE = os.path.join(
        RESOURCE_DIR, 'models/GoogleNews-vectors-negative300.bin.gz')
    KERAS_MODEL_FILE = os.path.join(
        RESOURCE_DIR, 'models/weights_20170208_195656.hdf5')

    CANDY_DETECTOR_HISTGRAM_BAND = (80, 200)
    CANDY_DETECTOR_HISTGRAM_THRES = 2.7e-3
    CANDY_DETECTOR_BINARIZE_BLOCK = 501
    CANDY_DETECTOR_MARGIN = (20, 20)
    CANDY_DETECTOR_OPENING_ITER = 2
    CANDY_DETECTOR_CLOSING_ITER = 5
    CANDY_DETECTOR_SURE_FG_THRES = 0.5
    CANDY_DETECTOR_RESTORE_FG_THRES = 0.0
    CANDY_DETECTOR_DILATE_ITER = 3

    IMAGE_CAPTURE_DEVICE = 0
    IMAGE_CAPTURE_WIDTH = 1920
    IMAGE_CAPTURE_HEIGHT = 1080
    IMAGE_CAPTURE_BLUR_THRESH = 100

    IMAGE_CALIBRATOR_AREA = (1625, 1100)
    IMAGE_CALIBRATOR_SCALE = 550

    TRAIN_LABEL_AREA_HEIGHT = 400

    PICKUP_ENDOPOINT = 'http://localhost:8000/api/pickup'


class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

    CLASS_TEXT_ANALYZER = 'candysorter.models.texts.FakeTextAnalyzer'
    CLASS_IMAGE_CAPTURE = 'candysorter.models.images.capture.FakeImageCapture'
    DUMMY_IMAGE_FILE = './candysorter/resources/data/candies_with_label_multi.jpg'


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


def get_config(env):
    global Config
    Config = _ENV_TO_CONFIG[env]()
    return Config
