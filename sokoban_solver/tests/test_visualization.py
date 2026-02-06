from visualization.terminal import state_to_string
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements


def test_state_to_string():
    puzzle = """####
#$.#
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    output = state_to_string(state, static)

    assert '#' in output
    assert '$' in output or '*' in output
    assert '@' in output or '+' in output


def test_state_to_string_box_on_goal():
    puzzle = """####
#* #
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    output = state_to_string(state, static)
    assert '*' in output


def test_state_to_string_player_on_goal():
    puzzle = """####
#$ #
#+.#
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    output = state_to_string(state, static)
    assert '+' in output


def test_state_to_string_roundtrip():
    """Rendering a parsed puzzle should reproduce the original."""
    puzzle = """####
#.$#
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    output = state_to_string(state, static)
    assert output == puzzle
