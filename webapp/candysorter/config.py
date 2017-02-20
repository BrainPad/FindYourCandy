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
    CLASSIFIER_MODEL_DIR = os.path.join(
        RESOURCE_DIR, 'models/classifier')
    INCEPTION_MODEL_FILE = os.path.join(
        RESOURCE_DIR, 'models/classify_image_graph_def.pb')

    CANDY_DETECTOR_HISTGRAM_BAND = (0, 255)
    CANDY_DETECTOR_HISTGRAM_THRES = 2.7e-3
    CANDY_DETECTOR_EDGE3_thres = 250
    CANDY_DETECTOR_EDGE5_thres = 230
    CANDY_DETECTOR_MARGIN = (30, 30)
    CANDY_DETECTOR_CLOSING_ITER = 1
    CANDY_DETECTOR_OPENING_ITER = 10
    CANDY_DETECTOR_ERODE_ITER = 25
    CANDY_DETECTOR_DILATE_ITER = 1
    CANDY_DETECTOR_BG_SIZE_FILTER = 2000
    CANDY_DETECTOR_SURE_FG_THRES = 10
    CANDY_DETECTOR_RESTORE_FG_THRES = 0.0

    IMAGE_CAPTURE_DEVICE = 0
    IMAGE_CAPTURE_WIDTH = 1920
    IMAGE_CAPTURE_HEIGHT = 1080
    IMAGE_CAPTURE_BLUR_THRESH = 100

    IMAGE_CALIBRATOR_AREA = (1625, 1100)
    IMAGE_CALIBRATOR_SCALE = 550

    PICKUP_ENDOPOINT = 'http://localhost:18001/api/pickup'

    TRAIN_LABEL_AREA_HEIGHT = 400

    CLOUD_ML_BUCKET = 'gs://candy-sorter-ml'
    CLOUD_ML_PACKAGE_URIS = ['gs://candy-sorter-ml/package/trainer.tar.gz']
    CLOUD_ML_PYTHON_MODULE = 'trainer.train'
    CLOUD_ML_TRAIN_DIR = 'gs://candy-sorter-ml/{name}/checkpoints'
    CLOUD_ML_LOG_DIR = 'gs://candy-sorter-ml/logs/{name}'
    CLOUD_ML_DATA_DIR = 'gs://candy-sorter-ml/{name}/features'


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
