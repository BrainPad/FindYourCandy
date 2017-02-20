# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import os

import tensorflow as tf
from tensorflow.python.ops import init_ops

INPUT_DATA_TENSOR_NAME = 'DecodeJpeg:0'
FEATURE_TENSOR_NAME = 'pool_3/_reshape:0'


class ModelParams(object):
    def __init__(self, labels, features_size, hidden_size):
        self.labels = labels
        self.features_size = features_size
        self.hidden_size = hidden_size

    def to_json(self):
        return json.dumps({
            "labels": self.labels,
            "features_size": self.features_size,
            "hidden_size": self.hidden_size
        })

    @classmethod
    def from_json(cls, s):
        params = json.loads(s)
        return cls(
            labels=params["labels"],
            features_size=params["features_size"],
            hidden_size=params["hidden_size"]
        )


class TransferModel(object):
    def __init__(self, features_size, num_classes, for_predict=False, hidden_size=3):
        self.hidden_size = hidden_size
        self.num_classes = num_classes

        with tf.variable_scope('transfer'):
            self.features = tf.placeholder(tf.float32, (None, features_size), name='features')
            self.label_ids = tf.placeholder(tf.int32, (None,), name='label_ids')

            try:
                ones_initializer = init_ops.ones_initializer()
            except TypeError:
                ones_initializer = init_ops.ones_initializer

            hidden = tf.contrib.layers.fully_connected(
                self.features,
                hidden_size,
                activation_fn=tf.nn.relu,
                weights_initializer=tf.contrib.layers.xavier_initializer(),
                biases_initializer=ones_initializer,
                trainable=True
            )

            logits = tf.contrib.layers.fully_connected(
                hidden,
                num_classes,
                weights_initializer=tf.contrib.layers.xavier_initializer(),
                biases_initializer=ones_initializer,
                trainable=True
            )

        if not for_predict:
            # add loss operation if initializing for training
            one_hot = tf.one_hot(self.label_ids, num_classes, name='target')
            self.loss_op = tf.reduce_mean(
                tf.nn.softmax_cross_entropy_with_logits(logits, one_hot)
            )

        self.softmax_op = tf.nn.softmax(logits)
        self.saver = tf.train.Saver()

        if not for_predict:
            # add train operation and summary operation if initializing for training
            # Optimizer
            with tf.variable_scope('optimizer'):
                optimizer = tf.train.AdamOptimizer()
                self.global_step = tf.Variable(0, name='global_step', trainable=False)
                self.train_op = optimizer.minimize(self.loss_op, global_step=self.global_step)
            # Summaries
            with tf.variable_scope('summaries'):
                tf.scalar_summary('in sample loss', self.loss_op)
                self.summary_op = tf.merge_all_summaries()

    @classmethod
    def from_model_params(cls, model_params):
        return cls(
            features_size=model_params.features_size,
            num_classes=len(model_params.labels),
            hidden_size=model_params.hidden_size
        )

    def restore_and_predict(self, input_tensor, model_checkpoint_path):
        saver = tf.train.Saver(tf.get_collection(tf.GraphKeys.VARIABLES, scope='transfer'))
        with tf.Session() as sess:
            sess.run(tf.initialize_all_variables())
            saver.restore(sess, model_checkpoint_path)
            prob = sess.run(self.softmax_op, self.feed_for_predict(input_tensor))
        return prob

    def feed_for_predict(self, features):
        return {
            self.features: features
        }

    def feed_for_training(self, features, label_ids):
        return {
            self.features: features,
            self.label_ids: label_ids
        }
