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

import logging

import cv2
from google.cloud import vision
import numpy as np

logger = logging.getLogger(__name__)

vision_client = vision.Client()


class Candy(object):
    def __init__(self, box_coords, box_dims, box_centroid, cropped_img):
        self.box_coords = box_coords
        self.box_dims = box_dims
        self.box_centroid = box_centroid
        self.cropped_img = cropped_img


class CandyDetector(object):
    def __init__(self,
                 histgram_band=(80, 200),
                 histgram_thres=2.7e-3,
                 bin_thres=150,
                 edge3_thres=250,
                 edge5_thres=230,
                 margin=(20, 20),
                 closing_iter=5,
                 opening_iter=2,
                 erode_iter=10,
                 dilate_iter=3,
                 bg_size_filter=2000,
                 sure_fg_thres=0.5,
                 restore_fg_thres=0.0,
                 box_dim_thres=50):
        self.histgram_band = histgram_band
        self.histgram_thres = histgram_thres

        self.bin_thres = bin_thres
        self.edge3_thres = edge3_thres
        self.edge5_thres = edge5_thres
        self.margin = margin

        self.closing_iter = closing_iter
        self.opening_iter = opening_iter
        self.erode_iter = erode_iter
        self.dilate_iter = dilate_iter

        self.bg_size_filter = bg_size_filter
        self.sure_fg_thres = sure_fg_thres
        self.restore_fg_thres = restore_fg_thres
        self.box_dim_thres = box_dim_thres

    @classmethod
    def from_config(cls, config):
        return cls(histgram_band=config['CANDY_DETECTOR_HISTGRAM_BAND'],
                   histgram_thres=config['CANDY_DETECTOR_HISTGRAM_THRES'],
                   bin_thres=config['CANDY_DETECTOR_BIN_THRES'],
                   edge3_thres=config['CANDY_DETECTOR_EDGE3_THRES'],
                   edge5_thres=config['CANDY_DETECTOR_EDGE5_THRES'],
                   margin=config['CANDY_DETECTOR_MARGIN'],
                   closing_iter=config['CANDY_DETECTOR_CLOSING_ITER'],
                   opening_iter=config['CANDY_DETECTOR_OPENING_ITER'],
                   erode_iter=config['CANDY_DETECTOR_ERODE_ITER'],
                   dilate_iter=config['CANDY_DETECTOR_DILATE_ITER'],
                   bg_size_filter=config['CANDY_DETECTOR_BG_SIZE_FILTER'],
                   sure_fg_thres=config['CANDY_DETECTOR_SURE_FG_THRES'],
                   restore_fg_thres=config['CANDY_DETECTOR_RESTORE_FG_THRES'],
                   box_dim_thres=config['CANDY_DETECTOR_BOX_DIM_THRES'])

    def detect(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Check object
        histr = cv2.calcHist([img_gray], [0], None, [256], [0, 256])
        histr = histr / histr.sum()
        if histr[self.histgram_band[0]:self.histgram_band[1]].sum() <= self.histgram_thres:
            return []

        # Binarize
        _, binarized = cv2.threshold(img_gray, self.bin_thres, 255, cv2.THRESH_BINARY_INV)

        # Edge
        kernel_laplacian_3x3 = np.float32([
            [1, 1, 1],
            [1, -8, 1],
            [1, 1, 1]
        ])
        kernel_gaussian = np.float32([
            [1, 2, 1],
            [2, 4, 2],
            [1, 2, 1]
        ]) / 16
        kernel_laplacian_5x5 = np.float32([
            [-1, -3, -4, -3, -1],
            [-3, 0, 6, 0, -3],
            [-4, 6, 20, 6, -4],
            [-3, 0, 6, 0, -3],
            [-1, -3, -4, -3, -1]
        ])

        edge3 = 255 - cv2.filter2D(img_gray, -1, kernel_laplacian_3x3)
        edge3 = cv2.filter2D(edge3, -1, kernel_gaussian)
        _, binarized_edge3 = cv2.threshold(edge3, self.edge3_thres, 255, cv2.THRESH_BINARY_INV)

        edge5 = 255 - cv2.filter2D(img_gray, -1, kernel_laplacian_5x5)
        edge5 = cv2.filter2D(edge5, -1, kernel_gaussian)
        _, binarized_edge5 = cv2.threshold(edge5, self.edge5_thres, 255, cv2.THRESH_BINARY_INV)

        binarized_edge = cv2.bitwise_or(binarized_edge3, binarized_edge5)
        binarized = cv2.bitwise_or(binarized, binarized_edge)

        # Fill the margin with black
        binarized[:self.margin[0], :] = 0
        binarized[-self.margin[0]:, :] = 0
        binarized[:, :self.margin[1]] = 0
        binarized[:, -self.margin[1]:] = 0

        # Remove noise
        kernel = np.ones((3, 3), np.uint8)
        closed = cv2.morphologyEx(binarized, cv2.MORPH_CLOSE, kernel, iterations=self.closing_iter)

        closed, contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(closed, contours, -1, 255, -1)

        opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=self.opening_iter)

        # Erode
        eroded = cv2.erode(closed, kernel, iterations=self.erode_iter)

        # Sure background
        bg = cv2.dilate(opened, kernel, iterations=self.dilate_iter)
        n, markers_bg, sizes, cogs = cv2.connectedComponentsWithStats(bg)
        sizes = sizes.take(4, axis=1)
        sure_bg = bg.copy()
        for i in range(1, n):
            if sizes[i] < self.bg_size_filter:
                sure_bg -= (markers_bg == i).astype(np.uint8) * 255

        # Sure foreground
        dist = cv2.distanceTransform(eroded, cv2.DIST_L2, 5)
        if self.sure_fg_thres <= 1.0:
            _, fg = cv2.threshold(dist, self.sure_fg_thres * dist.max(), 255, cv2.THRESH_BINARY)
        else:
            _, fg = cv2.threshold(dist, self.sure_fg_thres, 255, cv2.THRESH_BINARY)
        fg = np.uint8(fg)

        # Restore foreground
        _, markers_eroded = cv2.connectedComponents(eroded)

        oids_eroded, counts_eroded = np.unique(markers_eroded, return_counts=True)
        oids_fg, counts_fg = np.unique(markers_eroded * (fg > 0), return_counts=True)

        temp = np.array([
            counts_fg[np.where(oids_fg == oid)[0][0]] if oid in oids_fg else 0
            for oid in oids_eroded
        ])
        oids_sure_fg = oids_eroded[
            (oids_eroded > 0) & ~(1.0 * temp / counts_eroded > self.restore_fg_thres)
        ]
        sure_fg = np.bool_(fg)
        for oid in oids_sure_fg:
            sure_fg = np.logical_or(sure_fg, markers_eroded == oid)
        sure_fg = 255 * np.uint8(sure_fg)

        # Unknown region
        # unknown = cv2.subtract(sure_bg, sure_fg)

        # Label
        _, markers = cv2.connectedComponents(sure_fg)

        # Segmentate
        _, markers = cv2.distanceTransformWithLabels(255 - sure_fg, cv2.DIST_L2, 5, labels=markers)
        markers = (sure_bg // 255) * markers
        markers += 1

        candies = []
        for i in [i for i in list(np.unique(markers)) if i > 1]:
            temp = np.zeros(markers.shape, dtype='uint8')
            temp[markers == i] = 255
            _, _contours, _ = cv2.findContours(temp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contour = _contours[0]

            box_coords, box_dims, box_centroid = _bounding_box_of(contour)
            if any([dim <= self.box_dim_thres for dim in box_dims]):
                continue
            cropped_img = _crop_candy(img, markers != i, box_coords, box_dims, box_centroid)

            candies.append(Candy(box_coords=box_coords,
                                 box_dims=box_dims,
                                 box_centroid=box_centroid,
                                 cropped_img=cropped_img))

        return candies


def _crop_candy(img, mask, box_coords, box_dims, box_centroid):

    # White out other than candy
    _img = img.copy()
    _img[mask] = 255

    # Center of image
    h, w, _ = _img.shape
    center = (w / 2, h / 2)

    # Get bounding box coordinates
    x1, y1 = box_coords[0]  # top-left
    x2, y2 = box_coords[1]  # top-right

    # Get bounding box dimensions
    pw = box_dims[0]
    ph = box_dims[1]

    # Determine angle of rotation (in degrees)
    # FIXME: x1 == x2
    angle = np.arctan((y2 - y1) / (x2 - x1)) * 180 / np.pi

    # Center of bounding pox
    tx, ty = box_centroid

    # Translation matrix to move candy to center of image
    trans_mat = np.float32([[1, 0, -tx + w / 2], [0, 1, -ty + h / 2], [0, 0, 1]])

    # Rotation matrix
    rot_mat = cv2.getRotationMatrix2D(center, angle, 1)
    rot_mat = np.vstack((rot_mat, [0, 0, 1]))

    # Translation+Rotation matrix
    mat = np.dot(rot_mat, trans_mat)

    # Transform image
    _img = cv2.warpAffine(_img, mat[0:2, :], (w, h), borderValue=(255, 255, 255))

    # Crop candy
    pwh = max(pw, ph)

    cx1 = int(np.floor((w - pwh) / 2))
    cx2 = int(np.ceil((w + pwh) / 2))
    cy1 = int(np.floor((h - pwh) / 2))
    cy2 = int(np.ceil((h + pwh) / 2))

    return _img[cy1:cy2, cx1:cx2]


def _bounding_box_of(contour):
    rotbox = cv2.minAreaRect(contour)
    coords = cv2.boxPoints(rotbox)

    xrank = np.argsort(coords[:, 0])

    left = coords[xrank[:2], :]
    yrank = np.argsort(left[:, 1])
    left = left[yrank, :]

    right = coords[xrank[2:], :]
    yrank = np.argsort(right[:, 1])
    right = right[yrank, :]

    #            top-left,       top-right,       bottom-right,    bottom-left
    box_coords = tuple(left[0]), tuple(right[0]), tuple(right[1]), tuple(left[1])
    box_dims = rotbox[1]
    box_centroid = int((left[0][0] + right[1][0]) / 2.0), int((left[0][1] + right[1][1]) / 2.0)

    return box_coords, box_dims, box_centroid


def detect_labels(img):
    image = vision_client.image(content=cv2.imencode('.jpg', img)[1].tostring())
    try:
        texts = image.detect_text()
    except KeyError:
        # workaround for error in client library when encountering unexpected response bodies
        # https://github.com/GoogleCloudPlatform/google-cloud-python/issues/2930
        return [' ']
    # e.g.
    # (image)
    #   Sweet
    #      chocolate
    #
    # (visionAPI)
    #   [
    #     {"description: "Sweet\nchocolate", ...},
    #     {"description: "Sweet", ...},
    #     {"description: "chocolate", ...}
    #   ]
    #
    # (result)
    #   ['SWEET', 'CHOCOLATE']
    labels = set()
    for text in texts:
        words = [w.upper().strip() for w in text.description.split()]
        words = [w for w in words if w]
        labels.update(words)
    return list(labels)
