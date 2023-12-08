"""
Functions for image processing
"""


import cv2
from PIL import Image
import numpy as np
from tesserocr import PyTessBaseAPI


# Colors
red = (100, 50, 200)
darkblue = (255, 100, 0)
green = (0, 255, 0)
blue = (255, 0, 0)
yellow = (0, 255, 255)
white = (255, 255, 255)


def display(image, debug=False, wait=0, window_size=(600, 1000)):
    """
    :param wait: time in ms before moving to next step in debug. 0= infinite. default = 0
    :param image: image to process
    :param debug: bool = True if in debug mode
    :param window_size: width, height (integer type)
    :return: only displays image if debug=True
    """
    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', window_size)
    if debug:
        cv2.imshow("image", image)
        cv2.waitKey(wait)
    return


def read(path, engine='cv2'):
    if engine == 'cv2':
        return cv2.imread(path)
    elif engine == 'PIL':
        return Image.open(path)
    else:
        raise ValueError(f'Invalid engine: {engine}')


def restrict(x, y, x2, y2, image):
    """
    :param x: x coordinate of top left corner of box
    :param y: y coordinate of top left corner of box
    :param w: width of box
    :param h: height of box
    :param image: image to process
    :return: image cropped to box
    """
    y = np.floor(y).astype(int)
    x = np.floor(x).astype(int)
    y2 = np.ceil(y2).astype(int)
    x2 = np.ceil(x2).astype(int)
    image = image[y:y2, x:x2]
    # display(image, debug=True)
    return image


def orient_detect(api, cv2_image, conf_thresh=50, debug=False):
    """
    Check if image is upside down by running middle third of image thorugh
    the OCR and measuring the confidence. Rotates if confidence is low (indicating
    gibberish).
    :param cv2_image: full CV2 image after processing
    :param conf_thresh: int() percentage for confidence threshold under which the image is rotated
    :param debug: whether to display text and debug windows
    :return: cv2 image
    """
    # check orientation
    h, w = cv2_image.shape[:2]
    orientation_check_image = cv2_image[h // 3:2*h//3, 2*h//5:4*h//5]  # only look at middle third of image
    try:
        orientation_pil = Image.fromarray(orientation_check_image)
        api.SetImage(orientation_pil)
        api.Recognize()
    except:
        pass
        return cv2_image
    # if image in sideways, rotate 90-degrees
    if w > h:
        cv2_image = cv2.rotate(cv2_image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # rotate if bad text
    if api.MeanTextConf() < conf_thresh:
        cv2_image = cv2.rotate(cv2_image, cv2.ROTATE_180)

    if debug:
        print('\nText conf:', api.MeanTextConf())
        display(cv2_image, debug)

    api.Clear()
    return cv2_image


def pad(image, thickness=150):
    """
    Crop image to contour and pad with white space.
    :param image: CV2 image
    :param thickness: padding to add to contour
    :return: cropped and padded image
    """
    image = cv2.copyMakeBorder(image, thickness, thickness, thickness, thickness, cv2.BORDER_CONSTANT, value=white)

    return image


def hsv_to_rgb(h, s, v):
    if s == 0.0: v *= 255; return (v, v, v)
    i = int(h * 6.)  # XXX assume int() truncates!
    f = (h * 6.) - i;
    p, q, t = int(255 * (v * (1. - s))), int(255 * (v * (1. - s * f))), int(255 * (v * (1. - s * (1. - f))));
    v *= 255;
    i %= 6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)


def insertion_sort(arr):
    for idx in range(1, len(arr)):
        scan = idx
        while scan > 0 and arr[scan] < arr[scan-1]:
            # print(f"Switched {arr[scan]} and {arr[scan-1]}")
            arr[scan - 1], arr[scan] = arr[scan], arr[scan - 1]
            scan -= 1
    return arr


def box(api, image_path, x, y, w, h):
    image = restrict(x, y, w, h, read(image_path))
    image = orient_detect(api, image)
    image = pad(image)
    image = Image.fromarray(image)
    return image

