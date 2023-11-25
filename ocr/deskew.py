"""
This module deskews the pages prior to passing through OCR.
"""

from Zs.Z_modules import display
import cv2
import numpy as np


def skew_angle(image, debug=False):

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    if debug:
        display(thresh, debug=False)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilate = cv2.boxFilter(thresh, 0, (50, 80), kernel, (-1, -1), False, cv2.BORDER_DEFAULT)

    if debug:
        display(dilate, debug=True)

    if debug:
        # Find all contours
        contours = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        temp1 = cv2.drawContours(image.copy(), contours, -1, (255, 0, 0), 2)

        display(temp1, debug=debug)

        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        rect = cv2.minAreaRect(cnts[0])
        box = np.intp(cv2.boxPoints(rect))
        temp1 = cv2.drawContours(temp1, [box], -1, (36, 255, 12), 3)

        display(temp1, debug=debug)

    coords = np.column_stack(np.where(dilate > 0))
    angle = cv2.minAreaRect(coords)[-1]

    if angle < -45:
        angle = 90 + angle
        return -1.0 * angle
    elif angle > 45:
        angle = 90 - angle
        return angle
    return -1.0 * angle


def deskew(image, debug=False):
    angle = skew_angle(image, debug=debug)
    (h, w) = image.shape[:2]  # find height and width of image
    center = (w // 2, h // 2)  # finding center coordinates of image
    m = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    if debug:
        display(rotated, debug=debug)
    return rotated
