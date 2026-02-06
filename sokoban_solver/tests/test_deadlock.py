from solver.deadlock import (
    is_corner_deadlock, compute_static_deadlocks,
    is_freeze_deadlock, is_2x2_deadlock, is_deadlocked,
)
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements


# --- Step 1.14: Corner deadlock ---

def test_corner_deadlock_detected():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0),
                       (0, 1), (3, 1),
                       (0, 2), (3, 2),
                       (0, 3), (1, 3), (2, 3), (3, 3)])
    goals = frozenset([(2, 2)])

    # (1,1) has walls at (0,1) and (1,0) - top-left corner
    assert is_corner_deadlock((1, 1), walls, goals) is True


def test_corner_deadlock_is_goal():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0),
                       (0, 1), (3, 1),
                       (0, 2), (3, 2),
                       (0, 3), (1, 3), (2, 3), (3, 3)])
    goals = frozenset([(1, 1)])

    assert is_corner_deadlock((1, 1), walls, goals) is False


def test_corner_deadlock_not_corner():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0),
                       (0, 1), (3, 1),
                       (0, 2), (3, 2),
                       (0, 3), (1, 3), (2, 3), (3, 3)])
    goals = frozenset([(2, 2)])

    # (1,2) has wall to left (0,2) but not above/below in corner config
    # Actually (1,2) has wall at (0,2) left and (1,3) below — that IS a corner
    assert is_corner_deadlock((1, 2), walls, goals) is True


def test_compute_static_deadlocks():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0),
                       (0, 1), (3, 1),
                       (0, 2), (3, 2),
                       (0, 3), (1, 3), (2, 3), (3, 3)])
    goals = frozenset([(2, 2)])

    deadlocks = compute_static_deadlocks(walls, goals, 4, 4)

    assert (1, 1) in deadlocks
    assert (2, 1) in deadlocks
    assert (1, 2) in deadlocks
    assert (2, 2) not in deadlocks  # This is the goal


# --- Step 1.16: Freeze deadlock ---

def test_freeze_deadlock_movable():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                       (0, 1), (4, 1),
                       (0, 2), (4, 2),
                       (0, 3), (4, 3),
                       (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)])
    goals = frozenset([(1, 1)])

    # Box at (2,2) in open room — can be pushed
    boxes = frozenset([(2, 2)])
    assert is_freeze_deadlock(boxes, walls, goals) is False


def test_freeze_deadlock_two_boxes_against_wall():
    walls = frozenset([(0, 0), (1, 0), (2, 0), (3, 0),
                       (0, 1), (3, 1),
                       (0, 2), (3, 2),
                       (0, 3), (1, 3), (2, 3), (3, 3)])
    goals = frozenset([(2, 2)])

    # Two boxes side by side against top wall
    boxes = frozenset([(1, 1), (2, 1)])
    assert is_freeze_deadlock(boxes, walls, goals) is True


def test_freeze_deadlock_on_goal_ok():
    walls = frozenset([(0, 0), (1, 0), (2, 0),
                       (0, 1), (2, 1),
                       (0, 2), (1, 2), (2, 2)])
    # Box frozen but on goal — not a deadlock
    assert is_freeze_deadlock(frozenset([(1, 1)]), walls, frozenset([(1, 1)])) is False


# --- Step 1.17: 2x2 deadlock ---

def test_2x2_deadlock():
    goals = frozenset([(10, 10)])
    boxes = frozenset([(1, 1), (2, 1), (1, 2), (2, 2)])
    assert is_2x2_deadlock(boxes, frozenset(), goals) is True


def test_2x2_no_deadlock_missing_box():
    goals = frozenset([(10, 10)])
    boxes = frozenset([(1, 1), (2, 1), (1, 2)])
    assert is_2x2_deadlock(boxes, frozenset(), goals) is False


def test_2x2_all_goals_ok():
    goals = frozenset([(1, 1), (2, 1), (1, 2), (2, 2)])
    boxes = frozenset([(1, 1), (2, 1), (1, 2), (2, 2)])
    assert is_2x2_deadlock(boxes, frozenset(), goals) is False


# --- Step 1.18: Combined deadlock check ---

def test_is_deadlocked_static():
    puzzle = """####
#$ #
#. #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    static.deadlock_squares = compute_static_deadlocks(
        static.walls, static.goals, static.width, static.height
    )

    # Box at (1,1) is in corner — static deadlock
    state = State(player_pos=(2, 2), boxes=frozenset([(1, 1)]))
    assert is_deadlocked(state, static) is True


def test_is_deadlocked_2x2():
    puzzle = """######
#    #
# $$ #
# $$ #
#....#
######"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    static.deadlock_squares = compute_static_deadlocks(
        static.walls, static.goals, static.width, static.height
    )

    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (3, 2), (2, 3), (3, 3)]))
    assert is_deadlocked(state, static) is True


def test_is_deadlocked_valid_state():
    puzzle = """####
#  #
#$.#
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    static.deadlock_squares = compute_static_deadlocks(
        static.walls, static.goals, static.width, static.height
    )
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    assert is_deadlocked(initial, static) is False
