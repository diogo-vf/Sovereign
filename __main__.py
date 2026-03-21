from typing import Any
from map_generator import Shape, Hexagon, Rectangle, Rhombus, Diamond, Circle, Triangle, TriangleType


def remove_empty_cols(array: list[list[str]]) -> list[list[str]]:
    rows = len(array)
    list_to_clear = array

    # starting from the end, prevent out of index
    for col in range(len(list_to_clear[0]))[::-1]:
        empty_col = True
        for row in range(rows):
            value = list_to_clear[row][col]
            if str.strip(value) != '':
                empty_col = False
                break

        if empty_col:
            for row in range(rows):
                del list_to_clear[row][col]

    return list_to_clear


def remove_empty_rows(array: list[list[str]]) -> list[list[str]]:
    # start from the end
    for i in range(len(array))[::-1]:
        if str.strip("".join(array[i])) == '':
            del array[i]

    return array


def clear_list(array: list[list[str]]) -> list[list[str]]:
    new_list = remove_empty_cols(array)
    return remove_empty_rows(new_list)


def generate_hex_map(shape: Shape) -> tuple[dict[tuple[int, int], str], list[list[str]]]:  # TODO maybe generic type
    """
    Generic hex map generator.

    Args:
        shape: Shape defines which cell should exists

    Returns dictionnary composate by coordinate and value
    """
    grid = {}
    array = []

    for row in range(-shape.rows + 1, shape.rows):
        current_row = []
        for col in range(-shape.cols + 1, shape.cols):
            if shape.is_generable(row, col):
                char = '•' if row == 0 and col == 0 else '✓'
                grid[(row, col)] = char
                current_row.append(char)
            else:
                current_row.append('')

        array.append(current_row)

    return grid, clear_list(array)


def print_shape(grid: dict[tuple[int, int], str], array: list[list[str]]):
    # for key in grid:
    #     print(f"({key[0]:3}, {key[1]:3}) → {grid[key]}")
    # print("\n")

    for row in array:
        print(' '.join([' ' if x == '' else x for x in row]))
    print("\n")


if __name__ == '__main__':
    for s in [
        Rectangle(3, 5), 
        Hexagon(5), 
        Rhombus(5), 
        Diamond(5), 
        Circle(5),
        Triangle(5, triangle_type=TriangleType.ISOSCELES),
        Triangle(5, triangle_type=TriangleType.EQUILATERAL),
        Triangle(5, triangle_type=TriangleType.RIGHT),
        Triangle(5, 9, TriangleType.RIGHT),
    ]:
        print(f"{s} (cells:{s.total_cells()})")
        print('_____________________')
        print_shape(*generate_hex_map(s))
