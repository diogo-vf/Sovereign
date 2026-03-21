from . import Shape


class Rhombus(Shape):
    def __init__(self, size: int = 2):
        super().__init__(rows=size, cols=size)

    def is_generable(self, row: int, col: int) -> bool:
        return abs(row) + abs(col) < self.rows

    def total_cells(self) -> int:
        N = self.rows
        return 2 * N * N - 2 * N + 1
