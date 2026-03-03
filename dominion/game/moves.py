from game.constants import (
    FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN,
    NONE, PLAYER, AI, DIRS
)
from game.board import idx, xy, in_bounds


def compute_valid_moves(G: dict, owner: int) -> set[int]:
    """Compute the set of valid move indices for the given owner."""
    board = G['board']
    W, H = G['W'], G['H']
    fog = G['fog']

    # Wizard teleport phase: any revealed unclaimed non-Mountain tile
    if G.get('wizard_active_for', NONE) == owner:
        return {
            i for i, c in enumerate(board)
            if c['owner'] == NONE and c['type'] != MOUNTAIN and i in fog
        }

    candidates = set()

    for i, cell in enumerate(board):
        if cell['owner'] != owner:
            continue

        tile_type = cell['type']
        cx, cy = xy(i, W)

        if tile_type in (FOREST, DOMAIN, WIZARD, BARBARIAN):
            # Cardinal neighbors at distance 1
            for dx, dy in DIRS:
                nx, ny = cx + dx, cy + dy
                if in_bounds(nx, ny, W, H):
                    candidates.add(idx(nx, ny, W))

        elif tile_type == PLAINS:
            # Cardinal positions at distance 1 and 2
            for dx, dy in DIRS:
                for step in range(1, 3):
                    nx, ny = cx + dx * step, cy + dy * step
                    if in_bounds(nx, ny, W, H):
                        candidates.add(idx(nx, ny, W))

        elif tile_type == TOWER:
            # Cardinal positions at distance 1, 2, and 3 (Mountains don't block)
            for dx, dy in DIRS:
                for step in range(1, 4):
                    nx, ny = cx + dx * step, cy + dy * step
                    if in_bounds(nx, ny, W, H):
                        candidates.add(idx(nx, ny, W))

        elif tile_type == CAVE:
            # All Cave tile indices anywhere on the board
            for j, c in enumerate(board):
                if c['type'] == CAVE:
                    candidates.add(j)

    # Filter: unclaimed, non-Mountain, revealed
    return {
        i for i in candidates
        if board[i]['owner'] == NONE
        and board[i]['type'] != MOUNTAIN
        and i in fog
    }
