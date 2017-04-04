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

import argparse
import json
import logging
import os
import random

import tensorflow as tf
import time

import trainer.model as model
from trainer.utils import TrainingFeaturesDataReader

JPEG_EXT = 'jpg'

logger = logging.getLogger(__name__)


class DataSet(object):
    def __init__(self, features_data, label_ids_data, image_uris, labels):
        self.features_data = features_data
        self.label_ids_data = label_ids_data
        self.image_uris = image_uris
        self.labels = labels

    @classmethod
    def from_reader(cls, reader):
        data = reader.read_features()
        uris = reader.read_feature_metadata('image_uri')
        labels = reader.read_labels()
        return cls(data[0], data[1], uris, labels)

    def n_samples(self):
        return len(self.features_data)

    def feature_size(self):
        return self.features_data[0].shape[0]

    def get(self, idx):
        return self.features_data[idx], self.label_ids_data[idx]

    def get_meta(self, idx):
        lid = self.label_ids_data[idx]
        return {'url': self.image_uris[idx], 'label': self.labels[lid], 'lid': lid}

    def all(self):
        return self.features_data, self.label_ids_data


class TrainingConfig(object):
    def __init__(self, epochs, batch_size, optimizer_class, optimizer_args, keep_prob=1.0):
        self.epochs = epochs
        self.batch_size = batch_size
        self.optimizer = optimizer_class(**optimizer_args)
        self.optimizer_args = optimizer_args
        self.keep_prob = keep_prob

    def to_json(self):
        optimizer_str = type(self.optimizer).__name__
        return json.dumps({
            "epochs": self.epochs,
            "batch_size": self.batch_size,
            "keep_prob": self.keep_prob,
            "optimizer": {
                "name": optimizer_str,
                "args": self.optimizer_args,
            }
        })


class Trainer(object):
    def __init__(self, train_config, model_params, train_dir, log_dir):
        self.train_config = train_config
        self.model_params = model_params
        self.train_dir = train_dir
        self.log_dir = log_dir

        self.model = model.TransferModel.from_model_params(self.model_params)
        self.train_op = self.model.train_op(self.train_config.optimizer)

        self._sleep_sec = 0.1

        self._last_logged_loss = None

        self._force_logging_interval = 200
        self._check_interval = 10
        self._threshold = 0.20

    def _epoch_log_path(self, num_epoch):
        return os.path.join(self.log_dir, 'epochs', '{}.json'.format(str(num_epoch).zfill(6)))

    def train(self, dataset):
        n_samples = dataset.n_samples()

        logger.info('Build transfer network.')

        logger.info('Start training.')
        checkpoint_path = os.path.join(self.train_dir, 'model.ckpt')

        epoch_log_dir = os.path.dirname(self._epoch_log_path(0))
        if not tf.gfile.Exists(epoch_log_dir):
            tf.gfile.MakeDirs(epoch_log_dir)

        loss_log = []
        with tf.Session() as sess:
            summary_writer = tf.summary.FileWriter(self.log_dir, graph=sess.graph)
            sess.run(tf.global_variables_initializer())

            for epoch in range(self.train_config.epochs):
                # Shuffle data for batching
                shuffled_idx = list(range(n_samples))
                random.shuffle(shuffled_idx)
                for begin_idx in range(0, n_samples, self.train_config.batch_size):
                    batch_idx = shuffled_idx[begin_idx: begin_idx + self.train_config.batch_size]
                    sess.run(self.train_op, self.model.feed_for_training(*dataset.get(batch_idx)))

                # Print and write summaries.
                in_sample_loss, summary = sess.run(
                    [self.model.loss_op, self.model.summary_op],
                    self.model.feed_for_training(*dataset.all())
                )
                loss_log.append(in_sample_loss)

                summary_writer.add_summary(summary, epoch)

                if epoch % 100 == 0 or epoch == self.train_config.epochs - 1:
                    logger.info('{}th epoch end with loss {}.'.format(epoch, in_sample_loss))

                if self._needs_logging(loss_log):
                    features = sess.run(
                        [self.model.softmax_op],
                        self.model.feed_for_training(*dataset.all())
                    )

                    # write loss and predicted probabilities
                    probs = map(lambda a: a.tolist(), features[0])
                    max_l = max(loss_log)
                    loss_norm = [float(l) / max_l for l in loss_log]
                    with tf.gfile.FastGFile(self._epoch_log_path(epoch), 'w') as f:
                        data = {
                            'epoch': epoch,
                            'loss': loss_norm,
                        }
                        probs_with_uri = []

                        for i, p in enumerate(probs):
                            meta = dataset.get_meta(i)
                            item = {
                                'probs': p,
                                'url': meta['url'],
                                'property': {
                                    'label': meta['label'],
                                    'lid': int(meta['lid'])
                                }
                            }
                            probs_with_uri.append(item)

                        data['probs'] = probs_with_uri
                        f.write(json.dumps(data))

                # FIXME: sleep to show convergence slowly on UI
                if epoch < 200 and loss_log[-1] > max(loss_log) * 0.01:
                    time.sleep(self._sleep_sec)

            self.model.saver.save(sess, checkpoint_path, global_step=self.model.global_step)
            summary_writer.close()

    def _needs_logging(self, loss_log):
        if len(loss_log) < self._check_interval or len(loss_log) % self._check_interval != 0:
            return False
        if len(loss_log) % self._force_logging_interval == 0:
            return True

        loss = loss_log[-1]
        if self._last_logged_loss is None:
            self._last_logged_loss = loss
            return True

        loss_change_rate = loss/self._last_logged_loss
        if 1 - loss_change_rate > self._threshold:
            self._last_logged_loss = loss
            return True

        return False


def main(_):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)-7s %(levelname)-7s %(message)s'
    )
    logger.info('tf version: {}'.format(tf.__version__))

    parser = argparse.ArgumentParser(description='Run Dobot WebAPI.')
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--hidden_size', type=int, default=3, help="Number of units in hidden layer.")
    parser.add_argument('--epochs', type=int, default=2000, help="Number of epochs of training")
    parser.add_argument('--learning_rate', type=float, default=1e-3)
    parser.add_argument('--data_dir', type=str, default='data', help="Directory for training data.")
    parser.add_argument('--log_dir', type=str, default='log', help="Directory for TensorBoard logs.")
    parser.add_argument('--train_dir', type=str, default='train', help="Directory for checkpoints.")

    args = parser.parse_args()

    data_dir = args.data_dir
    reader = TrainingFeaturesDataReader(data_dir)

    dataset = DataSet.from_reader(reader)

    train_config = TrainingConfig(
        epochs=2000,
        batch_size=16,
        optimizer_class=tf.train.RMSPropOptimizer,
        optimizer_args={"learning_rate": 1e-3},
        keep_prob=1.0,
    )

    params = model.ModelParams(
        labels=dataset.labels,
        hidden_size=args.hidden_size,
        features_size=dataset.feature_size()
    )

    trainer = Trainer(
        train_config=train_config,
        model_params=params,
        train_dir=args.train_dir,
        log_dir=args.log_dir,
    )

    if not tf.gfile.Exists(args.train_dir):
        tf.gfile.MakeDirs(args.train_dir)

    if not tf.gfile.Exists(args.log_dir):
        tf.gfile.MakeDirs(args.log_dir)

    with tf.gfile.FastGFile(os.path.join(args.train_dir, 'params.json'), 'w') as f:
        f.write(params.to_json())

    with tf.gfile.FastGFile(os.path.join(args.log_dir, 'training.json'), 'w') as f:
        f.write(train_config.to_json())

    trainer.train(dataset)


if __name__ == '__main__':
    tf.app.run()
