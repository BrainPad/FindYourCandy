# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os

import cv2

from candysorter.config import get_config
from candysorter.models.images import capture

if __name__ == '__main__':
    img = capture.capture_image()
    print(img.shape)
    cv2.imwrite('test.png', img)
