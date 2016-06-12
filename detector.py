#!/usr/bin/env python2

from sys import argv
import cv2 as opencv
import numpy as np
import hashlib
import os
import shutil


def get_triangles_from_contours(contours):
    for contour in contours:
        approx = opencv.approxPolyDP(contour, 0.03 * opencv.arcLength(contour, True), True)
        if len(approx) == 3:
            yield approx


def get_triangle_angles(contour):
    points = np.array([c[0] for c in contour])

    a = points[1] - points[0]
    b = points[2] - points[1]
    c = points[0] - points[2]

    angles = []
    for e1, e2 in ((a, -b), (b, -c), (c, -a)):
        num = np.dot(e1, e2)
        denom = np.linalg.norm(e1) * np.linalg.norm(e2)
        angles.append(np.arccos(num/denom) * 180 / np.pi)
    return angles


# preserves the ratio
def resize_to_max(image, _max=800):
    _max += 0.0
    width, height = image.shape[:2]
    ratio = _max / max(width, height)
    if ratio >= 1:
        return image

    return opencv.resize(image, (0, 0), fx=ratio, fy=ratio)


def checksum_md5(filename):
    md5 = hashlib.md5()
    with open(filename,'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def detect_illuminati(path, cache=True):
    checksum = checksum_md5(path)
    path_cache = 'static/images/cache/{}.jpg'.format(checksum)
    path_cache_confirmed = 'static/images/cache/{}_confirmed.jpg'.format(checksum)

    if cache and (os.path.exists(path_cache_confirmed) or os.path.exists(path_cache)):
        return checksum

    shutil.copy(path, path_cache)

    image_original_color = resize_to_max(opencv.imread(path))
    image_gray = resize_to_max(opencv.imread(path, opencv.IMREAD_GRAYSCALE))
    image = opencv.blur(image_gray, (1, 1))
    _, image_threshold = opencv.threshold(image, 128, 255, opencv.THRESH_BINARY)

    result = opencv.findContours(image_threshold, opencv.RETR_LIST, opencv.CHAIN_APPROX_SIMPLE)
    if len(result) == 3:
        _, contours, hierarchy = result
    else:
        contours, hierarchy = result

    found = []
    for contour in get_triangles_from_contours(contours):
        angles = get_triangle_angles(contour)

        area = opencv.contourArea(contour)
        if len(filter(lambda a: 95 >= a >= 45, angles)) == 3 and area > 80:
            found.append(contour)
            opencv.drawContours(image_original_color, [contour], 0, (0, 255, 0), -1)

    if len(found) > 0:
        opencv.imwrite(path_cache_confirmed, image_original_color)

    return checksum

if __name__ == '__main__':
    detect_illuminati(argv[1], False)
