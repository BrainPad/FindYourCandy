# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime
import logging
import os
import re
import shutil
import time

import cv2
from flask import abort, Blueprint, jsonify, request, url_for
from google.cloud.logging import Client as LogClient
import numpy as np
import requests
from scipy import ndimage
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from werkzeug.contrib.cache import SimpleCache

from candysorter.config import Config
from candysorter.ext.google.cloud.ml import Client as MlClient, Job, State, TrainingInput
from candysorter.models.images.calibrate import ImageCalibrator
from candysorter.models.images.classify import CandyClassifier
from candysorter.models.images.detect import CandyDetector, detect_labels
from candysorter.utils import load_class

logger = logging.getLogger(__name__)

api = Blueprint('api', __name__, url_prefix='/api')

text_analyzer = None
candy_detector = None
candy_classifier = None
image_capture = None
image_calibrator = None

ml_client = MlClient()
log_client = LogClient()

cache = SimpleCache(default_timeout=600)


@api.record
def record(state):
    global text_analyzer
    text_analyzer = load_class(Config.CLASS_TEXT_ANALYZER).from_config(Config)
    text_analyzer.init()

    global candy_detector
    candy_detector = CandyDetector.from_config(Config)

    global candy_classifier
    candy_classifier = CandyClassifier.from_config(Config)
    candy_classifier.init()

    global image_capture
    image_capture = load_class(Config.CLASS_IMAGE_CAPTURE).from_config(Config)

    global image_calibrator
    image_calibrator = ImageCalibrator.from_config(Config)


@api.errorhandler(400)
def handle_http_error(e):
    return jsonify(error=e.code, message=e.name.lower()), e.code


@api.errorhandler(Exception)
def handle_exception(e):
    logger.exception('Unexpected error.')
    return jsonify(error=500, message='internal server error'), 500


def _cache_key(id_, key):
    return '{}:{}'.format(id_, key)


@api.route('/morphs', methods=['POST'])
def morphs():
    id_ = request.json.get('id')
    if not id_:
        abort(400)
    text = request.json.get('text')
    if not text:
        abort(400)

    tokens = text_analyzer.analyze_syntax(text)
    return jsonify(morphs=[
        dict(word=t.text.content,
             depend=dict(label=t.dep.label, index=[
                 _i for _i, _t in enumerate(tokens)
                 if _i != i and _t.dep.index == i
             ]),
             pos=dict(tag=t.pos.tag, case=t.pos.case, number=t.pos.number))
        for i, t in enumerate(tokens)
    ])


@api.route('/similarities', methods=['POST'])
def similarities():
    id_ = request.json.get('id')
    if not id_:
        abort(400)
    text = request.json.get('text')
    if not text:
        abort(400)

    # Issue ID
    predict_id = _job_id(id_)
    logger.info('Calculate similarities start: id=%s', predict_id)

    # Analyze text
    logger.info('Analyaing text.')
    labels = text_analyzer.labels
    tokens = text_analyzer.analyze_syntax(text)
    words = text_analyzer.filter_tokens(tokens)

    # Calculate speech similarity
    logger.info('Calculating speech similarity.')
    speech_sim = text_analyzer.calc_similarities(words)

    # Capture image
    logger.info('Capturing image.')
    img = _capture_image()

    # Detect candies
    logger.info('Detecting candies.')
    candies = candy_detector.detect(img)
    logger.info('  %d candies detected.', len(candies))

    # Create image directory
    save_dir = _create_save_dir(predict_id)

    # Save snapshot image
    logger.info('Saving snapshot image.')
    snapshot_file = os.path.join(save_dir, 'snapshot.jpg')
    snapshot_url = _image_url(snapshot_file)
    cv2.imwrite(snapshot_file, img)

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

    # Save target centroid
    logger.info('Saving target point.')
    nearest_centroid = candies[nearest_idx].box_centroid
    target_point = image_calibrator.get_coordinate(nearest_centroid[0], nearest_centroid[1])
    cache.set(_cache_key(id_, 'target'), target_point)

    # For json
    def _sim_as_json(sim):
        return [dict(label=l, lid=i + 1, em=np.asscalar(s))
                for i, (l, s) in enumerate(zip(labels, sim))]

    def _coords_as_json(rsim):
        return list(rsim)

    def _box_as_json(box_coords):
        return [[x.astype(int), y.astype(int)] for x, y in box_coords]

    return jsonify(similarities=dict(
        force=_sim_as_json(speech_sim),
        url=snapshot_url,
        embedded=[
            dict(url=url,
                 similarities=_sim_as_json(sim),
                 coords=_coords_as_json(rsim),
                 box=_box_as_json(candy.box_coords))
            for candy, sim, rsim, url in zip(candies, candy_sims, candy_rsims, candy_urls)
        ],
        nearest=dict(url=candy_urls[nearest_idx],
                     similarities=_sim_as_json(candy_sims[nearest_idx]),
                     coords=_coords_as_json(candy_rsims[nearest_idx]),
                     box=_box_as_json(candies[nearest_idx].box_coords)),
    ))


def _job_id(id_):
    # e.g. reqid -> 20170209_130952_reqid
    return '{}_{}'.format(datetime.now().strftime('%Y%m%d_%H%M%S'), id_)


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


def _create_save_dir(job_id):
    # e.g. 20170209_130952_reqid -> /tmp/download/image/20170209_130952_reqid/
    d = os.path.join(Config.DOWNLOAD_IMAGE_DIR, job_id)
    os.makedirs(d)
    return d


def _candy_file(save_dir, i):
    # e.g. /tmp/download/image/20170209_130952_reqid/candy_001.png
    return os.path.join(save_dir, 'candy_{:02d}.jpg'.format(i))


def _image_url(image_file):
    # e.g. 20170209_130952_reqid/candy_001.png
    rel = os.path.relpath(image_file, Config.DOWNLOAD_IMAGE_DIR)

    # e.g. /image/20170209_130952_reqid/candy_001.png
    return url_for('ui.image', filename=rel)


def _reduce_dimension(speech_sim, candy_sims):
    l = [speech_sim]
    l.extend(candy_sims)
    pca = PCA(n_components=2)
    rl = pca.fit_transform(l)
    mms = MinMaxScaler(feature_range=(0.3, 0.7))
    rl = mms.fit_transform(rl)
    return rl[0], rl[1:]


@api.route('/pickup', methods=['POST'])
def pickup():
    id_ = request.json.get('id')
    if not id_:
        abort(400)
    target_point = cache.get(_cache_key(id_, 'target'))
    if not target_point:
        abort(400)

    logger.info('Picking candy. x=%f, y=%f', target_point[0], target_point[1])
    requests.post(Config.PICKUP_ENDOPOINT, json={'x': target_point[0], 'y': target_point[1]})
    return jsonify()


@api.route('/capture', methods=['POST'])
def capture():
    id_ = request.json.get('id')
    if not id_:
        abort(400)
    step = request.json.get('step')
    if not step:
        abort(400)
    step = int(step)

    logger.info('Capture step %d', step)

    key_train_id = _cache_key(id_, 'train_id')
    train_id = cache.get(key_train_id)
    if not train_id:
        train_id = _job_id(id_)
        cache.set(key_train_id, train_id)

    key_save_dir = _cache_key(id_, 'train_save_dir')
    save_dir_root = cache.get(key_save_dir)
    if not save_dir_root:
        save_dir_root = _create_save_dir(train_id)
        cache.set(key_save_dir, save_dir_root)

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
    img_label = img[:Config.TRAIN_LABEL_AREA_HEIGHT]
    img_candies = img[Config.TRAIN_LABEL_AREA_HEIGHT:]

    # Save snapshot image
    logger.info('Saving snapshot image.')
    cv2.imwrite(os.path.join(save_dir, 'snapshot.jpg'), img)
    cv2.imwrite(os.path.join(save_dir, 'label.jpg'), img_label)
    cv2.imwrite(os.path.join(save_dir, 'candies.jpg'), img_candies)

    # Detect label
    logger.info('Detecting label.')
    labels = detect_labels(img_label)
    logger.info('  Detected labels: %s', labels)

    # Cache label
    key_labels = _cache_key(id_, 'labels')
    cache_labels = cache.get(key_labels)
    if not cache_labels:
        cache_labels = [None] * 4
    cache_labels[step - 1] = labels
    cache.set(key_labels, cache_labels)

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
def train():
    id_ = request.json.get('id')
    if not id_:
        abort(400)
    train_id = cache.get(_cache_key(id_, 'train_id'))
    if not train_id:
        abort(400)

    job_name = _job_name(train_id)

    # TODO: Vectorize
    # TODO: Upload to gcs

    job = Job(name=job_name, client=ml_client)
    job.training_input = TrainingInput(
        package_uris=Config.CLOUD_ML_PACKAGE_URIS,
        python_module=Config.CLOUD_ML_PYTHON_MODULE
    )
    job.training_input.with_args(
        '--train_dir={}'.format(Config.CLOUD_ML_TRAIN_DIR.format(name=job_name)),
        '--log_dir={}'.format(Config.CLOUD_ML_LOG_DIR.format(name=job_name)),
        '--data_dir={}'.format(Config.CLOUD_ML_DATA_DIR.format(name=job_name)),
    )
    job.create()

    return jsonify({})


CLOUD_ML_STATE_TO_API_STATE = {
    State.STATE_UNSPECIFIED: 'running',
    State.QUEUED: 'running',
    State.PREPARING: 'running',
    State.RUNNING: 'running',
    State.SUCCEEDED: 'complete',
    State.FAILED: 'failed',
    State.CANCELLING: 'running',
    State.CANCELLED: 'canceled',
}


@api.route('/status')
def status():
    id_ = request.args.get('id')
    if not id_:
        abort(400)
    train_id = cache.get(_cache_key(id_, 'train_id'))
    if not train_id:
        abort(400)

    job_name = _job_name(train_id)
    job = ml_client.get_job(job_name)

    # TODO: get embedded

    return jsonify(loss=_get_losses(job_name),
                   embedded=[],
                   status=CLOUD_ML_STATE_TO_API_STATE[job.state])


def _job_name(train_id):
    return 'candy_sorter_{}'.format(train_id)


def _get_losses(job_name):
    filter_ = 'resource.type:ml_job AND resource.labels.job_id:{}'.format(job_name)
    messages = [e.payload['message'] if isinstance(e.payload, dict) else e.payload
                for e in log_client.list_entries(filter_=filter_)]

    # FIXME: Umm...
    r = re.compile('^[0-9]+th epoch end with loss ([0-9.]+)\.$')
    groups = [r.match(m) for m in messages]
    return [float(g.group(1)) for g in groups if g]
