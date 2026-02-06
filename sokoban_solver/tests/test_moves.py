from core.moves import get_reachable_positions, generate_moves, apply_move
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements


# --- Step 1.6: Reachability tests ---

def test_reachable_open_room():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0),
                       (0, 1), (3, 1),
                       (0, 2), (3, 2),
                       (0, 3), (1, 3), (2, 3), (3, 3)])
    boxes = frozenset()
    reachable = get_reachable_positions((1, 1), boxes, walls, 4, 4)

    assert (1, 1) in reachable
    assert (2, 1) in reachable
    assert (1, 2) in reachable
    assert (2, 2) in reachable
    assert (0, 0) not in reachable


def test_reachable_blocked_by_box():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0),
                       (0, 1), (3, 1),
                       (0, 2), (3, 2),
                       (0, 3), (1, 3), (2, 3), (3, 3)])
    boxes = frozenset([(2, 1)])
    reachable = get_reachable_positions((1, 1), boxes, walls, 4, 4)

    assert (1, 1) in reachable
    assert (2, 1) not in reachable
    assert (1, 2) in reachable


def test_reachable_completely_blocked():
    walls = frozenset([(0, 0), (1, 0), (2, 0),
                       (0, 1), (2, 1),
                       (0, 2), (1, 2), (2, 2)])
    reachable = get_reachable_positions((0, 1), frozenset([(1, 1)]), walls, 3, 3)
    assert (1, 1) not in reachable


# --- Step 1.7: Move generation tests ---

def test_generate_simple_push():
    puzzle = """#####
#   #
# $ #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    moves = generate_moves(state, static)
    directions = [m[0] for m in moves]
    assert 'U' in directions


def test_generate_blocked_push():
    puzzle = """#####
#   #
##$ #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    moves = generate_moves(state, static)
    assert len(moves) >= 1


def test_move_updates_state():
    puzzle = """#####
#   #
# $ #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    moves = generate_moves(state, static)
    up_move = next((m for m in moves if m[0] == 'U'), None)
    assert up_move is not None

    new_state = up_move[1]
    assert new_state.player_pos == (2, 2)
    assert (2, 1) in new_state.boxes
    assert (2, 2) not in new_state.boxes


# --- Step 1.21: apply_move tests ---

def test_apply_move_up():
    puzzle = """#####
#   #
# $ #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    new_state = apply_move(state, 'U', static)
    assert new_state.player_pos == (2, 2)
    assert (2, 1) in new_state.boxes
    assert (2, 2) not in new_state.boxes


def test_apply_move_sequence():
    puzzle = """#####
#.  #
#   #
#$  #
#@  #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    state = apply_move(state, 'U', static)
    state = apply_move(state, 'U', static)

    assert (1, 1) in state.boxes
