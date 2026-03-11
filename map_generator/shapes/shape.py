from abc import ABC, abstractmethod

class Shape(ABC):
    def __init__(self, rows: int = 1, cols: int = 1):
        """
        side defines the length of the shape
        """
        self.rows = rows
        self.cols = cols

    @abstractmethod
    def is_generable(self, row: int, col: int) -> bool:
        """Returns True if the cell at (col, row) should exist."""
        pass

    @abstractmethod
    def total_cells(self) -> int:
        pass
