"""Terminal-based ASCII visualization for Sokoban puzzles."""


def state_to_string(state, puzzle_static):
    """Convert a state to an ASCII string representation.

    Args:
        state: State with player_pos and boxes.
        puzzle_static: PuzzleStatic with walls, goals, width, height.

    Returns:
        str: Multi-line ASCII representation.
    """
    grid = [[' ' for _ in range(puzzle_static.width)]
            for _ in range(puzzle_static.height)]

    for x, y in puzzle_static.walls:
        grid[y][x] = '#'

    for x, y in puzzle_static.goals:
        grid[y][x] = '.'

    for x, y in state.boxes:
        if (x, y) in puzzle_static.goals:
            grid[y][x] = '*'
        else:
            grid[y][x] = '$'

    px, py = state.player_pos
    if (px, py) in puzzle_static.goals:
        grid[py][px] = '+'
    else:
        grid[py][px] = '@'

    return '\n'.join(''.join(row) for row in grid)


def display_state(state, puzzle_static):
    """Print the current puzzle state to terminal."""
    print(state_to_string(state, puzzle_static))
    print()


def playback_solution(initial_state, solution, puzzle_static, delay=0.5):
    """Animate solution in terminal with time delay."""
    import time
    import os
    from core.moves import apply_move

    current_state = initial_state

    print("Initial state:")
    display_state(current_state, puzzle_static)
    time.sleep(delay)

    for i, move in enumerate(solution):
        os.system('clear')
        print(f"Move {i + 1}/{len(solution)}: {move}")
        current_state = apply_move(current_state, move, puzzle_static)
        display_state(current_state, puzzle_static)
        time.sleep(delay)

    print("Solution complete!")
