import cv2
import numpy as np
from PIL import Image
from utils.org.Line import Line
from utils.images import hsv_to_rgb, insertion_sort


class Column:
    """
    A class that represents a Column of Lines

    Attributes
    ----------
    index : int  - The index of the column
    left : int  - The left-most coordinate of the column
    top : int  - The top-most coordinate of the column
    right : int  - The right-most coordinate of the column
    bottom : int  - The bottom-most coordinate of the column
    lines : [Line]  - A list of Line objects in the column
    """

    def __init__(self, index: int):
        self.index: int = index
        self.left: int = 0
        self.top: int = 0
        self.right: int = 0
        self.bottom: int = 0
        self.lines: [Line] = []

    def __repr__(self):
        return f"Column {self.index} ({len(self.lines)}))"

    def __str__(self):
        return f"Column {self.index} ({len(self.lines)}))"

    def append(self, line):
        self.lines.append(line)

    def calc(self):
        self.left: int = 999999  # Reinitialize
        self.top: int = 999999
        self.right: int = 0
        self.bottom: int = 0

        for line in self.lines:
            if self.left > line.left:
                self.left = line.left  # Min

            if self.right < line.right:
                self.right = line.right  # Max

            if self.top > line.top:
                self.top = line.top  # Min

            if self.bottom < line.bottom:
                self.bottom = line.bottom  # Max

    def sort(self):
        self.lines = insertion_sort(self.lines)

        for i, line in enumerate(self.lines):
            line.line_nums = [i]  # Set line number based on column position
        # print("done!")

    def combine_horz_lines(self, threshold=10):
        """
            Combines lines that have the same top y coordinate within a threshold

            :param threshold: The maximum distance between two lines to be combined

            :return: None, modifies self.lines
        """

        remove = []
        for i, line in enumerate(self.lines):
            if i + 1 >= len(self.lines):  # If last line or only line, skip
                continue
            if abs(line.top - self.lines[i + 1].top) < threshold:  # if difference in top is less than threshold
                if line.left < self.lines[i + 1].left:
                    text = line.text + " " + self.lines[i + 1].text  # line is left, line + 1 is right
                else:
                    text = self.lines[i + 1].text + " " + line.text  # line is right, line + 1 is left

                x_min = line.left if line.left < self.lines[i + 1].left else self.lines[i + 1].left
                y_min = line.top if line.top < self.lines[i + 1].top else self.lines[i + 1].top
                x_max = line.right if line.right > self.lines[i + 1].right else self.lines[i + 1].right
                y_max = line.bottom if line.bottom > self.lines[i + 1].bottom else self.lines[i + 1].bottom
                line = Line(text, (x_min, y_min, x_max, y_max))  # Create new line with new bounds

                remove.append(i)  # remember to remove the old lines
                self.lines[i + 1] = line  # replace the next line with the new line, old line is left as is and will be removed later

        for i in sorted(remove, reverse=True):  # reverse so that the index doesn't change on us as we delete
            del self.lines[i]  # remove the old lines

        self.sort()  # Re-sort ensures line numbers are correct

    def draw_lines(self, image: Image):
        """
            Draws the bounding boxes of the lines in a column on the image

            :param image: The image to draw the bounding boxes on

            :return: None, image is shown in a new window using PIL.Image.show()
        """

        image_cv = np.array(image)  # Convert to cv2 image

        hue = 0
        for line in self.lines:
            x1, y1, x2, y2 = line.left, line.top, line.right, line.bottom
            image_cv = cv2.rectangle(image_cv, (x1, y1), (x2, y2), hsv_to_rgb(hue, 1, 1), 3)  # Draw bounding box
            hue += 0.001  # Increment hue

        Image.fromarray(image_cv).show()  # Convert back to PIL image and show
        return

    def combine_indent_lines(self, threshold=50):
        """
            Combines lines that are indented within a threshold

            :param threshold: The min distance between the starting points of line and column to be considered indented

            :return: None, modifies self.lines
        """

        n_lines = []  # New lines to replace self.lines
        for i, line in enumerate(self.lines):
            if i <= 0:  # First line, skip
                n_lines.append(line)
                continue
            elif (line.left - self.left) > threshold:  # line is indented by threshold pixels to the right
                #  Line is indented
                last_line = n_lines[-1]  # Get previous line

                text = last_line.text + "\n" + line.text
                x_min = line.left if line.left < last_line.left else last_line.left
                y_min = line.top if line.top < last_line.top else last_line.top
                x_max = line.right if line.right > last_line.right else last_line.right
                y_max = line.bottom if line.bottom > last_line.bottom else last_line.bottom

                # Overwrite last line with the new combined line
                n_lines[-1] = Line(text, (x_min, y_min, x_max, y_max), last_line.line_nums + line.line_nums)
            else:
                n_lines.append(line)

        self.lines = n_lines
        return

    def to_dicts(self, flag=False) -> list[dict]:
        """
            Converts the lines in the column to a list of dictionaries

            :param flag: If True, adds a "review_flag" key to each dictionary with a value of True

            :return: A list of dictionaries of shape {
                    "raw_string": str,
                    "left": int,
                    "top": int,
                    "right": int,
                    "bottom": int,
                    "line_nums": [int],
                    "review_flag": bool
                }
        """

        dicts = []
        for line in self.lines:
            dicts.append(line.to_dict())

        if flag:
            for d in dicts:
                d["review_flag"] = True
        return dicts
