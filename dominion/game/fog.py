from collections import deque
from game.constants import VISION_RANGE, CAVE, NONE, DIRS
from game.board import idx, xy, in_bounds


def bfs_reveal(board: list[dict], W: int, H: int, start_idx: int, vision_range: int) -> set[int]:
    """BFS from start_idx up to vision_range steps. Mountains do not block propagation."""
    if vision_range <= 0:
        return {start_idx}

    revealed = {start_idx}
    queue = deque([(start_idx, 0)])

    while queue:
        current, dist = queue.popleft()
        if dist >= vision_range:
            continue
        cx, cy = xy(current, W)
        for dx, dy in DIRS:
            nx, ny = cx + dx, cy + dy
            if in_bounds(nx, ny, W, H):
                ni = idx(nx, ny, W)
                if ni not in revealed:
                    revealed.add(ni)
                    queue.append((ni, dist + 1))

    return revealed


def compute_fog(G: dict) -> set[int]:
    """Compute the set of all revealed tile indices based on current board ownership."""
    board = G['board']
    W, H = G['W'], G['H']

    fog = set()

    # Track whether any cave is owned
    any_cave_owned = False
    cave_indices = []

    for i, cell in enumerate(board):
        if cell['type'] == CAVE:
            cave_indices.append(i)
            if cell['owner'] != NONE:
                any_cave_owned = True

        if cell['owner'] != NONE:
            vision = VISION_RANGE.get(cell['type'], 0)
            if vision > 0:
                fog |= bfs_reveal(board, W, H, i, vision)
            else:
                fog.add(i)  # The tile itself is always revealed if owned

    # Cave special: owning any Cave reveals all Cave tiles
    if any_cave_owned:
        fog.update(cave_indices)

    return fog
