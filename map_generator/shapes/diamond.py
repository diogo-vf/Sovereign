from . import Shape


class Diamond(Shape):
    def __init__(self, size: int = 5):
        super().__init__(rows=size + 1, cols=size + 1)

    def is_generable(self, row: int, col: int) -> bool:
        N = self.cols - 1
        if row <= 0:
            return row >= -(N - 3) and abs(col) <= N + row
        else:
            return row <= N and abs(col) <= N - row

    def total_cells(self) -> int:
        N = self.cols - 1
        return 2 * N * N + 2 * N - 8
