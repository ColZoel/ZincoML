"""
This module contains the functions for extracting text from an image using Tesseract OCR via Tessercocr.
"""
from utils.globals import header_re, pagenum
from tools.timers import *
from PIL import Image
from tesserocr import PyTessBaseAPI, RIL, iterate_level, PT
from utils.org.Line import Line
from utils.org.Column import Column
from utils.dirs import *
from utils import images
from multiprocessing import Pool

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


def ocr_task(image_path, x,y,w,h):  # TODO: add timer
    """
    OCR per image task
    """
    with PyTessBaseAPI() as api:
        image = images.box(image_path, x,y,w,h)
        lines = organize_lines(api, image, debug=False)
        if len(lines) == 0:
            return None
        ocr_dir = subdirectories(image_path)[4]
        image_df = pd.DataFrame(lines)
        image_df.to_parquet(os.path.join(ocr_dir, f'{file_stem(image_path)}.parquet'), compression='gzip')

    return image_df


def map_ocr(annotation_boxes, debug=False, cores=6):
    """
    Runs OCR in parallel on a list of images and bounding boxes. Returns a list of dataframes.
    """
    image_paths = [annotation_box[0] for annotation_box in annotation_boxes]
    annotations = [annotation_box[1:] for annotation_box in annotation_boxes]

    with Pool(cores) as p:
        dfs = p.starmap(ocr_task, [(image_path, annotations) for image_path, annotations in zip(image_paths, annotations)])
        p.close()
        p.join()

    return dfs


def save_aggregate(dfs, year_city_type_path):
    """
    Saves the aggregate dataframe to parquet
    """
    ocr_dir = subdirectories(year_city_type_path)[4]
    aggregate_df = pd.concat(dfs)
    aggregate_df.to_parquet(os.path.join(ocr_dir,
                                         f'{file_stem(year_city_type_path)}_aggregate.parquet'), compression='gzip')
    return aggregate_df



