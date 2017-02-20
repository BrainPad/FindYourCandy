# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import logging
import os
import random

import tensorflow as tf

import trainer.model as model
from trainer.utils import TrainingFeaturesDataReader

JPEG_EXT = 'jpg'

logger = logging.getLogger(__name__)


class Trainer(object):
    def __init__(self, epochs, train_dir, log_dir, batch_size, hidden_size):
        self.epochs = epochs
        self.train_dir = train_dir
        self.log_dir = log_dir
        self.batch_size = batch_size
        self.hidden_size = hidden_size

    def train(self, features_data, label_ids_data):
        n_samples = len(features_data)
        n_labels = len(set(label_ids_data))

        logger.info('Build transfer network.')

        feature_size = features_data[0].shape[0]

        mo = model.TransferModel(
            feature_size,
            n_labels,
            hidden_size=self.hidden_size
        )

        logger.info('Start training.')
        checkpoint_path = os.path.join(self.train_dir, 'model.ckpt')
        with tf.Session() as sess:
            summary_writer = tf.train.SummaryWriter(self.log_dir, graph=sess.graph)
            sess.run(tf.initialize_all_variables())
            for epoch in range(self.epochs):
                # Shuffle data for batching
                shuffled_idx = list(range(n_samples))
                random.shuffle(shuffled_idx)
                for begin_idx in range(0, n_samples, self.batch_size):
                    batch_idx = shuffled_idx[begin_idx: begin_idx + self.batch_size]
                    sess.run(mo.train_op, {
                        mo.features: features_data[batch_idx],
                        mo.label_ids: label_ids_data[batch_idx]
                    })

                # Print and write summaries.
                in_sample_loss, summary = sess.run(
                    [mo.loss_op, mo.summary_op],
                    mo.feed_for_training(features_data, label_ids_data)
                )

                summary_writer.add_summary(summary, epoch)

                # Save checkpoint per 100 epoch.
                if epoch % 100 == 0:
                    logger.info('{}th epoch end with loss {}.'.format(epoch, in_sample_loss))
                    mo.saver.save(sess, checkpoint_path, global_step=mo.global_step)

            # Ensure to save final ckeckpoint.
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

    data = reader.read_features()

    trainer = Trainer(
            epochs=args.epochs,
            train_dir=args.train_dir,
            log_dir=args.log_dir,
            batch_size=args.batch_size,
            hidden_size=args.hidden_size
        )

    params = model.ModelParams(
        labels=reader.read_labels(),
        hidden_size=args.hidden_size,
        features_size=data[0][0].shape[0]
    )

    with tf.gfile.FastGFile(args.train_dir+'/params.json', 'w') as f:
        f.write(params.to_json())

    trainer.train(*data)


if __name__ == '__main__':
    tf.app.run()
