from core.parser import parse_puzzle_string, extract_elements


def test_parse_simple_puzzle():
    puzzle = """####
#  #
####"""
    grid = parse_puzzle_string(puzzle)
    assert len(grid) == 3
    assert len(grid[0]) == 4
    assert grid[0][0] == '#'
    assert grid[1][1] == ' '


def test_parse_uneven_rows():
    puzzle = """####
#  ###
####"""
    grid = parse_puzzle_string(puzzle)
    assert all(len(row) == len(grid[0]) for row in grid)


def test_parse_strips_empty_lines():
    puzzle = """
####
#  #
####
"""
    grid = parse_puzzle_string(puzzle)
    assert len(grid) == 3


def test_extract_player():
    puzzle = """####
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    assert elements['player'] == (1, 1)


def test_extract_boxes():
    puzzle = """####
#$ #
#$ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    assert len(elements['boxes']) == 2
    assert (1, 1) in elements['boxes']
    assert (1, 2) in elements['boxes']


def test_extract_goals():
    puzzle = """####
#. #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    assert (1, 1) in elements['goals']


def test_extract_box_on_goal():
    puzzle = """####
#* #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    assert (1, 1) in elements['boxes']
    assert (1, 1) in elements['goals']


def test_extract_player_on_goal():
    puzzle = """####
#+ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    assert elements['player'] == (1, 1)
    assert (1, 1) in elements['goals']


def test_extract_walls():
    puzzle = """####
#  #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    assert (0, 0) in elements['walls']
    assert (1, 1) not in elements['walls']


def test_extract_dimensions():
    puzzle = """####
#  #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    assert elements['width'] == 4
    assert elements['height'] == 3
