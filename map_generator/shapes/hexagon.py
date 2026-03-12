from . import Shape


class Hexagon(Shape):
    def __init__(self, length_side: int = 2):
        super().__init__(rows=length_side, cols=length_side)

    def is_generable(self, row: int, col: int) -> bool:
        N = self.cols  # for a hex, cols = rows = side
        return abs(col) < N and abs(row) < N and abs(-col-row) < N
    
    def total_cells(self):
        return 3 * (self.cols - 1) * self.cols + 1
