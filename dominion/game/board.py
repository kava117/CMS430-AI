import random
from game.constants import (
    TILE_WEIGHTS, MOUNTAIN, CAVE, DOMAIN, NONE, PLAYER, AI
)


def idx(x: int, y: int, W: int) -> int:
    return y * W + x


def xy(i: int, W: int) -> tuple[int, int]:
    return (i % W, i // W)


def in_bounds(x: int, y: int, W: int, H: int) -> bool:
    return 0 <= x < W and 0 <= y < H


def make_cell(tile_type: int) -> dict:
    return {'type': tile_type, 'owner': NONE, 'used': False}


def generate_board(seed: str, W: int, H: int) -> list[dict]:
    random.seed(seed)

    # Build weighted tile list for random selection
    types = list(TILE_WEIGHTS.keys())
    weights = [TILE_WEIGHTS[t] for t in types]
    total_weight = sum(weights)
    cumulative = []
    running = 0
    for w in weights:
        running += w
        cumulative.append(running / total_weight)

    def pick_tile() -> int:
        r = random.random()
        for i, threshold in enumerate(cumulative):
            if r < threshold:
                return types[i]
        return types[-1]

    # Generate random board
    board = [make_cell(pick_tile()) for _ in range(W * H)]

    # Guarantee at least 2 Cave tiles
    cave_count = sum(1 for c in board if c['type'] == CAVE)
    while cave_count < 2:
        i = random.randrange(W * H)
        if board[i]['type'] != MOUNTAIN:
            board[i]['type'] = CAVE
            cave_count += 1

    # Place Player Domain: start at (1,1), walk right skipping Mountains
    x, y = 1, 1
    while x < W and board[idx(x, y, W)]['type'] == MOUNTAIN:
        x += 1
    if x < W:
        board[idx(x, y, W)]['type'] = DOMAIN
        board[idx(x, y, W)]['owner'] = PLAYER

    # Place AI Domain: start at (W-2, H-2), walk left skipping Mountains or owned
    x, y = W - 2, H - 2
    while x >= 0 and (
        board[idx(x, y, W)]['type'] == MOUNTAIN or
        board[idx(x, y, W)]['owner'] != NONE
    ):
        x -= 1
    if x >= 0:
        board[idx(x, y, W)]['type'] = DOMAIN
        board[idx(x, y, W)]['owner'] = AI

    return board
