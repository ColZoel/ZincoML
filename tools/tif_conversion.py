"""
This module is a subsidiary of Zinco tools that converts all directory images in a folder to tiff
after cropping rotating, reducing resolution and changing color. A new directory in the workspace is created to house
these data.

Author: Collin Zoeller, Brigham Young University: zoellercollin@gmail.com
Prepared exclusively for the doctoral project of Jonathan Palmer, Harvard Business School.

"""
from Zs.Z_modules import *
from Zs.Alpha.recognize import *
import os
import pandas as pd
import numpy as np
from datetime import datetime
import gc
from stopwatch import Stopwatch



def rename(excel_path):

    df = pd.read_excel(excel_path)
    city = ''
    year = ''
    new_name_list = []
    for i, filename in enumerate(df['FILENAME']):

        parts = filename.split('_')

        # year
        if parts[0][0].isnumeric():
            year = parts[0]
            city = parts[1]
        order_id = df.loc[i, 'ORDER']
        if 'SUB' in filename or 'sub' in filename:
            new = f'{year}_{city}_SUB_{order_id}.tif'
        else:
            new = f'{year}_{city}_{order_id}.tif'

        new_name_list.append(new)
    new_name_list = np.array(new_name_list)
    df.insert(3, 'STANDARD NAME', new_name_list)
    df.rename({'FILENAME': 'ORIGINAL FILENAME'}, axis=1, inplace=True)
    df = df[['STANDARD NAME', 'ORIGINAL FILENAME', 'ORDER', 'PAGE NUMBER', 'TYPE']]

    return df, city, year


def file_to_tiff(filepath, save_name, dpi=300, color='grey', conf_thresh=50, debug=False):
    """
    Converts images to binary in tiff format at a specified dpi. Images are saved in a new folder
    in the same directory that contains the superficial folder.
    :param filepath: dir() path to a file in the directory
    :param save_name: str() name of the output tiff image
    :param dpi: int() (square) resolution at which to save the image
    :param color: one of ['grey', 'bw', 'color'], output color map
    :param conf_thresh: int() upperbound on OCR confidence to rotate an image in reorientation step
    :param average_ratio: float() average dimension ratio for each image in dataset, updated ech iteration
    :param size_thresh: int() lowerbound on image size to remove whitespace (prevents data loss for older images)
    :param progress_bar: whether to print process information
    :param debug: whether to display debugging window
    :return: None
    """

    if color not in ['grey', 'bw', 'color']:
        raise KeyError("Only select from 'grey', 'bw', and 'color'")

    # create base save directory
    filename = filepath.split("/")[-1]
    year_city_type = filepath.split("/")[-2]
    city_type = filepath.split("/")[-3]
    city_type_tiff = city_type + '_tiffs'
    city_type_tiff_color = city_type_tiff + '_' + color
    base_save_dir = filepath.split('/')[:-3]
    save_dir = "/".join(base_save_dir)
    docs_save_dir = os.path.join(save_dir, city_type_tiff, year_city_type)
    save_dir = os.path.join(save_dir, city_type_tiff, year_city_type, city_type_tiff_color)

    os.makedirs(save_dir, exist_ok=True)

    image = cv2.imread(filepath)

    # 1. reduce image to text field (remove whitespace)
    image = detect_page(image, debug=debug)
    display(image, debug=debug)

    # 2. rotate cropped image (if needed)
    image = orient_detect(image, conf_thresh, debug)
    display(image, debug=debug)

    # 3. adjust skews
    # image = straighten_image(image, (10, 10))  # fix skew
    # display(image, debug=debug)

    if color != 'color':  # color images save and return at this step, else the follow transformations
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        display(image, debug=debug)

        if color == 'bw':
            (thresh, image) = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
            display(image, debug=debug)

    # convert to PIL Image so dpi can be specified
    save_path = os.path.join(save_dir, save_name)
    image = Image.fromarray(image)
    image.save(save_path, dpi=(dpi, dpi))

    del image  # removes saved image from memory for better processing at scale
    gc.collect()

    return docs_save_dir, save_dir


def to_tif(folder_path, excel_path, dpi=300, color='grey', redo=False, conf_thresh=50, size_thresh=4000, debug=False):
    """

    :param folder_path: pth() path of folder to process
    :param excel_path: pth() path of instruction excel listng filenames in reading order
    :param dpi: int() (square) resolution at which to save the image
    :param color: one of ['grey', 'bw', 'color'], output color map
    :param redo: bool() default=False. if True rerun the entire folder, elso process images not yet in save directory
    :param conf_thresh: int() upperbound on OCR confidence to rotate an image in reorientation step
    :param size_thresh: int() int() threshold below which whitespace is not removed
    :param debug: bool() whether to display debugging functions such as the images as they are being processed
    :return:
    """

    folder_name = folder_path.split('/')[-1]
    print(f'Converting {folder_name} to tif.')
    new_excel, city, year = rename(excel_path)

    json_name = f'{year}_{city}_meta.json'
    csv_name = f'{year}_{city}_meta.csv'

    # manifest text
    txt = (f'MANIFEST FOR THIS DIRECTORY\n\n'
           f'DATA SPECIFICATIONS:\n\n'
           f'year:  {year}\n'
           f'city:  {city}\n'
           f'dpi:   {dpi}\n'
           f'color: {color}\n\n'
           f'date processed: {datetime.now()}\n\n'
           f'INCLUDED FILES:\n'
           f'manifest.txt: this file. Explains the directory\n'
           f'{json_name}: metadata in json format\n'
           f'{csv_name}: metadata in csv format\n'
           f'{year}_{city}_tiffs: folder of converted tif files.\n'
           f'The last attribute of this folder indicates the color of the image.\n\n'
           
           f'Possible colors are:\n'
           f'grey: greyscale\n'
           f'bw: black and white (binary)\n'
           f'color: original color mapping\n\n'
        
           f'Metadata include the following:\n'
           f'STANDARDIZED NAME: reformatted name following year_city_order format\n'
           f'ORIGINAL NAME: name of file prior to reformatting\n'
           f'ORDER: corrected order of each page (from input excel)\n'
           f'PAGE NUMBER: page number as indicated on page, extracted from Zinco Page Finder and verified manually\n'
           f'TYPE: Indicates from what section of the directory the page was pulled\n\n'
           f'––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––-\n'
           f'ATTRIBUTIONS:\n'
           f'Prepared for FamilySearch in agreement with Jonathan Palmer, Harvard Business School: jpalmer@hbs.edu\n'
           f'Prepared by Collin Zoeller, Brigham Young University: zoellercollin@gmail.com\n\n'
           f'Note that the associated Zinco Page Finder and other Zinco program tools are proprietary and are used or\n'
           f'shared at the sole discretion of the authors.')

    size = len(new_excel)
    save_path = folder_path
    stopwatch = Stopwatch(2)

    ratio_list = []
    x_dims = []
    y_dims = []
    for i, filename in enumerate(new_excel['ORIGINAL FILENAME']):

        # ##################### progress bar ###########################
        seconds = stopwatch.duration
        mins = np.round_((seconds // 60), 0)
        seconds = seconds % 60
        hours = mins // 60
        mins = mins % 60
        timer = f'{int(hours)}:{int(mins)}:{int(seconds)}'

        current = f'{i+1} of {size}'
        sys.stdout.write('\r')
        sys.stdout.write("%s | %s | elapsed: %s | %d%%  %-15s" % (filename, current, timer,
                                                 ((i+1)/size)*100, '#' * 1 * int((i/size)*15)))
        sys.stdout.flush()
        # #################################################################

        if not redo:
            if i > 1 and new_excel.loc[i, 'STANDARD NAME'] in os.listdir(save_path):
                continue

        # update average ratio list prior to processing next image
        if len(ratio_list) > 0:
            avg_ratio = np.average(ratio_list)

        else:
            avg_ratio = 1.35

        if len(x_dims) > 0:
            av_x = int(np.average(x_dims))
        else:
            av_x = None
        if len(y_dims) > 0:
            av_y = int(np.average(y_dims))
        else:
            av_y = None
        # -------------------------------- process next image ----------------------------------------
        docs_path, save_path = file_to_tiff(os.path.join(folder_path, filename),
                                                new_excel.loc[i, 'STANDARD NAME'], dpi=dpi, color=color,
                                                conf_thresh=conf_thresh,  debug=debug)

        # save associated documents on first image
        if i == 1:
            json_path = os.path.join(docs_path, json_name)
            csv_path = os.path.join(docs_path, csv_name)
            manifest_path = os.path.join(docs_path, 'manifest.txt')
            new_excel.to_json(json_path, orient='records')
            new_excel.to_csv(csv_path)
            with open(manifest_path, 'w') as f:
                f.write(txt)

        elif i // 100:  # clean memory after a processing a chunk of the dataset
            gc.collect()
    else:
        print('\n\nFinished.')
    return


# excel_path = '/Users/collinzoeller/city_directories/1990_ROC_SUB.xlsx'
# folder_path = '/Users/collinzoeller/city_directories/ROC_BIZ/1990_ROC_SUB'
# to_tif(folder_path, excel_path, redo=True, debug=True)
#
#
