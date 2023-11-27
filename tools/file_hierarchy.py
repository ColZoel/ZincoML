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
from zinco import path
import yaml


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

