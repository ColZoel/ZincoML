"""
Functions for image processing
"""


import cv2
from PIL import Image


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


def restrict(x, y, w, h, image):
    """
    :param x: x coordinate of top left corner of box
    :param y: y coordinate of top left corner of box
    :param w: width of box
    :param h: height of box
    :param image: image to process
    :return: image cropped to box
    """
    return image[y:y + h, x:x + w]


def box(image_path, x, y, w, h):
    image = restrict(x, y, w, h, read(image_path))
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

