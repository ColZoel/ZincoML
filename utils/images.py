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


def box(annotation_box):
    image_path, x, y, w, h = annotation_box
    image = restrict(x, y, w, h, read(image_path))
    return image
