
class Line:
    """
        A class to represent a line of text

        Attributes
        ----------
        text : str  - The text of the line
        left : int  - The left coordinate of the line
        top : int  - The top coordinate of the line
        right : int  - The right coordinate of the line
        bottom : int  - The bottom coordinate of the line
        line_nums : [int]  - The line numbers that have been combined to make up the line
        review_flag : bool  - Whether or not the line needs to be reviewed by a human
    """

    def __init__(self, text: str, coords: tuple[int, int, int, int], line_nums: list[int] = None):
        """
            Creates a line object

            :param text: The text of the line
            :param coords: The coordinates of the line in the form (left, top, right, bottom)
            :param line_nums: The line numbers of the line

            :return: Line object
        """

        if line_nums is None:
            line_nums = []
        self.text: str = text
        self.left: int = coords[0]
        self.top: int = coords[1]
        self.right: int = coords[2]
        self.bottom: int = coords[3]
        self.line_nums: [int] = line_nums
        self.review_flag: bool = False if len(line_nums) < 5 else True  # if the line has more than 5 line numbers, it probably needs review
        # self.width: int = self.right - self.left
        # self.height: int = self.bottom - self.top

    def __repr__(self):
        return f"\"{self.text}\", ({self.left}, {self.top}))"

    def __str__(self):
        return f"\"{self.text}\", ({self.left}, {self.top}))"

    def __eq__(self, other):
        return (self.text, self.left, self.top, self.right, self.bottom) == (other.text, other.left, other.top, other.right, other.bottom)

    def __hash__(self):
        return hash((self.text, self.left, self.top, self.right, self.bottom))

    def __lt__(self, other):
        return self.top < other.top

    def __gt__(self, other):
        return self.top > other.top

    def __le__(self, other):
        return self.top <= other.top

    def __ge__(self, other):
        return self.top >= other.top

    def __ne__(self, other):
        return self.text != other.text or self.left != other.left or self.top != other.top or self.right != other.right or self.bottom != other.bottom

    def is_indented(self, parent):
        return (self.left - parent.left > 50) and (self.top - parent.top > 0)

    def is_same_line(self, other):
        return abs(self.top - other.top) < 5

    def to_dict(self) -> dict:
        """
            Converts the line to a dictionary

            :return: A dictionary of shape {
                        "raw_string": str,
                        "left": int,
                        "top": int,
                        "right": int,
                        "bottom": int,
                        "line_nums": [int],
                        "review_flag": bool
                    }
        """

        return {
            "raw_string": self.text,
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom,
            "line_nums": self.line_nums,
            "review_flag": False if len(self.line_nums) < 5 else True,
        }

