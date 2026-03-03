import random
from game.constants import (
    FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN,
    NONE, PLAYER, AI,
    TILE_WEIGHTS, VISION_RANGE, STRATEGIC_VALUE, TILE_ICON, DIRS
)
from game.board import idx, xy, in_bounds, make_cell, generate_board


# --- Constants tests (Step 2) ---

def test_tile_type_values_are_unique():
    types = [FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN]
    assert len(set(types)) == 8


def test_owner_values_are_unique():
    assert len({NONE, PLAYER, AI}) == 3


def test_tile_weights_cover_all_random_types():
    # Domain is placed deterministically, so it has no weight entry
    for t in [FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN]:
        assert t in TILE_WEIGHTS
    assert DOMAIN not in TILE_WEIGHTS


def test_vision_range_covers_all_types():
    for t in [FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN]:
        assert t in VISION_RANGE


def test_dirs_are_cardinal():
    assert len(DIRS) == 4
    assert all(len(d) == 2 for d in DIRS)


# --- Board tests (Step 3) ---

def test_idx_and_xy_roundtrip():
    W = 14
    for i in range(W * 10):
        x, y = xy(i, W)
        assert idx(x, y, W) == i


def test_in_bounds():
    assert in_bounds(0, 0, 10, 8)
    assert not in_bounds(-1, 0, 10, 8)
    assert not in_bounds(10, 0, 10, 8)
    assert not in_bounds(0, 8, 10, 8)


def test_make_cell_defaults():
    c = make_cell(CAVE)
    assert c == {'type': CAVE, 'owner': NONE, 'used': False}


def test_board_length():
    board = generate_board('test', 14, 10)
    assert len(board) == 140


def test_cave_guarantee():
    for seed in ['a', 'b', 'c', 'test123', 'xyz']:
        board = generate_board(seed, 14, 10)
        caves = [c for c in board if c['type'] == CAVE]
        assert len(caves) >= 2, f"Seed '{seed}' produced fewer than 2 caves"


def test_domain_placement():
    board = generate_board('test', 14, 10)
    player_domain = next((c for c in board if c['type'] == DOMAIN and c['owner'] == PLAYER), None)
    ai_domain     = next((c for c in board if c['type'] == DOMAIN and c['owner'] == AI), None)
    assert player_domain is not None, "Player domain missing"
    assert ai_domain is not None, "AI domain missing"


def test_mountains_never_owned():
    board = generate_board('test', 14, 10)
    assert all(c['owner'] == NONE for c in board if c['type'] == MOUNTAIN)


def test_determinism():
    b1 = generate_board('myseed', 14, 10)
    b2 = generate_board('myseed', 14, 10)
    assert [c['type'] for c in b1] == [c['type'] for c in b2]


def test_different_seeds_differ():
    b1 = generate_board('seed-A', 14, 10)
    b2 = generate_board('seed-B', 14, 10)
    assert [c['type'] for c in b1] != [c['type'] for c in b2]
