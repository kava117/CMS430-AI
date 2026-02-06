import time

from solver.astar import solve
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements
from solver.deadlock import compute_static_deadlocks


def _setup(puzzle):
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    static.deadlock_squares = compute_static_deadlocks(
        static.walls, static.goals, static.width, static.height
    )
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))
    return initial, static


def test_three_box_puzzle():
    puzzle = """########
#      #
# $$$  #
# ...  #
#@     #
########"""
    initial, static = _setup(puzzle)

    start = time.time()
    result = solve(initial, static)
    elapsed = time.time() - start

    assert result['success'] is True
    assert elapsed < 5.0


def test_microban_level_1():
    puzzle = """####
# .#
#  ###
#*@  #
#  $ #
#  ###
####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True
    assert len(result['solution']) <= 10


def test_solver_returns_optimal():
    puzzle = """#####
#   #
# $.#
#   #
# @ #
#####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True
    # Box at (2,2), goal at (3,2). Optimal: push right = 1 push.
    assert len(result['solution']) == 1


def test_lateral_push():
    """Box must be pushed sideways then down."""
    puzzle = """######
# @  #
# $  #
#    #
# .  #
######"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True
    assert len(result['solution']) == 2  # DD


def test_multi_direction_puzzle():
    """Requires pushes in multiple directions."""
    puzzle = """#####
# . #
#   #
# $ #
#  @#
#####"""
    initial, static = _setup(puzzle)
    result = solve(initial, static)

    assert result['success'] is True
