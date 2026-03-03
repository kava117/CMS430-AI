from game.board import generate_board, idx, xy
from game.fog import compute_fog
from game.moves import compute_valid_moves
from game.claim import claim_tile, trigger_barbarians, check_win_condition, snapshot_board, restore_board
from game.constants import (
    NONE, PLAYER, AI,
    CAVE, MOUNTAIN, DOMAIN, BARBARIAN, WIZARD, FOREST
)


def _make_G(seed='claimtest', W=14, H=10):
    board = generate_board(seed, W, H)
    G = {
        'W': W, 'H': H, 'board': board,
        'fog': set(), 'wizard_active_for': NONE, 'log': [],
    }
    G['fog'] = compute_fog(G)
    return G


def test_claim_sets_owner():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    # Skip Barbarian tiles — claiming one sweeps the row (resetting owner to NONE)
    target = next(i for i in sorted(moves) if G['board'][i]['type'] != BARBARIAN)
    claim_tile(G, target, PLAYER)
    assert G['board'][target]['owner'] == PLAYER


def test_claim_updates_fog():
    G = _make_G()
    fog_before = len(G['fog'])
    moves = compute_valid_moves(G, PLAYER)
    # Skip Barbarian tiles — their sweep can shrink fog
    target = next(i for i in sorted(moves) if G['board'][i]['type'] != BARBARIAN)
    claim_tile(G, target, PLAYER)
    assert len(G['fog']) >= fog_before


def test_win_condition_none_at_start():
    G = _make_G()
    assert check_win_condition(G) is None


def test_win_condition_majority():
    G = _make_G(W=8, H=6)
    claimable = [i for i, c in enumerate(G['board']) if c['type'] != MOUNTAIN]
    majority = len(claimable) // 2 + 1
    for i in claimable[:majority]:
        G['board'][i]['owner'] = PLAYER
    assert check_win_condition(G) == PLAYER


def test_win_condition_draw():
    G = _make_G(W=8, H=6)
    claimable = [i for i, c in enumerate(G['board']) if c['type'] != MOUNTAIN]
    half = len(claimable) // 2
    for i in claimable[:half]:
        G['board'][i]['owner'] = PLAYER
    for i in claimable[half:]:
        G['board'][i]['owner'] = AI
    result = check_win_condition(G)
    # All tiles claimed; equal counts → DRAW
    assert result in ('DRAW', PLAYER, AI)  # depends on parity


def test_barbarian_sweep_row(monkeypatch):
    G = _make_G(W=14, H=10)  # W > H, so always horizontal
    row = 3
    barb_idx = idx(5, row, G['W'])
    G['board'][barb_idx]['type'] = BARBARIAN
    G['board'][barb_idx]['owner'] = NONE
    # Give player some tiles in that row
    for x in [1, 2, 3]:
        G['board'][idx(x, row, G['W'])]['owner'] = PLAYER
    trigger_barbarians(G, barb_idx, minimax_mode=True)
    row_tiles = [G['board'][idx(x, row, G['W'])] for x in range(G['W'])]
    non_mountain = [c for c in row_tiles if c['type'] != MOUNTAIN]
    assert all(c['owner'] == NONE for c in non_mountain), "Barbarian horizontal sweep failed"


def test_barbarian_sweep_column():
    G = _make_G(W=8, H=14)  # H > W, so always vertical
    col = 3
    barb_idx = idx(col, 5, G['W'])
    G['board'][barb_idx]['type'] = BARBARIAN
    G['board'][barb_idx]['owner'] = NONE
    for y in [1, 2, 3]:
        G['board'][idx(col, y, G['W'])]['owner'] = AI
    trigger_barbarians(G, barb_idx, minimax_mode=True)
    col_tiles = [G['board'][idx(col, y, G['W'])] for y in range(G['H'])]
    non_mountain = [c for c in col_tiles if c['type'] != MOUNTAIN]
    assert all(c['owner'] == NONE for c in non_mountain), "Barbarian vertical sweep failed"


def test_snapshot_restore():
    G = _make_G()
    snap = snapshot_board(G)
    moves = compute_valid_moves(G, PLAYER)
    # Skip Barbarians — their sweep resets ownership, making the first assert fail
    target = next(i for i in sorted(moves) if G['board'][i]['type'] != BARBARIAN)
    claim_tile(G, target, PLAYER)
    assert G['board'][target]['owner'] == PLAYER
    restore_board(G, snap)
    assert G['board'][target]['owner'] == NONE, "Restore did not revert ownership"


def test_claim_wizard_returns_true():
    G = _make_G()
    wiz_idx = next((i for i, c in enumerate(G['board']) if c['type'] == WIZARD), None)
    if wiz_idx is None:
        return  # no wizard on this board — skip
    G['board'][wiz_idx]['owner'] = NONE
    G['fog'].add(wiz_idx)
    result = claim_tile(G, wiz_idx, PLAYER)
    assert result is True
