# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import cv2

from candysorter.models.images.calibrate import ImageCalibrator

if __name__ == '__main__':
    calibrator = ImageCalibrator(area=(1625, 1100), scale=550)
    img = cv2.imread('./candysorter/resources/data/org/captured.jpg')
    cv2.imwrite('test_org.jpg', img)

    img = calibrator.calibrate(img)
    cv2.imwrite('test_calibrated.jpg', img)
