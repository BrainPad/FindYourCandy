# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import os

import tensorflow as tf

from trainer.feature_extractor import FeatureExtractor
from trainer.model import TransferModel, ModelParams

logger = logging.getLogger(__name__)


class CandyClassifier(object):
    def __init__(self, checkpoint_dir, params_file, inception_model_file):
        self.inception_model = None
        self.model = None
        self.checkpoint_dir = checkpoint_dir
        self.params_file = params_file
        self.inception_model_file = inception_model_file

    @classmethod
    def from_config(cls, config):
        checkpoint_dir = config.CLASSIFIER_MODEL_DIR
        return cls(
            checkpoint_dir=checkpoint_dir,
            params_file=os.path.join(checkpoint_dir, 'params.json'),
            inception_model_file=config.INCEPTION_MODEL_FILE
        )

    def init(self):
        logger.info('Loading inception-v3 model...')
        self.inception_model = FeatureExtractor(self.inception_model_file)
        logger.info('Finished loading inception model...')

        logger.info('Loading transfer model...')
        with tf.gfile.FastGFile(self.params_file, 'r') as f:
            params = ModelParams.from_json(f.read())
        self.model = TransferModel.from_model_params(params)
        logger.info('Finished loading transfer model...')

    def classify(self, img_bgr):
        features = self.inception_model.get_feature_vector(img_bgr)
        ckpt = tf.train.get_checkpoint_state(self.checkpoint_dir)

        if ckpt is None:
            raise IOError('Checkpoints not found.')
        checkpoint_path = ckpt.model_checkpoint_path
        result = self.model.restore_and_predict(features, checkpoint_path)
        return result[0]
