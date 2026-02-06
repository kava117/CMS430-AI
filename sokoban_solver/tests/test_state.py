from core.state import State, PuzzleStatic, is_goal_state
from core.parser import parse_puzzle_string, extract_elements


# --- Step 1.4: State tests ---

def test_state_creation():
    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (3, 3)]))
    assert state.player_pos == (1, 1)
    assert len(state.boxes) == 2


def test_state_hashable():
    state1 = State(player_pos=(1, 1), boxes=frozenset([(2, 2)]))
    state2 = State(player_pos=(1, 1), boxes=frozenset([(2, 2)]))

    assert hash(state1) == hash(state2)

    state_set = {state1}
    assert state2 in state_set


def test_state_equality():
    state1 = State(player_pos=(1, 1), boxes=frozenset([(2, 2)]))
    state2 = State(player_pos=(1, 1), boxes=frozenset([(2, 2)]))
    state3 = State(player_pos=(1, 2), boxes=frozenset([(2, 2)]))

    assert state1 == state2
    assert state1 != state3


def test_state_immutable_boxes():
    boxes = frozenset([(2, 2), (3, 3)])
    state = State(player_pos=(1, 1), boxes=boxes)
    assert isinstance(state.boxes, frozenset)


# --- Step 1.5: PuzzleStatic tests ---

def test_puzzle_static_creation():
    puzzle = """####
#.$#
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)

    assert static.width == 4
    assert static.height == 3
    assert (1, 1) in static.goals
    assert (0, 0) in static.walls


def test_puzzle_static_walls_frozenset():
    puzzle = """####
#  #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)

    assert isinstance(static.walls, frozenset)
    assert isinstance(static.goals, frozenset)


# --- Step 1.8: Goal check tests ---

def test_goal_state_achieved():
    goals = frozenset([(2, 2), (3, 3)])
    static = PuzzleStatic(walls=frozenset(), goals=goals, width=5, height=5)

    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (3, 3)]))
    assert is_goal_state(state, static) is True


def test_goal_state_not_achieved():
    goals = frozenset([(2, 2), (3, 3)])
    static = PuzzleStatic(walls=frozenset(), goals=goals, width=5, height=5)

    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (4, 4)]))
    assert is_goal_state(state, static) is False


def test_goal_state_partial():
    goals = frozenset([(2, 2), (3, 3)])
    static = PuzzleStatic(walls=frozenset(), goals=goals, width=5, height=5)

    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (1, 1)]))
    assert is_goal_state(state, static) is False
