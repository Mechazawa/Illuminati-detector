#!/usr/bin/env python2

from sys import argv
import cv2 as opencv
import numpy as np
import hashlib
import os


def get_triangles_from_contours(contours):
    for contour in contours:
        approx = opencv.approxPolyDP(contour, 0.03 * opencv.arcLength(contour, True), True)
        if len(approx) == 3:
            yield approx


def get_triangle_angles(contour):
    points = np.array([c[0] for c in contour])

    A = points[1] - points[0]
    B = points[2] - points[1]
    C = points[0] - points[2]

    angles = []
    for e1, e2 in ((A, -B), (B, -C), (C, -A)):
        num = np.dot(e1, e2)
        denom = np.linalg.norm(e1) * np.linalg.norm(e2)
        angles.append(np.arccos(num/denom) * 180 / np.pi)
    return angles


def checksum_md5(filename):
    md5 = hashlib.md5()
    with open(filename,'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            md5.update(chunk)
    return md5.hexdigest()


def detect_illuminati(path):
    path_cache = 'cache/{}_confirmed.jpg'.format(checksum_md5(path))

    if os.path.exists(path_cache):
        return True

    if os.path.exists(path):
        return False

    image_original_color = opencv.imread(path)
    image_gray = opencv.imread(path, opencv.IMREAD_GRAYSCALE)
    image = opencv.blur(image_gray, (3, 3))
    _, image_threshold = opencv.threshold(image, 128, 255, opencv.THRESH_BINARY)
    _, contours, hierarchy = opencv.findContours(image_threshold, opencv.RETR_LIST, opencv.CHAIN_APPROX_SIMPLE)

    found = []
    for contour in get_triangles_from_contours(contours):
        angles = get_triangle_angles(contour)

        if len(filter(lambda a: 95 >= a >= 45, angles)) == 3:
            found.append(contour)
            opencv.drawContours(image_original_color, [contour], 0, (0, 255, 0), -1)

    if len(found) > 0:
        opencv.imwrite(path_cache, image_original_color)

    return len(found) > 0


def main(path):
    detect_illuminati(path)

if __name__ == '__main__':
    main(argv[1])


