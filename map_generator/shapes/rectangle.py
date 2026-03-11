from . import Shape

class Rectangle(Shape):
    def __init__(self, rows = 1, cols = 1):
        super().__init__(rows, cols)
    
    def is_generable(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols
    
    def total_cells(self):
        return self.rows * self.cols
