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

from candysorter.ext.google.cloud import language


# flake8: noqa
class DefaultConfig(object):
    DEBUG = False
    TESTING = False

    PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    APP_ROOT     = os.path.abspath(os.path.dirname(__file__))

    DOWNLOAD_DIR       = os.path.join(PROJECT_ROOT, 'tmp', 'download')
    DOWNLOAD_IMAGE_DIR = os.path.join(DOWNLOAD_DIR, 'image')
    RESOURCE_DIR       = os.path.join(APP_ROOT, 'resources')
    MODEL_DIR          = os.path.join(RESOURCE_DIR, 'models')

    JSON_AS_ASCII               = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    LOG_DIR   = os.path.join(PROJECT_ROOT, 'logs')
    LOG_LEVEL = logging.INFO

    CLASS_TEXT_ANALYZER = 'candysorter.models.texts.TextAnalyzer'
    CLASS_IMAGE_CAPTURE = 'candysorter.models.images.capture.ImageCapture'

    WORD2VEC_MODEL_FILES = {
        'en': {
            'file': os.path.join(MODEL_DIR, 'GoogleNews-vectors-negative300.bin.gz'),
            'binary': True,
        },
        'ja': {
            'file': os.path.join(MODEL_DIR, 'model.vec'),
            'binary': False,
        },
    }
    CLASSIFIER_MODEL_DIR         = os.path.join(MODEL_DIR, 'classifier')
    CLASSIFIER_MODEL_DIR_INITIAL = os.path.join(MODEL_DIR, 'classifier_initial')
    INCEPTION_MODEL_FILE         = os.path.join(MODEL_DIR, 'classify_image_graph_def.pb')

    POS_WEIGHTS = {
        language.PartOfSpeech.ADJECTIVE: 1.0,
        language.PartOfSpeech.NOUN: 2.8,
    }

    CANDY_DETECTOR_HISTGRAM_BAND    = (0, 255)
    CANDY_DETECTOR_HISTGRAM_THRES   = 2.7e-3
    CANDY_DETECTOR_BIN_THRES        = 150
    CANDY_DETECTOR_EDGE3_THRES      = 250
    CANDY_DETECTOR_EDGE5_THRES      = 230
    CANDY_DETECTOR_MARGIN           = (30, 30)
    CANDY_DETECTOR_CLOSING_ITER     = 2
    CANDY_DETECTOR_OPENING_ITER     = 5
    CANDY_DETECTOR_ERODE_ITER       = 25
    CANDY_DETECTOR_DILATE_ITER      = 1
    CANDY_DETECTOR_BG_SIZE_FILTER   = 2000
    CANDY_DETECTOR_SURE_FG_THRES    = 10
    CANDY_DETECTOR_RESTORE_FG_THRES = 0.0
    CANDY_DETECTOR_BOX_DIM_THRES    = 50

    IMAGE_CAPTURE_DEVICE      = 0
    IMAGE_CAPTURE_WIDTH       = 1920
    IMAGE_CAPTURE_HEIGHT      = 1080
    IMAGE_CAPTURE_BLUR_THRESH = 100

    IMAGE_CALIBRATOR_AREA  = (1625, 1100)
    IMAGE_CALIBRATOR_SCALE = 550

    PICKUP_ENDOPOINT = 'http://localhost:18001/api/pickup'

    TRAIN_LABEL_AREA_HEIGHT = 285

    # replace "YOUR-OWN-BUCKET-NAME" to your own bucket name
    CLOUD_ML_BUCKET          = 'gs://{YOUR-OWN-BUCKET-NAME}'
    CLOUD_ML_PACKAGE_URIS    = ['gs://{YOUR-OWN-BUCKET-NAME}/package/trainer-0.0.0.tar.gz']
    CLOUD_ML_PYTHON_MODULE   = 'trainer.train'
    CLOUD_ML_TRAIN_DIR       = 'gs://{YOUR-OWN-BUCKET-NAME}/{job_id}/checkpoints'
    CLOUD_ML_LOG_DIR         = 'gs://{YOUR-OWN-BUCKET-NAME}/logs/{job_id}'
    CLOUD_ML_DATA_DIR        = 'gs://{YOUR-OWN-BUCKET-NAME}/{job_id}/features'
    CLOUD_ML_RUNTIME_VERSION = '1.0'


class DevelopmentConfig(DefaultConfig):
    DEBUG = True
    LOG_LEVEL = logging.DEBUG

    CLASS_TEXT_ANALYZER = 'candysorter.models.texts.FakeTextAnalyzer'
    CLASS_IMAGE_CAPTURE = 'candysorter.models.images.capture.FakeImageCapture'
    DUMMY_IMAGE_FILE    = './candysorter/resources/data/candies_with_label_multi.jpg'


class StagingConfig(DefaultConfig):
    pass


class ProductionConfig(DefaultConfig):
    pass


_ENV_TO_CONFIG = {
    'dev': DevelopmentConfig,
    'stg': StagingConfig,
    'prd': ProductionConfig,
}


def get_config(env):
    return _ENV_TO_CONFIG[env]()
