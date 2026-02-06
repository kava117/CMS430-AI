from solver.astar import solve
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements
from solver.deadlock import compute_static_deadlocks


def _setup(puzzle):
    """Helper to parse a puzzle and return (initial_state, puzzle_static)."""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    static.deadlock_squares = compute_static_deadlocks(
        static.walls, static.goals, static.width, static.height
    )
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))
    return initial, static


# --- Step 1.10: Basic A* ---

def test_solve_trivial_one_push():
    puzzle = """####
#. #
#$ #
#@ #
####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True
    assert result['solution'] == 'U'


def test_solve_trivial_two_pushes():
    puzzle = """#####
#.  #
#   #
#$  #
#@  #
#####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True
    assert len(result['solution']) == 2
    assert result['solution'] == 'UU'


def test_solve_already_solved():
    puzzle = """####
#* #
#@ #
####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True
    assert result['solution'] == ''


# --- Step 1.11: No solution ---

def test_solve_impossible_corner():
    puzzle = """####
#$ #
#  #
#@.#
####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is False
    assert 'states_explored' in result['stats']


def test_solve_returns_stats():
    puzzle = """####
#. #
#$ #
#@ #
####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert 'stats' in result
    assert 'states_explored' in result['stats']
    assert result['stats']['states_explored'] >= 1


# --- Step 1.13: Distance heuristic integration ---

def test_solve_uses_distance_heuristic():
    # Box must go around wall to reach goal
    puzzle = """######
#.   #
# ## #
#  $ #
#  @ #
######"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True


# --- Step 1.15: Static deadlock pruning ---

def test_solver_prunes_corner_deadlock():
    puzzle = """#####
#   #
# $.#
# @ #
#####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True


# --- Step 1.19: Full deadlock integration ---

def test_solver_prunes_2x2_deadlock():
    puzzle = """######
#    #
# $$ #
# .. #
# @  #
######"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True


def test_solver_with_deadlock_detection_faster():
    puzzle = """#######
#     #
# $$$ #
# ... #
#@    #
#######"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True
    assert result['stats']['states_explored'] < 10000
