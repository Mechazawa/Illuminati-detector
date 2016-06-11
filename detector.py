#!/usr/bin/env python2
import cv2 as opencv
import numpy as np
from sys import argv


def getTrianglesFromContours(contours):
    for contour in contours:
        approx = opencv.approxPolyDP(contour, 0.03 * opencv.arcLength(contour, True), True)
        if len(approx) == 3:
            yield approx


def getTriangleAngles(contour):
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


def main(path):
    image_original_color = opencv.imread(path)
    image_gray = opencv.imread(path, opencv.IMREAD_GRAYSCALE)
    image = opencv.blur(image_gray, (3,3))
    _, image_threshold = opencv.threshold(image, 128, 255, opencv.THRESH_BINARY)
    _, contours, hierarchy = opencv.findContours(image_threshold, opencv.RETR_LIST, opencv.CHAIN_APPROX_SIMPLE)

    found = []
    for contour in getTrianglesFromContours(contours):
        angles = getTriangleAngles(contour)

        if len(filter(lambda a: 80 > a > 45, angles)) == 3:
            found.append(contour)
            opencv.drawContours(image_original_color, [contour], 0, (0, 255, 0), -1)

if __name__ == '__main__':
    main(argv[1])


