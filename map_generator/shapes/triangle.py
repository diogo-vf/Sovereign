from enum import Enum
from . import Shape


class TriangleType(Enum):
    ISOSCELES = "isosceles"
    EQUILATERAL = "equilateral"
    RIGHT = "right"

    def __str__(self):
        return self.value


class Triangle(Shape):
    def __init__(self, rows: int = 5, cols: int = None, triangle_type: TriangleType = TriangleType.ISOSCELES):
        if cols is None:
            cols = rows * 2 if triangle_type == TriangleType.EQUILATERAL else rows
        super().__init__(rows=rows, cols=cols)
        self.triangle_type = triangle_type

    def is_generable(self, row: int, col: int) -> bool:
        half_r = (self.rows - 1) // 2
        r = row + half_r  # distance from tip (0 = tip, grows toward base)
        match self.triangle_type:
            case TriangleType.ISOSCELES:
                return -half_r <= row <= half_r and abs(col) <= r
            case TriangleType.EQUILATERAL:
                return -half_r <= row <= half_r and abs(col) <= r * 2
            case TriangleType.RIGHT:
                half_c = (self.cols - 1) // 2
                # shift origin to centroid (1/3 height, 1/3 base from right-angle corner)
                er = row + (half_r + 1) // 3
                ec = col - (half_c + 1) // 3
                r_from_tip = er + half_r
                col_max = -half_c + r_from_tip * half_c // half_r if half_r > 0 else half_c
                return -half_r <= er <= half_r and -half_c <= ec <= col_max

    def total_cells(self) -> int:
        half_r = (self.rows - 1) // 2
        n = 2 * half_r + 1
        match self.triangle_type:
            case TriangleType.ISOSCELES:
                return n * n
            case TriangleType.EQUILATERAL:
                return n * (2 * n - 1)
            case TriangleType.RIGHT:
                half_c = (self.cols - 1) // 2
                return sum(k * half_c // half_r + 1 for k in range(n)) if half_r > 0 else 2 * half_c + 1

    def __str__(self):
        return f"{super().__str__()} {self.triangle_type}"
