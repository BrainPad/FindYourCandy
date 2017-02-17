# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

import cv2
from keras.models import load_model
import tensorflow as tf

logger = logging.getLogger(__name__)

# https://github.com/fchollet/keras/issues/2397
_graph = None


class CandyClassifier(object):
    def __init__(self, model_file):
        self.model = None
        self.model_file = model_file

    @classmethod
    def from_config(cls, config):
        return cls(model_file=config.KERAS_MODEL_FILE)

    def init(self):
        logger.info('Loading keras model...')
        self.model = load_model(self.model_file)
        # self.model = None
        logger.info('Finished loading keras model...')

        global _graph
        _graph = tf.get_default_graph()

    def classify(self, img_bgr):
        img = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        img = cv2.resize(img, (150, 150))
        img = img.transpose((2, 0, 1))
        img = img.reshape((1,) + img.shape)
        img //= 255

        with _graph.as_default():
            return self.model.predict(img)[0]
