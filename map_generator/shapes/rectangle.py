from . import Shape

class Rectangle(Shape):
    def __init__(self, rows = 1, cols = 1):
        super().__init__(rows, cols)
    
    def is_generable(self, row: int, col: int) -> bool:
        return -(self.rows // 2) <= row < (self.rows + 1) // 2 and \
               -(self.cols // 2) <= col < (self.cols + 1) // 2
    
    def total_cells(self):
        return self.rows * self.cols
