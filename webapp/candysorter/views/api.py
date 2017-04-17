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

from datetime import datetime
from functools import wraps
import glob
import logging
import os
import shutil
import string
import time

import cv2
from flask import abort, Blueprint, g, jsonify, request, url_for
import numpy as np
import requests
from scipy import ndimage
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler

from candysorter.cache import Cache
from candysorter.ext.google.cloud.ml import State
from candysorter.models.images.calibrate import ImageCalibrator
from candysorter.models.images.classify import CandyClassifier
from candysorter.models.images.detect import CandyDetector, detect_labels
from candysorter.models.images.filter import exclude_unpickables
from candysorter.models.images.train import CandyTrainer
from candysorter.utils import load_class, random_str, symlink_force

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')
config = None
cache = Cache()

text_analyzer = None
candy_detector = None
candy_classifier = None
candy_trainer = None
image_capture = None
image_calibrator = None


@api.record
def record(state):
    global config
    config = state.app.config

    global text_analyzer
    text_analyzer = load_class(config['CLASS_TEXT_ANALYZER']).from_config(config)
    text_analyzer.init()

    global candy_detector
    candy_detector = CandyDetector.from_config(config)

    global candy_classifier
    candy_classifier = CandyClassifier.from_config(config)
    candy_classifier.init()

    global candy_trainer
    candy_trainer = CandyTrainer.from_config(config)

    global image_capture
    image_capture = load_class(config['CLASS_IMAGE_CAPTURE']).from_config(config)

    global image_calibrator
    image_calibrator = ImageCalibrator.from_config(config)


@api.errorhandler(400)
def handle_http_error(e):
    return jsonify(error=e.code, message=e.name.lower()), e.code


@api.errorhandler(Exception)
def handle_exception(e):
    logger.exception('Unexpected error.')
    return jsonify(error=500, message='internal server error'), 500


def id_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method == 'POST':
            id_ = request.json.get('id')
        else:
            id_ = request.args.get('id')
        if not id_:
            abort(400)
        g.id = id_
        return f(*args, **kwargs)

    return wrapper


@api.route('/morphs', methods=['POST'])
@id_required
def morphs():
    text = request.json.get('text')
    if not text:
        abort(400)
    lang = request.json.get('lang', 'en')

    logger.info('=== Analyze text: id=%s ===', g.id)

    tokens = text_analyzer.analyze_syntax(text, lang)
    return jsonify(morphs=[
        dict(
            word=t.text.content,
            depend=dict(
                label=t.dep.label,
                index=[_i for _i, _t in enumerate(tokens) if _i != i and _t.dep.index == i]),
            pos=dict(tag=t.pos.tag, case=t.pos.case, number=t.pos.number))
        for i, t in enumerate(tokens)
    ])


@api.route('/similarities', methods=['POST'])
@id_required
def similarities():
    text = request.json.get('text')
    if not text:
        abort(400)
    lang = request.json.get('lang', 'en')

    logger.info('=== Calculate similarities: id=%s ===', g.id)

    # Session
    session_id = _session_id()

    # Analyze text
    logger.info('Analyaing text.')
    labels = text_analyzer.labels
    tokens = text_analyzer.analyze_syntax(text, lang)

    # Calculate speech similarity
    logger.info('Calculating speech similarity.')
    speech_sim = text_analyzer.calc_similarities(tokens, lang)

    # Capture image
    logger.info('Capturing image.')
    img = _capture_image()

    # Detect candies
    logger.info('Detecting candies.')
    candies = candy_detector.detect(img)
    logger.info('  %d candies detected.', len(candies))

    # Create image directory
    save_dir = _create_save_dir(session_id)

    # Save snapshot image
    logger.info('Saving snapshot image.')
    snapshot_file = os.path.join(save_dir, 'snapshot.jpg')
    snapshot_url = _image_url(snapshot_file)
    cv2.imwrite(snapshot_file, img)

    # Exclude unpickupables
    logger.info('Excluding unpickables.')
    candies = exclude_unpickables(image_calibrator, candies)
    logger.info('  %d candies pickable.', len(candies))

    # Save candy images
    logger.info('Saving candy images.')
    candy_files = [_candy_file(save_dir, i) for i, c in enumerate(candies)]
    candy_urls = [_image_url(f) for f in candy_files]
    for c, f in zip(candies, candy_files):
        cv2.imwrite(f, c.cropped_img)

    # Calculate candy similarities
    logger.info('Calculating candy similarities.')
    candy_sims = [candy_classifier.classify(c.cropped_img) for c in candies]

    # Reduce dimension
    logger.info('Reducing dimension.')
    speech_rsim, candy_rsims = _reduce_dimension(speech_sim, candy_sims)

    # Find nearest candy
    logger.info('Finding nearest candy.')
    nearest_idx = np.argmax([speech_sim.dot(s) for s in candy_sims])
    logger.info('  Nearest candy: idx=%d, url=%s', nearest_idx, candy_urls[nearest_idx])

    # Save pickup point
    logger.info('Saving pickup point.')
    nearest_centroid = candies[nearest_idx].box_centroid
    pickup_point = image_calibrator.get_coordinate(nearest_centroid[0], nearest_centroid[1])
    cache.set('pickup_point', pickup_point)

    # For json
    def _sim_as_json(sim):
        return [
            dict(label=l, lid=i + 1, em=np.asscalar(s))
            for i, (l, s) in enumerate(zip(labels, sim))
        ]

    def _coords_as_json(rsim):
        return list(rsim)

    def _box_as_json(box_coords):
        return [[x.astype(int), y.astype(int)] for x, y in box_coords]

    return jsonify(similarities=dict(
        force=_sim_as_json(speech_sim),
        url=snapshot_url,
        embedded=[
            dict(
                url=url,
                similarities=_sim_as_json(sim),
                coords=_coords_as_json(rsim),
                box=_box_as_json(candy.box_coords))
            for candy, sim, rsim, url in zip(candies, candy_sims, candy_rsims, candy_urls)
        ],
        nearest=dict(
            url=candy_urls[nearest_idx],
            similarities=_sim_as_json(candy_sims[nearest_idx]),
            coords=_coords_as_json(candy_rsims[nearest_idx]),
            box=_box_as_json(candies[nearest_idx].box_coords)), ))


@api.route('/pickup', methods=['POST'])
@id_required
def pickup():
    pickup_point = cache.get('pickup_point')
    if not pickup_point:
        abort(400)

    logger.info('=== Pickup candy: id=%s ===', g.id)

    logger.info('Picking candy. x=%f, y=%f', pickup_point[0], pickup_point[1])
    requests.post(config['PICKUP_ENDOPOINT'], json=dict(x=pickup_point[0], y=pickup_point[1]))
    return jsonify()


@api.route('/capture', methods=['POST'])
@id_required
def capture():
    step = request.json.get('step')
    if not step or not (1 <= step <= 4):
        abort(400)

    # Session
    if step == 1:
        session_id = _session_id()
        cache.set('session_id', session_id)

        save_dir_root = _create_save_dir(session_id)
        cache.set('save_dir', save_dir_root)

        labels_list = [None] * 4
        cache.set('labels_list', labels_list)
    else:
        session_id = cache.get('session_id')
        if not session_id:
            abort(400)
        save_dir_root = cache.get('save_dir')
        if not save_dir_root:
            abort(400)
        labels_list = cache.get('labels_list')
        if not labels_list:
            abort(400)

    logger.info('=== Capture step %d: id=%s, session=%s ===', step, g.id, session_id)

    # Create image directory
    save_dir = os.path.join(save_dir_root, 'train{:02d}'.format(step))
    shutil.rmtree(save_dir, ignore_errors=True)
    os.makedirs(save_dir)

    # Capture image
    logger.info('Capturing image.')
    img = _capture_image()

    # Rotate image
    logger.info('Rotating image.')
    img = ndimage.rotate(img, -90)

    # Crop label and candies
    logger.info('Cropping image.')
    img_label = img[:config['TRAIN_LABEL_AREA_HEIGHT']]
    img_candies = img[config['TRAIN_LABEL_AREA_HEIGHT']:]

    # Save snapshot image
    logger.info('Saving snapshot image.')
    cv2.imwrite(os.path.join(save_dir, 'snapshot.jpg'), img)
    cv2.imwrite(os.path.join(save_dir, 'label.jpg'), img_label)
    cv2.imwrite(os.path.join(save_dir, 'candies.jpg'), img_candies)

    # Detect label
    logger.info('Detecting label.')
    labels = detect_labels(img_label)
    logger.info('  Detected labels: %s', labels)

    # Save label
    labels_list[step - 1] = labels
    cache.set('labels_list', labels_list)

    # Detect candies
    logger.info('Detecting candies.')
    candies = candy_detector.detect(img_candies)
    logger.info('  %d candies detected.', len(candies))

    # Save candy images
    logger.info('Saving candy images.')
    candy_files = [_candy_file(save_dir, i) for i, c in enumerate(candies)]
    for c, f in zip(candies, candy_files):
        cv2.imwrite(f, c.cropped_img)
    candy_urls = [_image_url(f) for f in candy_files]

    return jsonify(labels=labels, urls=candy_urls)


@api.route('/train', methods=['POST'])
@id_required
def train():
    session_id = cache.get('session_id')
    if not session_id:
        abort(400)
    labels_list = cache.get('labels_list')
    if not labels_list:
        abort(400)
    save_dir_root = cache.get('save_dir')
    if not save_dir_root:
        abort(400)

    logger.info('=== Start training: id=%s, session=%s ===', g.id, session_id)

    job_id = _job_id(session_id)

    logger.info('Creating labels file: job_id=%s', job_id)
    labels = [' '.join(l) for l in labels_list]
    candy_trainer.create_labels_file(job_id, labels)

    logger.info('Creating features file: job_id=%s', job_id)
    files_list = []
    urls_list = []
    for i in range(4):
        path = os.path.join(save_dir_root, 'train{:02d}'.format(i + 1), 'candy_*.jpg')
        files = glob.glob(path)
        files_list.append(files)
        urls_list.append([_image_url(f) for f in files])
    candy_trainer.create_features_file(job_id, files_list, urls_list)

    logger.info('Starting training: job_id=%s', job_id)
    candy_trainer.start_training(job_id)

    return jsonify({})


CLOUD_ML_STATE_TO_API_STATE = {
    State.STATE_UNSPECIFIED: 'preparing',
    State.QUEUED: 'preparing',
    State.PREPARING: 'preparing',
    State.RUNNING: 'running',
    State.SUCCEEDED: 'complete',
    State.FAILED: 'failed',
    State.CANCELLING: 'canceled',
    State.CANCELLED: 'canceled',
}


@api.route('/status', methods=['POST'])
@id_required
def status():
    session_id = cache.get('session_id')
    if not session_id:
        abort(400)

    logger.info('=== Training status: id=%s, session=%s ===', g.id, session_id)

    job_id = _job_id(session_id)
    _status, losses, embedded = candy_trainer.status(job_id)
    logger.info('Training status: %s', _status)

    status = CLOUD_ML_STATE_TO_API_STATE[_status]
    if status == 'failed':
        logger.error('Failed to train: job_id=%s', job_id)
    if status == 'complete':
        key = 'model_updated_{}'.format(job_id)
        if not cache.get(key):
            logger.info('Training completed, updating model: job_id=%s', job_id)
            new_checkpoint_dir = candy_trainer.download_checkpoints(job_id)
            symlink_force(new_checkpoint_dir, config['CLASSIFIER_MODEL_DIR'])
            text_analyzer.reload()
            candy_classifier.reload()
            cache.set(key, True)

    return jsonify(status=status, loss=losses, embedded=embedded)


@api.route('/_labels')
def labels():
    return jsonify(labels=text_analyzer.labels)


@api.route('/_reload', methods=['POST'])
def reload():
    text_analyzer.reload()
    candy_classifier.reload()
    return jsonify({})


@api.route('/_reset', methods=['POST'])
def reset():
    symlink_force(
        os.path.basename(config['CLASSIFIER_MODEL_DIR_INITIAL']), config['CLASSIFIER_MODEL_DIR'])
    text_analyzer.reload()
    candy_classifier.reload()
    return jsonify({})


def _session_id():
    # e.g. 20170209_130952_reqid
    return '{}_{}'.format(datetime.now().strftime('%Y%m%d_%H%M%S'), g.id)


def _capture_image(retry_count=5, retry_interval=0.1):
    for i in range(retry_count):
        try:
            img = image_capture.capture()
            img = image_calibrator.calibrate(img)
            return img
        except Exception:
            logger.warning('  Retrying: %d times.', (i + 1))
            time.sleep(retry_interval)
    raise Exception('Failed to capture image.')


def _create_save_dir(session_id):
    # e.g. 20170209_130952_reqid -> /tmp/download/image/20170209_130952_reqid/
    d = os.path.join(config['DOWNLOAD_IMAGE_DIR'], session_id)
    os.makedirs(d)
    return d


def _candy_file(save_dir, i):
    # e.g. /tmp/download/image/20170209_130952_reqid/candy_01_xxxxxxxx.png
    return os.path.join(
        save_dir, 'candy_{:02d}_{}.jpg'.format(i, random_str(8, string.lowercase + string.digits)))


def _image_url(image_file):
    # e.g. 20170209_130952_reqid/candy_01_xxxxxxxx.png
    rel = os.path.relpath(image_file, config['DOWNLOAD_IMAGE_DIR'])

    # e.g. /image/20170209_130952_reqid/candy_01_xxxxxxxx.png
    return url_for('ui.image', filename=rel)


def _reduce_dimension(speech_sim, candy_sims):
    l = [speech_sim]
    l.extend(candy_sims)
    pca = PCA(n_components=2)
    rl = pca.fit_transform(l)
    mms = MinMaxScaler(feature_range=(0.3, 0.7))
    rl = mms.fit_transform(rl)
    return rl[0], rl[1:]


def _job_id(session_id):
    return 'candy_sorter_{}'.format(session_id)
