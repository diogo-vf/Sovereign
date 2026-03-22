def render_hex_map(cells: dict[tuple[int, int], str]) -> str:
    """
    Render every cell has an ASCII Hexagon in the console.
    Each cell is drawn as:
    
         __
        /  \\
        \\__/

    Adjacent cells interlock their edges automatically.

    The formula choice (axial vs offset) is determined automatically by
    picking whichever produces a more compact result.
    """
    if not cells:
        return ""

    LEFT_MARGIN = 4  # Left space before drawing the map


    def draw(grid: dict, cells: dict, get_xy):
        for (row, col) in cells:
            y, x = get_xy(row, col)
            grid[(y, x)] = '_'
            grid[(y, x + 1)] = '_'
            grid[(y+1, x - 1)] = '/'
            grid[(y+1, x)] = ' '
            grid[(y+1, x + 1)] = ' '
            grid[(y+1, x + 2)] = '\\'
            grid[(y+2, x - 1)] = '\\'
            grid[(y+2, x)] = '_'
            grid[(y+2, x + 1)] = '_'
            grid[(y+2, x + 2)] = '/'

    def to_lines(grid: dict) -> str:
        if not grid:
            return ""
        max_y = max(k[0] for k in grid)
        max_x = max(k[1] for k in grid)
        lines = [
            ''.join(grid.get((y, x), ' ') for x in range(max_x + 1)).rstrip()
            for y in range(max_y + 1)
        ]
        while lines and not lines[-1].strip():
            lines.pop()
        return '\n'.join(lines)

    # axial formula: y = BASE_Y + 2*row + col
    # Works for shapes whose col axis is diagonal (e.g. Hexagon).

    def axial_lines(cells):
        min_key = min(2*r + c for r, c in cells)
        min_col = min(c for r, c in cells)
        BASE_Y   = -min_key
        CENTER_X = LEFT_MARGIN + 1 - 3 * min_col
        return max(BASE_Y + 2*r + c for r, c in cells) + 3

    def render_axial(cells):
        min_key = min(2*r + c for r, c in cells)
        min_col = min(c for r, c in cells)
        BASE_Y   = -min_key
        CENTER_X = LEFT_MARGIN + 1 - 3 * min_col

        def get_xy(row, col):
            return BASE_Y + 2*row + col, CENTER_X + 3*col

        grid: dict = {}
        draw(grid, cells, get_xy)
        return to_lines(grid)

    # offset formula: y = 2*(row - min_row) + parity(col - min_col)
    # Works for shapes with straight horizontal rows (Rectangle, Triangle, Diamond…).
    # parity = 1 if (col-min_col) is even, 0 if odd  → auto-shift so min_y == 0.

    def offset_lines(cells):
        min_row = min(r for r, _ in cells)
        min_col = min(c for _, c in cells)

        def raw_y(r, c):
            return (r - min_row) * 2 + (1 if (c - min_col) % 2 == 0 else 0)

        y_off = min(raw_y(r, c) for r, c in cells)
        return max(raw_y(r, c) - y_off for r, c in cells) + 3

    def render_offset(cells):
        min_row = min(r for r, c in cells)
        min_col = min(c for r, c in cells)

        def raw_y(r, c):
            return (r - min_row) * 2 + (1 if (c - min_col) % 2 == 0 else 0)

        y_off = min(raw_y(r, c) for r, c in cells)

        def get_xy(row, col):
            col_idx = col - min_col
            x = LEFT_MARGIN + 1 + col_idx * 3
            y = raw_y(row, col) - y_off
            return y, x

        grid: dict = {}
        draw(grid, cells, get_xy)
        return to_lines(grid)

    # Select the more compact formula
    if axial_lines(cells) <= offset_lines(cells):
        return render_axial(cells)
    else:
        return render_offset(cells)
