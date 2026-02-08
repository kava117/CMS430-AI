"""Move generation and player reachability for Sokoban solver."""

from collections import deque
from core.state import State

DIRECTIONS = {
    'U': (0, -1),
    'D': (0, 1),
    'L': (-1, 0),
    'R': (1, 0),
}


def get_reachable_positions(player_pos, boxes, walls, width, height):
    """BFS to find all positions the player can reach without pushing boxes.

    Args:
        player_pos: (x, y) starting position.
        boxes: frozenset of (x, y) box positions (treated as obstacles).
        walls: frozenset of (x, y) wall positions.
        width: Grid width.
        height: Grid height.

    Returns:
        set of (x, y) reachable positions.
    """
    obstacles = walls | boxes
    visited = {player_pos}
    queue = deque([player_pos])

    while queue:
        x, y = queue.popleft()
        for dx, dy in DIRECTIONS.values():
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height and
                    (nx, ny) not in obstacles and (nx, ny) not in visited):
                visited.add((nx, ny))
                queue.append((nx, ny))

    return visited


def generate_moves(state, puzzle_static):
    """Generate all valid box pushes from the current state.

    For each box, check all 4 directions. A push is valid if:
    1. The player can reach the push-from position (opposite side of box).
    2. The push destination (box + direction) is not a wall or another box.

    Args:
        state: Current State (player_pos, boxes).
        puzzle_static: PuzzleStatic with walls, goals, width, height.

    Returns:
        list of (direction_char, new_state) tuples.
    """
    reachable = get_reachable_positions(
        state.player_pos, state.boxes, puzzle_static.walls,
        puzzle_static.width, puzzle_static.height
    )
    obstacles = puzzle_static.walls | state.boxes
    moves = []

    for box in state.boxes:
        bx, by = box
        for direction, (dx, dy) in DIRECTIONS.items():
            # Player must stand on opposite side of push direction
            push_from = (bx - dx, by - dy)
            # Box moves in the push direction
            push_to = (bx + dx, by + dy)

            if (push_from in reachable and
                    push_to not in obstacles and
                    0 <= push_to[0] < puzzle_static.width and
                    0 <= push_to[1] < puzzle_static.height):
                new_boxes = (state.boxes - {box}) | {push_to}
                new_state = State(player_pos=box, boxes=new_boxes)
                moves.append((direction, new_state, box))

    return moves


def apply_move(state, direction, puzzle_static):
    """Apply a push move to a state and return the new state.

    Finds which box the player is pushing based on the direction,
    then moves the box and player.

    Args:
        state: Current State.
        direction: One of 'U', 'D', 'L', 'R'.
        puzzle_static: PuzzleStatic.

    Returns:
        New State after the push.
    """
    dx, dy = DIRECTIONS[direction]
    px, py = state.player_pos

    # The box being pushed is adjacent to the player in the push direction
    # But the player may not be adjacent — they need to walk to push position first.
    # In our model, we find the box that can be pushed from the player's reachable area.
    # For apply_move (replaying a known solution), we search for the box.

    reachable = get_reachable_positions(
        state.player_pos, state.boxes, puzzle_static.walls,
        puzzle_static.width, puzzle_static.height
    )

    for box in state.boxes:
        bx, by = box
        push_from = (bx - dx, by - dy)
        push_to = (bx + dx, by + dy)

        if (push_from in reachable and
                push_to not in (puzzle_static.walls | state.boxes) and
                0 <= push_to[0] < puzzle_static.width and
                0 <= push_to[1] < puzzle_static.height):
            new_boxes = (state.boxes - {box}) | {push_to}
            return State(player_pos=box, boxes=new_boxes)

    raise ValueError(f"No valid {direction} push from state {state}")
