# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import cv2

from candysorter.config import get_config
from candysorter.models.images import calibrate
from candysorter.models.images import detect


if __name__ == '__main__':
    Config = get_config('dev')

    img_src = cv2.imread('./candysorter/resources/data/label.jpg')
    assert(img_src is not None)

    labels = detect.detect_labels(img_src)
    print(labels)
