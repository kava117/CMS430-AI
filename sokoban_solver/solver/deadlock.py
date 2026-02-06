"""Deadlock detection for Sokoban solver."""


def is_corner_deadlock(pos, walls, goals):
    """Check if a position is a corner deadlock (box stuck in corner, not on goal)."""
    x, y = pos
    if pos in goals:
        return False

    top = (x, y - 1) in walls
    bottom = (x, y + 1) in walls
    left = (x - 1, y) in walls
    right = (x + 1, y) in walls

    return ((top and left) or (top and right) or
            (bottom and left) or (bottom and right))


def compute_static_deadlocks(walls, goals, width, height):
    """Precompute all positions that are static deadlocks (corners not on goals).

    Args:
        walls: frozenset of wall positions.
        goals: frozenset of goal positions.
        width: Grid width.
        height: Grid height.

    Returns:
        frozenset of deadlock positions.
    """
    deadlocks = set()
    for y in range(height):
        for x in range(width):
            pos = (x, y)
            if pos not in walls and pos not in goals:
                if is_corner_deadlock(pos, walls, goals):
                    deadlocks.add(pos)
    return frozenset(deadlocks)


def is_freeze_deadlock(boxes, walls, goals):
    """Detect boxes that cannot move in any direction and are not on goals."""
    box_set = set(boxes)

    for bx, by in boxes:
        if (bx, by) in goals:
            continue

        can_move = False
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            new_box = (bx + dx, by + dy)
            push_from = (bx - dx, by - dy)
            if (new_box not in walls and new_box not in box_set and
                    push_from not in walls):
                can_move = True
                break

        if not can_move:
            return True

    return False


def is_2x2_deadlock(boxes, walls, goals):
    """Detect four boxes forming an immovable 2x2 square (not all on goals)."""
    box_set = set(boxes)

    for x, y in boxes:
        square = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
        if all(pos in box_set for pos in square):
            if not all(pos in goals for pos in square):
                return True

    return False


def is_deadlocked(state, puzzle_static):
    """Apply all deadlock detection strategies.

    Returns True if state is provably unsolvable.
    """
    boxes = state.boxes

    # Quick check: any box on precomputed deadlock square?
    if any(box in puzzle_static.deadlock_squares for box in boxes):
        return True

    # Dynamic deadlock checks
    if is_freeze_deadlock(boxes, puzzle_static.walls, puzzle_static.goals):
        return True

    if is_2x2_deadlock(boxes, puzzle_static.walls, puzzle_static.goals):
        return True

    return False
