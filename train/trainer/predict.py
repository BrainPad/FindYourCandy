# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import json
import logging

import numpy as np
import tensorflow as tf

import trainer.model as model
from trainer.utils import FeaturesDataReader

logger = logging.getLogger(__name__)


class Predictor(object):
    def __init__(self, data_reader, checkpoint_dir, params_file):
        self.labels = data_reader.read_labels()
        self.features_data = data_reader.read_features()
        self.data_reader = data_reader
        self.checkpoint_dir = checkpoint_dir
        with tf.gfile.FastGFile(params_file, 'r') as f:
            params = model.ModelParams.from_json(f.read())

        self.model_params = params

    def predict(self):
        logger.info('Found labels: {}'.format(self.labels))

        n_samples = len(self.features_data[0])
        logger.info('{} features were extracted.'.format(n_samples))

        logger.info('Start prediction.')

        ckpt = tf.train.get_checkpoint_state(self.checkpoint_dir)

        if ckpt is None:
            raise IOError('Checkpoints not found.')
        checkpoint_path = ckpt.model_checkpoint_path

        mo = model.TransferModel.from_model_params(self.model_params)
        prob = mo.restore_and_predict(self.features_data, checkpoint_path)

        label_ids = np.argmax(prob, axis=1)
        return label_ids, prob

    def predict_to_json(self):
        return self.result_to_json(*self.predict())

    def result_to_json(self, label_ids, prob):
        result = []
        image_urls = self.data_reader.read_feature_metadata('image_uri')
        for i in xrange(len(label_ids)):
            lid = label_ids[i]
            result.append({
                "url": image_urls[i],
                "top_lid": lid,
                "top_label": self.model_params.labels[lid],
                "probs": prob[i].tolist()
            })
        return json.dumps(result)


def main(_):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)-7s %(levelname)-7s %(message)s'
    )
    logger.info('tf version: {}'.format(tf.__version__))

    parser = argparse.ArgumentParser(description='Run Dobot WebAPI.')
    parser.add_argument('--data_dir', type=str, default='data', help="Directory for training data.")
    parser.add_argument('--train_dir', type=str, default='train', help="Directory for checkpoints.")

    args = parser.parse_args()

    reader = FeaturesDataReader(args.data_dir)

    predictor = Predictor(reader, args.train_dir, args.train_dir+'/params.json')
    print(predictor.predict_to_json())

if __name__ == '__main__':
    tf.app.run()
