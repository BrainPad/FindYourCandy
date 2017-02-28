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
import os
import logging
import json
import sys

import tensorflow as tf
import cv2

INPUT_DATA_TENSOR_NAME = 'DecodeJpeg:0'
FEATURE_TENSOR_NAME = 'pool_3/_reshape:0'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)-7s %(levelname)-7s %(message)s'
)
logger = logging.getLogger(__name__)


class FeatureExtractor(object):
    """
    FeatureExtractor extracts 2048-dimension feature vectors from image files
    using inception-v3.
    """

    def __init__(self, model_file):
        # load inception-v3 model
        self.graph = tf.Graph()
        with tf.gfile.FastGFile(model_file, 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            with self.graph.as_default():
                _ = tf.import_graph_def(graph_def, name='')

            feature = tf.reshape(self.graph.get_tensor_by_name(FEATURE_TENSOR_NAME), [-1])
        self.feature_op = feature

        self.saver = None

    @classmethod
    def from_model_dir(cls, model_dir):
        return cls(os.path.join(model_dir, 'classify_image_graph_def.pb'))

    def get_feature_vector(self, img_bgr):
        with tf.Session(graph=self.graph) as sess:
            feature_data = sess.run(
                self.feature_op,
                {INPUT_DATA_TENSOR_NAME: img_bgr}
            )
        return feature_data.reshape(-1, feature_data.shape[0])

    def get_feature_vectors_from_files(self, image_paths):
        # Decode image
        with self.graph.as_default():
            image_path = tf.placeholder(tf.string, None, 'image_path')
            image = tf.image.decode_jpeg(tf.read_file(image_path))

        # Extract features
        features = []
        with tf.Session(graph=self.graph) as sess:
            for path in image_paths:
                image_data = sess.run(
                    image,
                    {image_path: path}
                )
                feature_data = sess.run(
                    self.feature_op,
                    {INPUT_DATA_TENSOR_NAME: image_data}
                )
                features.append(feature_data)
        return features


class ImagePathGeneratorForTraining(object):
    def __init__(self, image_dir, extension='jpg'):
        self.image_dir = image_dir
        self.extension = extension

    def get_labels(self):
        return sorted(
            [sub_dir for sub_dir in tf.gfile.ListDirectory(self.image_dir)
             if tf.gfile.IsDirectory('/'.join((self.image_dir, sub_dir)))
             ]
        )

    def __iter__(self):
        for label_id, label in enumerate(self.get_labels()):
            dir_path = os.path.join(self.image_dir, label)
            paths = tf.gfile.Glob('{}/*.{}'.format(dir_path, self.extension))
            for path in paths:
                yield path, label_id
        raise StopIteration()


class ImagePathGeneratorForPrediction(object):
    def __init__(self, image_dir, extension='jpg'):
        self.image_dir = image_dir
        self.extension = extension

    def __iter__(self):
        paths = tf.gfile.Glob('{}/*.{}'.format(self.image_dir, self.extension))
        for path in paths:
            yield path, None
        raise StopIteration()


class FeaturesDataWriter(object):
    """
    FeatureDataWriter extracts feature data from images and write to json lines
    """

    def __init__(self, path_generator, feature_extractor):
        self.path_generator = path_generator
        self.extractor = feature_extractor

    def write_features(self, features_data_path):
        with tf.gfile.FastGFile(features_data_path, 'w') as f:
            for path, label_id in self.path_generator:
                sys.stdout.write("\rprocessing image: {}".format(path))
                sys.stdout.flush()
                line = self.extract_data_for_path(path, label_id)
                f.write(json.dumps(line) + '\n')

    def extract_data_for_path(self, image_path, label_id):
        vector = self.extractor.get_feature_vectors_from_files([image_path])
        line = {
            'image_uri': image_path,
            'feature_vector': vector[0].tolist()
        }
        if label_id is not None:
            line['label_id'] = label_id
        return line


def write_labels(labels, labels_data_path):
    with tf.gfile.FastGFile(labels_data_path, 'w') as f:
        f.write(json.dumps(labels))


def main():
    parser = argparse.ArgumentParser(description='Run Dobot WebAPI.')
    parser.add_argument('output_dir', nargs=1, type=str)
    parser.add_argument('--image_dir', type=str)
    parser.add_argument('--model_file', type=str, default=None)
    parser.add_argument('--for_prediction', action='store_true')

    args = parser.parse_args()
    output_dir = args.output_dir[0]

    labels_file = os.path.join(output_dir, 'labels.json')
    features_file = os.path.join(output_dir, 'features.json')
    model_file = args.model_file

    if args.for_prediction:
        path_gen = ImagePathGeneratorForPrediction(args.image_dir)
    else:
        path_gen = ImagePathGeneratorForTraining(args.image_dir)
        logger.info("writing label file: {}".format(labels_file))
        write_labels(path_gen.get_labels(), labels_file)

    extractor = FeatureExtractor(model_file)
    writer = FeaturesDataWriter(path_gen, extractor)

    logger.info("writing features file: {}".format(features_file))
    writer.write_features(features_file)


if __name__ == "__main__":
    main()
