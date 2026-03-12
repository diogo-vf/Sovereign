from typing import Any
from map_generator import Shape, Hexagon, Rectangle


def remove_empty_cols(array: list[list[str]])-> list[list[str]]:
    rows = len(array)
    list_to_clear = array.copy()

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


def remove_empty_rows(array: list[list[str]])-> list[list[str]]:
    # start from the end
    for i in range(len(list_to_clear))[::-1]:
        if str.strip("".join(list_to_clear[i])) == '':
            del list_to_clear[i]


def clear_list(array: list[list[str]]) -> list[list[str]]:
    new_list = remove_empty_cols(array)
    return remove_empty_rows(new_list)


def generate_hex_map(shape: Shape) -> tuple[dict[tuple[int, int], str], list[list[str]]]: # TODO maybe generic type
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
                grid[(row, col)] = '✓'
                current_row.append('✓')
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
    for s in [Rectangle(3, 5), Hexagon(5)]:
        print(f"{s.__class__.__name__} (cells:{s.total_cells()})")
        print('_____________________')
        print_shape(*generate_hex_map(s))
