# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import json
import logging
import os
import random

import tensorflow as tf

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


class Trainer(object):
    def __init__(self, epochs, train_dir, log_dir, batch_size, hidden_size):
        self.epochs = epochs
        self.train_dir = train_dir
        self.log_dir = log_dir
        self.batch_size = batch_size
        self.hidden_size = hidden_size

    def _epoch_log_path(self, num_epoch):
        return os.path.join(self.log_dir, 'epochs', '{}.json'.format(num_epoch))

    def train(self, dataset):
        n_samples = dataset.n_samples()
        n_labels = len(dataset.labels)

        logger.info('Build transfer network.')

        mo = model.TransferModel(
            dataset.feature_size(),
            n_labels,
            hidden_size=self.hidden_size
        )

        logger.info('Start training.')
        checkpoint_path = os.path.join(self.train_dir, 'model.ckpt')

        epoch_log_dir = os.path.dirname(self._epoch_log_path(0))
        if not tf.gfile.Exists(epoch_log_dir):
            tf.gfile.MakeDirs(epoch_log_dir)

        loss_log = []
        with tf.Session() as sess:
            summary_writer = tf.train.SummaryWriter(self.log_dir, graph=sess.graph)
            sess.run(tf.initialize_all_variables())
            for epoch in range(self.epochs):
                # Shuffle data for batching
                shuffled_idx = list(range(n_samples))
                random.shuffle(shuffled_idx)
                for begin_idx in range(0, n_samples, self.batch_size):
                    batch_idx = shuffled_idx[begin_idx: begin_idx + self.batch_size]
                    sess.run(mo.train_op, mo.feed_for_training(*dataset.get(batch_idx)))

                # Print and write summaries.
                in_sample_loss, summary = sess.run(
                    [mo.loss_op, mo.summary_op],
                    mo.feed_for_training(*dataset.all())
                )
                loss_log.append(in_sample_loss)

                summary_writer.add_summary(summary, epoch)

                # Save checkpoint per 100 epoch.
                if epoch % 100 == 0 or epoch == self.epochs - 1:
                    logger.info('{}th epoch end with loss {}.'.format(epoch, in_sample_loss))
                    mo.saver.save(sess, checkpoint_path, global_step=mo.global_step)
                    features = sess.run(
                        [mo.softmax_op],
                        mo.feed_for_training(*dataset.all())
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

            mo.saver.save(sess, checkpoint_path, global_step=mo.global_step)
            summary_writer.close()


def main(_):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(name)-7s %(levelname)-7s %(message)s'
    )
    logger.info('tf version: {}'.format(tf.__version__))

    parser = argparse.ArgumentParser(description='Run Dobot WebAPI.')
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--hidden_size', type=int, default=3, help="Number of units in hidden layer.")
    parser.add_argument('--epochs', type=int, default=1000, help="Number of epochs of training")
    parser.add_argument('--data_dir', type=str, default='data', help="Directory for training data.")
    parser.add_argument('--log_dir', type=str, default='log', help="Directory for TensorBoard logs.")
    parser.add_argument('--train_dir', type=str, default='train', help="Directory for checkpoints.")

    args = parser.parse_args()

    data_dir = args.data_dir
    reader = TrainingFeaturesDataReader(data_dir)

    dataset = DataSet.from_reader(reader)

    trainer = Trainer(
        epochs=args.epochs,
        train_dir=args.train_dir,
        log_dir=args.log_dir,
        batch_size=args.batch_size,
        hidden_size=args.hidden_size
    )

    params = model.ModelParams(
        labels=dataset.labels,
        hidden_size=args.hidden_size,
        features_size=dataset.feature_size()
    )

    with tf.gfile.FastGFile(args.train_dir + '/params.json', 'w') as f:
        f.write(params.to_json())

    trainer.train(dataset)


if __name__ == '__main__':
    tf.app.run()
