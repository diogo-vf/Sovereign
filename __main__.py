from map_generator import Shape, Hexagon, Rectangle, Rhombus, Diamond, Circle, Triangle, TriangleType, render_map


def generate_hex_map(shape: Shape) -> dict[tuple[int, int], str]:
    grid = {}
    for row in range(-shape.rows + 1, shape.rows):
        for col in range(-shape.cols + 1, shape.cols):
            if shape.is_generable(row, col):
                grid[(row, col)] = '•' if row == 0 and col == 0 else '·'
    return grid


def print_shape(grid: dict[tuple[int, int], str]):
    for key in grid:
        print(f"({key[0]:3}, {key[1]:3}) → {grid[key]}")
    print("\n")

    # for row in array:
    #     print(' '.join([' ' if x == '' else x for x in row]))
    # print("\n")

if __name__ == '__main__':

    for s in [
        Rectangle(3, 9),
        Hexagon(5),
        Rhombus(5),
        Diamond(6),
        Circle(5),
        Triangle(5, 10, triangle_type=TriangleType.ISOSCELES),
        Triangle(5, triangle_type=TriangleType.EQUILATERAL),
        Triangle(5, triangle_type=TriangleType.RIGHT),
        Triangle(8, 4, TriangleType.RIGHT),
    ]:
        print(f"{s} (cells:{s.total_cells()})")
        print('_____________________')
        # print_shape(generate_hex_map(s))
        print(render_map(generate_hex_map(s)))

