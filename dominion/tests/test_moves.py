from game.board import generate_board, idx, xy
from game.fog import compute_fog
from game.moves import compute_valid_moves
from game.constants import (
    NONE, PLAYER, AI,
    FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN
)


def _make_G(seed='movetest', W=14, H=10):
    board = generate_board(seed, W, H)
    G = {'W': W, 'H': H, 'board': board, 'fog': set(), 'wizard_active_for': NONE}
    G['fog'] = compute_fog(G)
    return G


def test_player_has_moves_at_start():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    assert len(moves) > 0


def test_ai_has_moves_at_start():
    G = _make_G()
    moves = compute_valid_moves(G, AI)
    assert len(moves) > 0


def test_no_mountains_in_valid_moves():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    assert all(G['board'][i]['type'] != MOUNTAIN for i in moves)


def test_no_owned_tiles_in_valid_moves():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    assert all(G['board'][i]['owner'] == NONE for i in moves)


def test_no_fogged_tiles_in_valid_moves():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    assert all(i in G['fog'] for i in moves)


def test_plains_expansion_reaches_distance_2():
    W, H = 12, 10
    board = generate_board('plainstest', W, H)
    # Force a Plains tile owned by player at (3,3)
    pi = idx(3, 3, W)
    board[pi] = {'type': PLAINS, 'owner': PLAYER, 'used': False}
    G = {'W': W, 'H': H, 'board': board, 'fog': set(), 'wizard_active_for': NONE}
    G['fog'] = compute_fog(G)
    # Reveal tiles manually so distance-2 tiles pass the fog filter
    for dx, dy in [(0,-1),(0,1),(-1,0),(1,0),(0,-2),(0,2),(-2,0),(2,0)]:
        nx, ny = 3+dx, 3+dy
        if 0 <= nx < W and 0 <= ny < H:
            G['fog'].add(idx(nx, ny, W))
    moves = compute_valid_moves(G, PLAYER)
    dist2 = idx(3, 5, W)  # (3, 3+2)
    if board[dist2]['type'] != MOUNTAIN and board[dist2]['owner'] == NONE:
        assert dist2 in moves, "Plains did not reach distance-2 tile"


def test_tower_expansion_reaches_distance_3():
    W, H = 12, 10
    board = generate_board('towertest', W, H)
    ti = idx(4, 4, W)
    board[ti] = {'type': TOWER, 'owner': PLAYER, 'used': False}
    G = {'W': W, 'H': H, 'board': board, 'fog': set(), 'wizard_active_for': NONE}
    G['fog'] = compute_fog(G)
    for step in range(1, 4):
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = 4+dx*step, 4+dy*step
            if 0 <= nx < W and 0 <= ny < H:
                G['fog'].add(idx(nx, ny, W))
    moves = compute_valid_moves(G, PLAYER)
    dist3 = idx(4, 7, W)  # (4, 4+3)
    if board[dist3]['type'] != MOUNTAIN and board[dist3]['owner'] == NONE:
        assert dist3 in moves, "Tower did not reach distance-3 tile"


def test_wizard_teleport_returns_all_revealed_unclaimed():
    G = _make_G()
    G['wizard_active_for'] = PLAYER
    moves = compute_valid_moves(G, PLAYER)
    expected = {
        i for i, c in enumerate(G['board'])
        if c['owner'] == NONE and c['type'] != MOUNTAIN and i in G['fog']
    }
    assert moves == expected
    G['wizard_active_for'] = NONE  # restore
