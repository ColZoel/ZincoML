"""
This module contains the functions for extracting text from an image using Tesseract OCR via Tessercocr.
"""

import gc
import pandas as pd
import glob
from Zs.Alpha.globals import *
from Zs.Z_modules import *
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PT, PSM
from Line import Line
from Column import Column
# from Zs.Alpha.preprocessor import preprocess  # Fixme: remove preprocessing from ocr since it's not needed anymore

special_chars_regex = re.compile(r'[\-.*]')


def organize_lines(api: PyTessBaseAPI, image: Image, debug=False) -> list[dict]:
    """
        APPLY OCR TO IMAGE AND ORGANIZES OUTPUT INTO RECORDS AND COLUMNS

        :param api: Tesserocr API object
        :param image: PIL image object
        :param debug: if True, shows intermediate debugging images

        :return: list of Records of shape {
            "raw_string": str,
            "left": int,
            "top": int,
            "right": int,
            "bottom": int,
            "line_nums": [int],
            "review_flag": bool
        }
    """
    ocr_start = time.perf_counter()

    file_loc = os.path.dirname(os.path.realpath(__file__))  # Gets location of this script
    api.SetVariable("tessedit_char_whitelist",
                    open(os.path.join(file_loc, "whitelist.txt")).read().strip())  # sets allowed chars

    image = Image.fromarray(image)
    api.SetImage(image)
    api.Recognize()  # bulk of time, actual OCR

    ocr_stop = time.perf_counter()
    ocr_time = ocr_stop - ocr_start

    combining_start = time.perf_counter()

    ri = api.GetIterator()
    columns = []
    column_index = -1  # current column index, initialized to -1 to avoid first block being skipped
    column_x = -1000  # current column's x-coord, initialized to -1000 to avoid first block being skipped

    for i, b in enumerate(iterate_level(ri, RIL.BLOCK)):
        block_type = ri.BlockType()
        if block_type == PT.FLOWING_IMAGE or \
                block_type == PT.HEADING_IMAGE or \
                block_type == PT.PULLOUT_IMAGE or \
                block_type == PT.UNKNOWN:
            continue  # Skip image blocks
        if debug:
            b.GetImage(RIL.BLOCK, 2, image)[0].show()

        block_box = b.BoundingBoxInternal(RIL.BLOCK)

        if abs(block_box[0] - column_x) > 200:  # Make new Column if block is more than 200 units away
            column_index += 1
        column_x = block_box[0]  # Update column position for each block to account for drift

        #  Text Line level
        line_level = RIL.TEXTLINE

        for r in iterate_level(ri, line_level):
            line = r.GetUTF8Text(line_level)  # return text encoding
            #  Check if block is a line, if so, increment column index
            if block_type == PT.HORZ_LINE or block_type == PT.VERT_LINE:
                column_index += 1
                if ri.IsAtFinalElement(RIL.BLOCK, RIL.TEXTLINE):
                    break
                continue

            #  Check if block is a header, if so, skip
            header = re.search(header_re, line)
            if header is not None:
                if ri.IsAtFinalElement(RIL.BLOCK, RIL.TEXTLINE):
                    break
                continue

            #  Check if block is a page number, if so, skip
            is_pg_num = re.search(pagenum, line)
            box = r.BoundingBoxInternal(line_level)
            if (is_pg_num is not None) and (box[1] < 500):  # I just chose 500 as a threshold for the top of the page
                if ri.IsAtFinalElement(RIL.BLOCK, RIL.TEXTLINE):
                    break
                continue

            #  Check if block is a See Also, if so, skip
            elif "See Also" in line:
                if ri.IsAtFinalElement(RIL.BLOCK, RIL.TEXTLINE):
                    break
                continue

            #  Check if block is a blank line, if so, skip
            elif line == '':
                if ri.IsAtFinalElement(RIL.BLOCK, RIL.TEXTLINE):
                    break
                continue

            #  Create Line object from text and bounding box
            l = Line(line, box)

            #  Removes stray marks from x coord calc
            for c in iterate_level(ri, RIL.SYMBOL):
                char = c.GetUTF8Text(RIL.SYMBOL)

                if special_chars_regex.search(char) is None:
                    l.left = c.BoundingBoxInternal(RIL.SYMBOL)[0]
                    break  # only need to find first non-special char
                if ri.IsAtFinalElement(RIL.TEXTLINE, RIL.SYMBOL):  # Never loop out of a Line
                    print(f"WARN: No text detected in {box}")
                    break

            if column_index >= len(columns):  # if column doesn't exist yet, create it
                columns.append(Column(column_index))
            columns[-1].append(l)  # add line to column

            # Never loop out of a block
            if ri.IsAtFinalElement(RIL.BLOCK, RIL.TEXTLINE):
                break

    combining_stop = time.perf_counter()
    combining_time = combining_stop - combining_start

    # Sort Columns into Columns with many lines (probably correct) and Columns with few lines (probably misreads)
    large_columns = []
    small_columns = []
    for column in columns:
        column.calc()  # calculate column bounds while we're looping through them all
        if len(column.lines) > 10:
            large_columns.append(column)
        else:
            small_columns.append(column)

    lonely_columns = []  # columns that don't match up with any other column (very likely wrong and unfixable)
    for column in small_columns:
        found_matching_col = False
        for curr_column in large_columns:
            if not found_matching_col \
                    and ((curr_column.left - column.left) < 50) \
                    and ((
                                 column.right - curr_column.right) < 50):  # if the columns start within 50 units of each other and end within 50 units of each other
                found_matching_col = True
                if column.top < curr_column.top:
                    # fragment is above the top of current column
                    lines = column.lines
                    lines += curr_column.lines  # prepend lines
                    curr_column.lines = lines  # save the lines
                    curr_column.calc()  # recalculate bounds
                else:
                    curr_column.lines += column.lines  # append lines to current column
                    curr_column.calc()  # recalculate bounds

        if not found_matching_col:
            lonely_columns.append(column)  # column doesn't match up with any other column, so it's probably wrong

    lines = []
    for column in large_columns:  # apply line combining to large columns, note: process is skipped for lonely columns
        column.sort()  # sort lines by y-coord with ~O(n) insertion sort
        column.combine_horz_lines()  # combine lines that are horizontally aligned
        column.combine_indent_lines()  # combine lines that are indented into records

        if debug:
            column.draw_lines(image)  # opens visual of lines
        lines = lines + column.to_dicts()  # Save Column objects as dicts for parquet/dataframe storage

    for column in lonely_columns:
        lines = lines + column.to_dicts(flag=True)  # append broken columns with flag

    if debug:
        print(f"\nOCR time: {ocr_time:.2f}s")
        print(f"Combining time: {combining_time:.2f}s")
        print(f"Found {len(lines)} lines")

    return lines


def block_ocr(start, ocr_dir, prepped_dir, change_list, debug=False, rerun=False):
    '''
    Runs OCR on all prepped images in the prepped_dir
    :param start: start time of the program
    :param temp_dir: directory to store ocr results as parquet files
    :param prepped_dir: directory containing prepped images
    :param rerun: if True, rerun OCR on all images
    :return: list() of OCR time for each page. Saves raw OCR output to temp_dir as parquet files
    '''
    with PyTessBaseAPI() as api:
        page_ocr = []
        empty = []  # list of pages with no text
        ocr_changed = []  # list of pages that were rerun
        size = len(glob.glob(prepped_dir + '/*_prep.jpg'))

        for ind, filepath in enumerate(sorted(glob.glob(prepped_dir + '/*_prep.jpg'), key=numerical_sort)):
            filename = filepath.split('/')[-1]
            current = f'{ind + 1} of {size}'
            progress_bar(start, filename, ind, current, size, "OCR")
            name = filename.replace('_prep.jpg', '_raw_ocr.parquet')

            if name not in change_list and not rerun and name in os.listdir(ocr_dir):
                continue

            ocr_start = time.perf_counter()
            image = cv2.imread(filepath)
            lines = organize_lines(api, image, debug)

            if len(lines) == 0:
                empty.append(filename)
                continue

            ocr_stop = time.perf_counter()
            ocr_time = ocr_stop - ocr_start
            page_ocr.append(ocr_time)

            progress_bar(start, filename, ind, current, size, "OCR")

            image_df = pd.DataFrame(lines)

            image_df.to_parquet(os.path.
                                join(ocr_dir,
                                     name), compression='gzip')  # save lines to parquet (smaller, faster than csv)
            ocr_changed.append(name)

            if ind // 25:  # clear tesseract and cached memory every 25th image
                api.Clear()
                gc.collect()
        else:
            gc.collect()

        empty_files = '\n'.join(empty)
        txt = (f'EMPTY IMAGES: {len(empty)}\n'
               f'{empty_files}')
        with open(os.path.join(ocr_dir, 'empty_images.txt'), 'w') as f:
            f.write(txt)

        return page_ocr, ocr_changed  # return list of ocr times for each page and list of pages that were passed


def see_ocr(filename, year_city_type_path=None, save=False):
    ocr = '_raw_ocr.parquet'
    parse = '_parsed.parquet'
    prep_image = '_prep.jpg'
    run_preprocessor = False
    image_name = None

    if len(filename.split('/')) > 1:  # if pathlike object
        image_name = filename.split('/')[-1]
        year_city_type_path = filename.replace(image_name, '')
        filename = filename.split('/')[-1]

    if ocr in filename:
        # image_name = filename.replace(ocr, prep_image)
        image_df = pd.read_parquet(os.path.join(year_city_type_path, filename))
        return image_df

    elif parse in filename:
        image_name = filename.replace(parse, prep_image)
    elif prep_image in filename:
        image_name = filename
    elif filename.split('.')[-1] == 'jpg':
        run_preprocessor = True
        image_name = filename.replace('.jpg', prep_image)
    else:
        raise KeyError(f"filename={filename} is not a valid filename")

    if image_name is None:
        raise KeyError(f"need to specify year_city_type_path or filename={filename} must be a pathlike object")

    if year_city_type_path is None:
        raise KeyError(f"need to specify year_city_type_path or filename={filename} must be a pathlike object")
    dirs = subdirectories(year_city_type_path)

    if run_preprocessor:
        preprocess(year_city_type_path, filename)

    prepped_dir = dirs[2]

    image_filepath = os.path.join(prepped_dir, image_name)
    image = cv2.imread(image_filepath)

    lines = organize_lines(PyTessBaseAPI(), image, True)

    image_df = pd.DataFrame(lines)

    if save:
        name = image_name.replace('.jpg', '_raw_ocr.parquet')
        image_df.to_parquet(os.path.
                            join(dirs[3],
                                 name), compression='gzip')

    return image_df
