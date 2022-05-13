#!/usr/bin/env python2

from sys import argv
import cv2 as opencv
import numpy as np
import hashlib
import os
import shutil


def get_triangles_from_contours(contours, ep_buffer=0.03):
    for contour in contours:
        # fluctuate between 0.01 and 0.06
        approx = opencv.approxPolyDP(contour, ep_buffer * opencv.arcLength(contour, True), False)
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


def detect_illuminati(path, blur_seq=None, thresh_seq=None, ep_buffer_seq=None, cache=True):
    if blur_seq is None:
        blur_seq = [6, 5, 4, 3, 2, 1, 0]
    if ep_buffer_seq is None:
        ep_buffer_seq = [1, 2, 3, 4, 5]
    if thresh_seq is None:
        thresh_seq = [128, 160, 192]

    checksum = checksum_md5(path)
    path_cache = 'static/images/cache/{}.jpg'.format(checksum)
    path_cache_confirmed = 'static/images/cache/{}_confirmed.jpg'.format(checksum)

    if cache and (os.path.exists(path_cache_confirmed) or os.path.exists(path_cache)):
        return checksum

    if not os.path.exists(path_cache):
        shutil.copy(path, path_cache)

    image_original_color = resize_to_max(opencv.imread(path))
    image_gray = resize_to_max(opencv.imread(path, opencv.IMREAD_GRAYSCALE))
    found = []

    for blur in blur_seq:
        image = opencv.blur(image_gray, (blur, blur)) if blur > 0 else image_gray

        for thresh in thresh_seq:
            _, image_threshold = opencv.threshold(image, thresh, 255, opencv.THRESH_BINARY)

            result = opencv.findContours(image_threshold, opencv.RETR_LIST, opencv.CHAIN_APPROX_SIMPLE)
            if len(result) == 3:
                _, contours, hierarchy = result
            else:
                contours, hierarchy = result

            for ep_buffer in ep_buffer_seq:
                for contour in get_triangles_from_contours(contours, ep_buffer * 0.01):
                    angles = get_triangle_angles(contour)

                    area = opencv.contourArea(contour)
                    if len(list(filter(lambda a: 95 >= a >= 40, angles))) == 3 and 40000 >= area >= 10:
                        found.append(contour)

    if len(found) > 0:
        for f in found:
            opencv.drawContours(image_original_color, [f], 0, (0, 255, 0), -1)
        opencv.imwrite(path_cache_confirmed, image_original_color)

    return checksum


def display_image(title, image, wait=True):
    opencv.imshow(title, image)
    if wait:
        opencv.waitKey(0)
        opencv.destroyAllWindows()

if __name__ == '__main__':

    detect_illuminati(argv[1], cache=False)
