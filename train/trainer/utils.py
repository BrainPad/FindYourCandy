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

import os
import json

import numpy as np
import tensorflow as tf


class FeaturesDataReader(object):
    def __init__(self, data_dir, labels_file_name='labels.json', features_file_name='features.json'):
        self.labels_file = os.path.join(data_dir, labels_file_name)
        self.features_file = os.path.join(data_dir, features_file_name)

    def read_features(self):
        with tf.gfile.FastGFile(self.features_file) as i_:
            features = map(lambda l: json.loads(l)['feature_vector'], i_.readlines())
        return np.array(features, dtype='float32')

    def read_labels(self):
        with tf.gfile.FastGFile(self.labels_file) as i_:
            labels = json.loads(i_.read())
        return labels

    def read_feature_metadata(self, key):
        with tf.gfile.FastGFile(self.features_file) as i_:
            features = map(lambda l: json.loads(l)[key], i_.readlines())
        return np.array(features)


class TrainingFeaturesDataReader(FeaturesDataReader):
    def read_features(self):
        with tf.gfile.FastGFile(self.features_file) as i_:
            lines = i_.readlines()
            features = map(lambda l: json.loads(l)['feature_vector'], lines)
            label_ids = map(lambda l: json.loads(l)['label_id'], lines)
        return np.array(features, dtype='float32'), np.array(label_ids, dtype='int32')
