from typing import Any
from map_generator import Shape, Hexagone, Rectangle

def generate_hex_map(shape: Shape) -> tuple[dict[tuple[int,int], str], list]:
    """
    Generic hex map generator.

    Args:
        shape: Shape defines which cell should exists

    Returns dictionnary composate by coordinate and value
    """
    grid = {}
    array = []

    for row in range(-shape.rows +1, shape.rows):
        current_row = []
        for col in range(-shape.cols +1, shape.cols):
            if shape.is_generable(row, col):
                grid[(row, col)] = "✓"
                current_row.append("✓")
            else:
                current_row.append(" ")
        
        array.append(current_row)

    return grid, array
    

def print_shape(grid: dict[tuple[int,int], str], array: list):
    for key in grid:
        print(f"({key[0]:3}, {key[1]:3}) → {grid[key]}")

    for row in array:
        print(" ".join(row))

        
if __name__ == "__main__":
    for shape in [Rectangle(3,5), Hexagone(5)]:
        print(f"{shape.__class__.__name__} (cells:{shape.total_cells()})")
        print("_____________________")
        print_shape(*generate_hex_map(shape))

