"""
This module contains functions to raondomly select images to be annotated for CV training.
"""

import os
import random
import shutil
import sys
from glob import glob
import time
from Zs.Z_modules import short_step


def check_for_jpeg(path):
    """
    check if there is a duplicate folder of jpeg images
    """
    jpeg_folder = glob(path + "_jpeg")
    if len(jpeg_folder) > 0:
        return jpeg_folder[0]
    else:
        return path


def image_paths(path, image_list=None):
    """
    list all images in a folder
    """
    if image_list is None:
        image_list = []
    image_list.extend(glob(path + "/*.jpg"))
    image_list.extend(glob(path + "/*.jpeg"))
    image_list.extend(glob(path + "/*.tiff"))
    image_list.extend(glob(path + "/*.tif"))

    return image_list


def list_all_images(path):
    """
    un-nest images from folders and list them all in one folder
    """
    im_paths = []

    year_city_types = glob(path + "/*")
    year_city_types = [check_for_jpeg(y) for y in year_city_types]
    year_city_types = [y for y in year_city_types if "_out" not in y]
    year_city_types = [y for y in year_city_types if "_tiff" not in y]
    year_city_types = [y for y in year_city_types if y.split("/")[-1][0].isnumeric()]
    year_city_types = sorted(set(year_city_types))  # remove duplicates
    for year_city_type_path in year_city_types:
        if os.path.isdir(year_city_type_path):
            im_paths = image_paths(year_city_type_path, im_paths)

    return im_paths, year_city_types


def sample_size_from_population(image_paths, sample_size=None, percentage=None):
    """
    creates sample size for population
    """

    population_size = len(image_paths)

    if sample_size is None and percentage is None:
        raise ValueError("Either sample_size or percentage must be specified.")
    if sample_size is not None and percentage is not None:
        raise ValueError("Only one of sample_size or percentage can be specified.")
    if percentage is not None and (percentage < 0 or percentage > 1):
        raise ValueError("percentage must be between 0 and 1.")
    if sample_size is not None and sample_size > population_size:
        raise ValueError(f'sample_size {sample_size} is larger than population_size {population_size}.')

    if percentage is not None:
        sample_size = int(population_size * percentage)
    elif sample_size is not None:
        pass

    return sample_size


def sample_size_each_folder(year_city_types, population_sample_size, excluded=None):
    """
    creates sample size for each folder
    """
    if excluded is not None:
        for year_city_type in excluded:
            if year_city_type in year_city_types:
                year_city_types.remove(year_city_type)

    num_dirs = len(year_city_types)

    sample_size_each_folder = population_sample_size // num_dirs

    return sample_size_each_folder


def verify_sample_size_each_folder(year_city_types, sample_size_each_folder):
    """
    verifies that each folder has enough images to sample from
    """
    images = []
    for year_city_type in year_city_types:
        images = image_paths(year_city_type, images)

        if len(images) < sample_size_each_folder:
            print(f'Not enough images in {year_city_type} to sample {sample_size_each_folder} images.')
            return False

    return True


def sample_folder(folder, n):
    """
    randomly sample from a folder
    """
    image_list = set(image_paths(folder))
    return random.sample(sorted(image_list), n)


def copy_sample(sample, destination):
    """
    copy sample to destination
    """
    os.makedirs(destination, exist_ok=True)
    start = time.perf_counter()
    for i, image in enumerate(sample):
        short_step(start, f'Copying {i+1} of {len(sample)}', i, len(sample))
        shutil.copy(image, destination)


def sample_images(path, sample_size=None, percentage=None, excluded=None, sample_all=False):
    """
    randomly sample nested images from each folder in root path
    """
    image_paths, year_city_types = list_all_images(path)
    population_sample_size = sample_size_from_population(image_paths, sample_size, percentage)
    if sample_all:
        return random.sample(image_paths, population_sample_size)

    n_samples = sample_size_each_folder(year_city_types, population_sample_size, excluded)

    if not verify_sample_size_each_folder(year_city_types, n_samples):
        sys.exit()

    sample = []
    for year_city_type in year_city_types:
        sample.extend(sample_folder(year_city_type, n_samples))

    return sample


def sample_dir(path, sample_size=None, percentage=None, excluded=None, sample_all=False):
    """
    randomly sample nested images from each folder in root path and copy to destination
    """
    destination = path + "/sample"
    os.makedirs(destination, exist_ok=True)
    sample = sample_images(path, sample_size, percentage, excluded, sample_all)
    copy_sample(sample, destination)
    print(f'{len(sample)} images copied to {destination}.')
    return sample


sample = sample_dir('/Volumes/CZ ROC/AZ', percentage=0.02, sample_all=True)

