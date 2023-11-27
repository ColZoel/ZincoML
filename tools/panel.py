"""
This module aggregates individual raw OCR files into a single file for each year-city-type combination.
The output is therefore a panel of year, raw OCR, and debug information.
This output can later be passed through the parser (vectorized) to create a panel of year, city, and parsed information.

Collin Zoeller
"""

import os
import pandas as pd
from glob import glob
from multiprocessing import Pool
import warnings
import time
from Zs.Alpha.parallel.module import core_default
from Zs.Z_modules import short_step, progress_bar, save


def aggregate_ocr_task(start, size, filename):

    current = f'{size}'
    progress_bar(start, filename, size, current, size, "aggregating")
    df = pd.read_parquet(filename)

    return df


def build_task(file):
    filename = file.split('/')[-1]
    year = filename.split('_')[0]
    city = filename.split('_')[1]
    df = pd.read_feather(file)
    df['year'] = year
    df['city'] = city
    df['parent_file'] = filename

    return df


def build_sync(parent_dir, save_dir, dir_list=None, out_to='csv', cores=6):

    start = time.perf_counter()

    if cores > os.cpu_count():
        cores = os.cpu_count()
        warnings.warn(f"cores set to {cores} because you have {os.cpu_count()} cores."
                      f" Performance may be severely impacted.")

    # default is to search the entire directory for all files ending in _ocr.csv
    dir_list = glob(os.path.join(parent_dir, '*_out')) if dir_list is None else dir_list

    # aggregate all image OCRs before aggregating the whole panel. This helps keep order
    image_OCRs = [glob(os.path.join(folder, 'debug', 'temp', '1', '*_ocr.parquet')) for folder in dir_list]
    image_OCRs = [c for c in image_OCRs if c != []]
    df = []

    with Pool(cores) as p:
        for year_dir in image_OCRs:
            size = len(year_dir)
            dfs = p.starmap(aggregate_ocr_task, [(start, size, filename) for filename in year_dir])
            df.append(pd.concat(dfs, ignore_index=True))
        p.close()
        p.join()

    df = pd.concat(df, ignore_index=True)
    df.to_feather(os.path.join(save_dir, 'panel.feather'))
    progress_bar(start, 'panel.feather', 1, 1, 3, "creating panel file")
    if out_to == 'csv':
        df.to_csv(os.path.join(save_dir, 'panel.csv'))
        progress_bar(start, 'panel.csv', 1, 2, 3, "creating panel file")
    elif out_to == 'stata':
        df.to_stata(os.path.join(save_dir, 'panel.dta'))
        progress_bar(start, 'panel.dta', 2, 2, 3, "creating panel file")
    else:
        raise ValueError("out_to must be either 'csv' or 'stata'. Feather was still saved.")
    progress_bar(start, 'done.', 1, 3, 3, "")
    return df


def build(parent_dir, save_dir, dir_list=None, out_to='csv', cores=6):
    build_sync(parent_dir, save_dir, dir_list=dir_list, out_to=out_to, cores=cores)
    return None

df = pd.read_feather('/Volumes/CZ ROC/panel.feather')
print(df.head())