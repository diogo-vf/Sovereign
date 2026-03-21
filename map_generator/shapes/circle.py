from . import Shape


class Circle(Shape):
    def __init__(self, size: int = 5):
        super().__init__(rows=size, cols=size)

    def is_generable(self, row: int, col: int) -> bool:
        return row * row + col * col < self.rows * self.rows

    def total_cells(self) -> int:
        N = self.rows
        return sum(1 for r in range(-N + 1, N) for c in range(-N + 1, N) if r * r + c * c < N * N)
