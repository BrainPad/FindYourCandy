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

import json
import os
from urlparse import urlparse

from google.cloud import storage
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

from trainer.feature_extractor import FeatureExtractor

from candysorter.ext.google.cloud import ml


class CandyTrainer(object):
    def __init__(self, feature_extractor, package_uris, python_module, data_dir_format,
                 train_dir_format, log_dir_format, local_model_dir, local_classifier_model_dir):
        self.feature_extractor = feature_extractor
        self.package_uris = package_uris
        self.python_module = python_module
        self.data_dir_format = data_dir_format
        self.train_dir_format = train_dir_format
        self.log_dir_format = log_dir_format

        self.local_model_dir = local_model_dir
        self.local_classifier_model_dir = local_classifier_model_dir

        self.ml_client = ml.Client()
        self.storage_client = storage.Client()

    @classmethod
    def from_config(cls, config):
        return cls(feature_extractor=FeatureExtractor(config['INCEPTION_MODEL_FILE']),
                   package_uris=config['CLOUD_ML_PACKAGE_URIS'],
                   python_module=config['CLOUD_ML_PYTHON_MODULE'],
                   data_dir_format=config['CLOUD_ML_DATA_DIR'],
                   train_dir_format=config['CLOUD_ML_TRAIN_DIR'],
                   log_dir_format=config['CLOUD_ML_LOG_DIR'],
                   local_model_dir=config['MODEL_DIR'],
                   local_classifier_model_dir=config['CLASSIFIER_MODEL_DIR'])

    def data_dir(self, job_id):
        return self.data_dir_format.format(job_id=job_id)

    def train_dir(self, job_id):
        return self.train_dir_format.format(job_id=job_id)

    def log_dir(self, job_id):
        return self.log_dir_format.format(job_id=job_id)

    def lables_file(self, job_id):
        return os.path.join(self.data_dir(job_id), 'labels.json')

    def features_file(self, job_id):
        return os.path.join(self.data_dir(job_id), 'features.json')

    def create_labels_file(self, job_id, labels):
        with tf.gfile.FastGFile(self.lables_file(job_id), 'w') as f:
            f.write(json.dumps(labels, separators=(',', ':')))

    def create_features_file(self, job_id, files_list, urls_list):
        with tf.gfile.FastGFile(self.features_file(job_id), 'w') as f:
            for label_id, (files, urls) in enumerate(zip(files_list, urls_list)):
                features = self.feature_extractor.get_feature_vectors_from_files(files)

                def _to_json(feature, url):
                    return json.dumps({
                        'label_id': label_id,
                        'image_uri': url,
                        'feature_vector': feature.tolist()
                    }, separators=(',', ':'))

                lines = [_to_json(feature, url) for feature, url in zip(features, urls)]
                f.write('\n'.join(lines))
                f.write('\n')

    def start_training(self, job_id):
        job = ml.Job(name=job_id, client=self.ml_client)
        job.training_input = ml.TrainingInput(
            package_uris=self.package_uris,
            python_module=self.python_module
        )
        job.training_input.with_args(
            '--data_dir={}'.format(self.data_dir(job_id)),
            '--train_dir={}'.format(self.train_dir(job_id)),
            '--log_dir={}'.format(self.log_dir(job_id)),
        )
        job.create()

    def status(self, job_id):
        job = self.ml_client.get_job(job_id)
        losses, features = self._get_losses_and_features(job_id)

        embeddings = []
        if len(features) > 0:
            coords = features_to_coords(features)
            for i, f in enumerate(features):
                embeddings.append({
                    'coords': list(coords[i]),
                    'url': f['url'],
                    'property': f['property']
                })

        return job.state, losses, embeddings

    def download_checkpoints(self, job_id):
        # e.g. resources/models/classifier_candy_sorter_20170221_191316_testid/
        checkpoint_dir = os.path.join(self.local_model_dir, 'classifier_{}'.format(job_id))
        os.mkdir(checkpoint_dir)

        # e.g.  gs://candy-sorter-ml/candy_sorter_20170221_191316_testid/checkpoints
        #  bucket:      candy-sorter-ml
        #  blob_prefix: candy_sorter_20170221_191316_testid/checkpoints
        o = urlparse(self.train_dir(job_id))
        bucket_name = o.hostname
        blob_prefix = o.path[1:]

        bucket = self.storage_client.get_bucket(bucket_name)
        for b in bucket.list_blobs(prefix=blob_prefix):
            if b.name.endswith('/'):
                continue
            to = os.path.join(checkpoint_dir, os.path.basename(b.name))
            b.download_to_filename(to)

        return checkpoint_dir

    def _get_losses_and_features(self, job_id):
        epoch_log_dir = os.path.join(self.log_dir(job_id), 'epochs')
        if tf.gfile.Exists(epoch_log_dir):
            files = tf.gfile.ListDirectory(epoch_log_dir)
            if len(files) == 0:
                return [], []
        else:
            return [], []

        last_log = sorted(files, reverse=True)[0]
        with tf.gfile.FastGFile(os.path.join(epoch_log_dir, last_log), 'r') as f:
            log = json.loads(f.read())
        return log['loss'], log['probs']


def features_to_coords(features, n_dimensions=2):
    d = [f['probs'] for f in features]

    pca = PCA(n_components=n_dimensions)
    pca.fit(d)
    coords = []
    for v in d:
        x = pca.components_[0].dot(v)
        y = pca.components_[1].dot(v)
        coords.append((x, y))

    mms = MinMaxScaler(feature_range=(0.3, 0.7))
    return mms.fit_transform(coords)
