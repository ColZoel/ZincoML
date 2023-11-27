"""
Converts filetypes. Images to .png, .jpg, .jpeg, .gif, .bmp, .ico, .tiff, .webp, .svg and .pdf. Data types to .json,
.txt, .csv, .xls, .xlsx, .xml, .yaml, .html, .md, .rst, .ipynb, .py, .pyc, .pickle, .h5, .npy, .npz, .mat, .pkl,
.pth, .pt, .pb, .pbtxt, .bin, .caffemodel, .prototxt, .cfg, .weights, .names, .data,
"""
import os
import time

import cv2
import glob
from PIL import Image
from Zs.Z_modules import short_step
import gc
from multiprocessing import Pool


def image(src, type, start, dirsize, i, dirname, out_folder=None, backend='cv2'):
    """
    Converts image to .png, .jpg, .jpeg, .gif, .bmp, .ico, .tiff, .webp and .svg
    """
    if i % 25 == 0:
        gc.collect()
    filename = src.split('/')[-1]
    short_step(start, f'{dirname}:  {i+1} of {dirsize}', i+1, dirsize)
    filename = filename.replace(filename.split('.')[-1], type)

    if out_folder is not None:
        filename = os.path.join(out_folder, filename)
    else:
        filename = os.path.join(src.split('/')[:-1], filename)

    if os.path.isfile(filename):
        return  # skip if file already exists

    if backend == 'cv2':
        try:
            img = cv2.imread(src)
        except:
            print(f'Could not read {src}.')
            return

        cv2.imwrite(filename, img)

    elif backend == 'PIL':
        try:
            img = Image.open(src)
        except:
            print(f'Could not read {src}.')
            return
        img.save(filename)

    return


def directory(path, type, backend='cv2'):
    """
    Converts all images in a directory to .png, .jpg, .jpeg, .gif, .bmp, .ico, .tiff, .webp and .svg
    """
    start = time.perf_counter()
    dirname = path.split('/')[-1]
    # print(f'{dirname}\n')
    if not os.path.isdir(path):
        raise ValueError(f'{path} is not a directory.')
    out_folder = path + f'_{type}'
    os.makedirs(out_folder, exist_ok=True)

    dir_list = glob.glob(path + '/*')
    dirsize = len(dir_list)

    for i, src in enumerate(dir_list):
        image(src, type, start, dirsize, i, dirname, out_folder=out_folder, backend=backend)

    print(f'Finished {dirsize} files')
    return


def multi_dirs_async(dirlist, type, backend='cv2', cores=4):
    """
    Converts all images in a directory to .png, .jpg, .jpeg, .gif, .bmp, .ico, .tiff, .webp and .svg
    """

    for d in dirlist:
        if not os.path.isdir(d):
            raise ValueError(f'{d} is not a directory.')

    with Pool(cores) as p:
        p.starmap(directory, [(path, type, backend) for path in dirlist])

    print(f'Finished {len(dirlist)} directories')
    return


dirlist = [
    '/Volumes/CZ ROC/AZ/2004_ROC_SUB_E_AZ',
    '/Volumes/CZ ROC/AZ/2006_ROC',
    '/Volumes/CZ ROC/AZ/2007_ROC',
    '/Volumes/CZ ROC/AZ/2008_ROC',
]

if __name__ == '__main__':
    multi_dirs_async(dirlist, 'jpeg', backend='cv2', cores=4)


with open()