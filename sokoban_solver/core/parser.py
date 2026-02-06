"""Parse Sokoban puzzle strings into grid and element representations."""


def parse_puzzle_string(puzzle_str):
    """Parse a puzzle string into a 2D grid of characters.

    Rows are padded with spaces to equal the width of the longest row.

    Args:
        puzzle_str: Multi-line string in standard Sokoban text format.

    Returns:
        list[list[str]]: 2D grid of single characters.
    """
    lines = puzzle_str.split('\n')
    # Strip trailing empty lines but preserve leading whitespace in each line
    while lines and lines[-1].strip() == '':
        lines.pop()
    while lines and lines[0].strip() == '':
        lines.pop(0)

    if not lines:
        return []

    max_width = max(len(line) for line in lines)

    grid = []
    for line in lines:
        row = list(line.ljust(max_width))
        grid.append(row)

    return grid


def extract_elements(grid):
    """Extract player, boxes, goals, and walls from a parsed grid.

    Handles combined characters:
        '+' = player on goal
        '*' = box on goal

    Args:
        grid: 2D list of characters from parse_puzzle_string().

    Returns:
        dict with keys: 'player', 'boxes', 'goals', 'walls', 'width', 'height'
    """
    player = None
    boxes = set()
    goals = set()
    walls = set()

    height = len(grid)
    width = len(grid[0]) if grid else 0

    for y, row in enumerate(grid):
        for x, char in enumerate(row):
            if char == '#':
                walls.add((x, y))
            elif char == '@':
                player = (x, y)
            elif char == '$':
                boxes.add((x, y))
            elif char == '.':
                goals.add((x, y))
            elif char == '+':
                player = (x, y)
                goals.add((x, y))
            elif char == '*':
                boxes.add((x, y))
                goals.add((x, y))

    return {
        'player': player,
        'boxes': boxes,
        'goals': goals,
        'walls': walls,
        'width': width,
        'height': height,
    }
