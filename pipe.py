"""
Zinco pipeline main file. All the pieces come together here.
"""

from image_segmentation.predict import *
from ocr.ocr import map_ocr, save_aggregate
from parsing.parser import parse_image
from utils.config import load_config


# Vertical (vectorized) pipeline
def vertical(path=None, output='csv', debug=False, cores=6):
    """
    Zinco pipeline vectorized function
    :param path: path to input images to process
    :param output: output type, one of 'csv', 'parquet', or 'dta', or None. Always saves a feather. Default is 'csv'
    :param debug: whether to run in debug mode (runs a debug model)
    :param cores: number of cores to use for parallel processing
    :return: None
    """
    if path is None:
        path = load_config('main')['input_images']

    # Step 1: Image segmentation
    results_df = predict_text_fields(path)

    # Step 2: Text extraction
    dfs = map_ocr(results_df, cores=cores)
    aggregate = save_aggregate(dfs, path)

    # Step 3: Data parsing with LLM
    parse_image(aggregate, path, output=output)

    return
