import math
from game.board import generate_board, idx
from game.fog import compute_fog
from game.moves import compute_valid_moves
from game.claim import check_win_condition
from game.ai import heuristic, minimax_root, wizard_teleport_decision, minimax_alpha_beta
from game.constants import NONE, PLAYER, AI, CAVE, WIZARD, MOUNTAIN


def _make_G(seed='aitest', W=10, H=8, depth=2):
    board = generate_board(seed, W, H)
    G = {
        'W': W, 'H': H, 'depth': depth,
        'board': board, 'fog': set(),
        'wizard_active_for': NONE, 'log': [],
    }
    G['fog'] = compute_fog(G)
    return G


def test_heuristic_returns_float():
    G = _make_G()
    h = heuristic(G)
    assert isinstance(h, (int, float))
    assert math.isfinite(h)


def test_heuristic_increases_when_ai_gains_tile():
    G = _make_G()
    h_before = heuristic(G)
    free = next(
        i for i, c in enumerate(G['board'])
        if c['owner'] == NONE and c['type'] != MOUNTAIN and i in G['fog']
    )
    G['board'][free]['owner'] = AI
    h_after = heuristic(G)
    G['board'][free]['owner'] = NONE  # restore
    assert h_after > h_before


def test_minimax_root_returns_valid_move():
    G = _make_G()
    ai_moves = compute_valid_moves(G, AI)
    best = minimax_root(G, depth=2)
    assert best in ai_moves, f"minimax_root returned {best} which is not a valid AI move"


def test_minimax_root_does_not_mutate_board():
    G = _make_G()
    board_snapshot = [c.copy() for c in G['board']]
    fog_snapshot   = set(G['fog'])
    minimax_root(G, depth=2)
    assert [c['owner'] for c in G['board']] == [c['owner'] for c in board_snapshot]
    assert G['fog'] == fog_snapshot


def test_minimax_prefers_cave():
    W, H = 10, 8
    board = generate_board('cave-pref', W, H)
    G = {'W': W, 'H': H, 'depth': 2, 'board': board, 'fog': set(),
         'wizard_active_for': NONE, 'log': []}
    G['fog'] = compute_fog(G)
    ai_dom = next(i for i, c in enumerate(board) if c['owner'] == AI)
    from game.board import xy
    ax, ay = xy(ai_dom, W)
    cave_idx = idx(max(0, ax - 1), ay, W)
    board[cave_idx] = {'type': CAVE, 'owner': NONE, 'used': False}
    G['fog'].add(cave_idx)
    best = minimax_root(G, depth=2)
    # Cave adjacent to AI domain should be strongly preferred
    assert best == cave_idx or G['board'][best]['type'] == CAVE, \
        "AI did not prefer an adjacent Cave tile"


def test_wizard_teleport_decision_returns_high_value():
    G = _make_G()
    # Reveal a Cave tile for the wizard to target
    cave_idx = next(
        (i for i, c in enumerate(G['board'])
         if c['type'] == CAVE and c['owner'] == NONE),
        None
    )
    if cave_idx is None:
        return
    G['fog'].add(cave_idx)
    result = wizard_teleport_decision(G)
    assert result is not None
    assert G['board'][result]['type'] == CAVE or result == cave_idx


def test_wizard_teleport_decision_declines_low_value():
    G = _make_G()
    # Remove all high-value tiles from fog — only keep revealed mountains (unclaim-able)
    G['fog'] = set(
        i for i, c in enumerate(G['board'])
        if c['type'] == MOUNTAIN
    )
    result = wizard_teleport_decision(G)
    assert result is None  # all visible tiles are Mountains → decline
