"""
This module controls and sets the file hierarchy for the Zinco pipeline. In general, the files should be organized as
 follows:

|-- Directory Group (Alphabetical or Business section, e.g. "AZ" for Alphabetical)
|   |-- year_city_type (e.g. "2000_ROC_SUB_E_AZ")
|   |   |-- year_city_type.jpg (e.g. "2000_ROC_SUB_E_AZ.jpg")

This module creates an output folder within the directory group folder with extension "_out" for each subdirectory such
such that the structure is as follows:

|-- Directory Group (Alphabetical or Business section, e.g. "AZ" for Alphabetical)
|   |-- year_city_type (e.g. "2000_ROC_SUB_E_AZ")
|   |   |-- year_city_type.jpg (e.g. "2000_ROC_SUB_E_AZ.jpg")
|   |-- year_city_type_out (e.g. "2000_ROC_SUB_E_AZ_out")
|   |   |-- annotations
|   |   |   |-- year_city_type_annotated.json (e.g. "2000_ROC_SUB_E_AZ_annotated.json")
|   |   |   |-- year_city_type_annotated.jpeg (e.g. "2000_ROC_SUB_E_AZ_annotated.jpeg")
|   |   |-- ocr
|   |   |   |-- year_city_type_ocr.parquet (e.g. "2000_ROC_SUB_E_AZ_ocr.parquet")
|   |   |-- processed
|   |   |   |-- year_city_type_processed.csv (e.g. "2000_ROC_SUB_E_AZ_processed.csv")
"""

import os
import glob

import pandas as pd
import yaml
import re
from pandas import read_excel, read_csv, read_stata, read_parquet, read_json, read_feather, read_pickle
numbers = re.compile(r'(\d+)')


def numerical_sort(value):
    """
    Sorts a list of strings by numerical value (key for sort function in loops over directories)
    """
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def input_dir(path):
    config_pth = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yaml')
    if not os.path.isfile(config_pth):
        raise ValueError(f'missing config yaml at {config_pth}.')
    if not os.path.isdir(path):
        raise ValueError(f'{path} is not a directory.')
    if path is None:
        config = yaml.load(open(config_pth, 'r'), Loader=yaml.FullLoader)
        path = config['input_images']
        if not os.path.exists(path):
            raise ValueError(f'{path} does not exist. Check path in config.yaml.')
        if not os.path.isdir(path):
            raise ValueError(f'{path} is not a directory.')
    return path


def set_directories(in_file=None):
    """
    Create base paths for common folders given an input in the input folder.

    To access: set_directories()['param'] where param is one of:
            'base', 'city_type', 'year_city_type'

    :param in_file: input file path for item in directory/AZ/year_city_type
    :return: dict() of directories.
    """
    options = in_file.split("/")
    if ".jp" in options[-1]:  # if filename is present
        input_dir = options[:-1]  # don't include filename
    else:
        input_dir = options  # everything but file name (city_type folder)
    input_dir = "/".join(input_dir)

    dirs = {}  # creates a dictionary of the directories
    for i, loc in enumerate(['city', 'base']):

        dirs['%s' % loc] = input_dir.split("/")[:-i-1]
        dirs['%s' % loc] = "/".join(dirs['%s' % loc])

    dirs['input'] = input_dir

    return dirs


def subdirectories(year_city_type_path):
    """
    Creates subdirectories for the year_city_type folder

        [0] save_dir: path to 'year_city_type_out'\n
        [1] debug_dir: path to 'year_city_type_out/debug'\n
        [2] temp_dir: path to 'year_city_type_out/debug/temp'\n
        [3] annotate_dir: path to 'year_city_type_out/debug/temp/1'\n
        [4] ocr_dir: path to 'year_city_type_out/debug/temp/2'\n
        [5] parse_dir: path to 'year_city_type_out/debug/temp/3'\n

    :param year_city_type_path: path to the year_city_type folder
    :return: tuple of subdirectories

    """
    if year_city_type_path[-1] == "/":
        year_city_type_path = year_city_type_path[:-1]
    save_dir = year_city_type_path.split(".")[0] + "_out"
    debug_dir = os.path.join(save_dir, 'debug')
    temp_dir = os.path.join(debug_dir, 'temp')
    annotate_dir = os.path.join(debug_dir, '1')
    ocr_dir = os.path.join(temp_dir, '2')
    parse_dir = os.path.join(temp_dir, '3')

    dirs = (save_dir, debug_dir, temp_dir, annotate_dir, ocr_dir, parse_dir)

    return dirs


def file_stem(path):
    return os.path.basename(path).split('.')[0]


def parse_parts(path):
    filename = os.path.basename(path)
    dirname = os.path.dirname(path)
    return filename, dirname


def save_paths(year_city_type_path):
    debug_dir = subdirectories(year_city_type_path)[1]
    save_dir = subdirectories(year_city_type_path)[0]
    file = file_stem(year_city_type_path)

    feather_save_path = (os.path.join(debug_dir, f'{file}.feather'))  # debug incase csv fails
    csv_save_path = os.path.join(save_dir, f'{file}.csv')
    dta_save_path = os.path.join(save_dir, f'{file}.dta')

    return feather_save_path, csv_save_path, dta_save_path


def read_any(path):
    """
    Reads any file type and returns a dataframe
    """
    if path.endswith('.csv'):
        return read_csv(path)
    elif path.endswith('.feather'):
        return read_feather(path)
    elif path.endswith('.dta'):
        return read_stata(path)
    elif path.endswith('.parquet'):
        return read_parquet(path)
    elif path.endswith('.json'):
        return read_json(path)
    elif path.endswith('.xlsx'):
        return read_excel(path)
    elif path.endswith('.xls'):
        return read_excel(path)
    elif path.endswith('.pkl'):
        return read_pickle(path)
    elif isinstance(path, pd.DataFrame):
        pass
    else:
        raise ValueError(f'Invalid file type: {path}')


def recent_model(dir_):
    """
    Returns the most recent model in a directory
    """
    files = glob.glob(os.path.join(dir_, '*.onnx'))
    files.sort(key=os.path.getmtime)
    return files[-1]


