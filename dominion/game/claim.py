import random
from game.constants import (
    MOUNTAIN, BARBARIAN, WIZARD, NONE, PLAYER, AI
)
from game.board import idx, xy, in_bounds
from game.fog import compute_fog


def snapshot_board(G: dict) -> list[dict]:
    """Return a shallow copy of the board (all cell values are primitives)."""
    return [cell.copy() for cell in G['board']]


def restore_board(G: dict, snap: list[dict]):
    """Restore board from snapshot and recompute fog."""
    for i, cell in enumerate(snap):
        G['board'][i] = cell.copy()
    G['fog'] = compute_fog(G)


def trigger_barbarians(G: dict, index: int, minimax_mode: bool = False):
    """Sweep the row or column of the given Barbarian tile, resetting ownership."""
    board = G['board']
    W, H = G['W'], G['H']
    x, y = xy(index, W)

    if W > H:
        direction = 'h'
    elif H > W:
        direction = 'v'
    else:
        # Square board: deterministic during minimax, random otherwise
        direction = 'h' if minimax_mode else random.choice(['h', 'v'])

    if direction == 'h':
        # Sweep entire row
        for cx in range(W):
            ci = idx(cx, y, W)
            if board[ci]['type'] != MOUNTAIN:
                board[ci]['owner'] = NONE
    else:
        # Sweep entire column
        for cy in range(H):
            ci = idx(x, cy, W)
            if board[ci]['type'] != MOUNTAIN:
                board[ci]['owner'] = NONE

    if not minimax_mode:
        G['log'].append(
            f"Barbarians sweep {'row ' + str(y) if direction == 'h' else 'column ' + str(x)}!"
        )

    G['fog'] = compute_fog(G)


def claim_tile(G: dict, index: int, owner: int, minimax_mode: bool = False) -> bool:
    """
    Claim a tile for owner. Returns True if the claimed tile was a Wizard.
    Triggers barbarian effects as needed.
    """
    board = G['board']
    fog_before = set(G['fog'])

    # Claim the tile
    board[index]['owner'] = owner

    # If the claimed tile is a Barbarian, trigger sweep immediately
    if board[index]['type'] == BARBARIAN:
        trigger_barbarians(G, index, minimax_mode)

    # Recompute fog after claim
    G['fog'] = compute_fog(G)

    # Check newly revealed tiles for Barbarians
    newly_revealed = sorted(G['fog'] - fog_before)
    for ni in newly_revealed:
        if ni == index:
            continue
        if board[ni]['type'] == BARBARIAN and board[ni]['owner'] == NONE:
            trigger_barbarians(G, ni, minimax_mode)

    was_wizard = board[index]['type'] == WIZARD
    return was_wizard


def check_win_condition(G: dict) -> int | str | None:
    """
    Returns PLAYER, AI, 'DRAW', or None.
    PLAYER/AI if they have majority. 'DRAW' if all tiles claimed and equal.
    None if game continues.
    """
    board = G['board']
    claimable = [c for c in board if c['type'] != MOUNTAIN]
    total = len(claimable)
    if total == 0:
        return None

    player_count = sum(1 for c in claimable if c['owner'] == PLAYER)
    ai_count = sum(1 for c in claimable if c['owner'] == AI)
    majority = total // 2 + 1

    if player_count >= majority:
        return PLAYER
    if ai_count >= majority:
        return AI

    # Check if all tiles are claimed
    if player_count + ai_count == total:
        if player_count > ai_count:
            return PLAYER
        elif ai_count > player_count:
            return AI
        else:
            return 'DRAW'

    return None
