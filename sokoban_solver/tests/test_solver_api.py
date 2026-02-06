from solver.astar import solve_puzzle


def test_api_success():
    puzzle = """####
#. #
#$ #
#@ #
####"""

    result = solve_puzzle(puzzle)

    assert result['success'] is True
    assert 'solution' in result
    assert 'stats' in result
    assert 'initial_state' in result
    assert 'player' in result['initial_state']
    assert 'boxes' in result['initial_state']
    assert 'goals' in result['initial_state']


def test_api_failure():
    puzzle = """####
#$ #
#  #
#@.#
####"""

    result = solve_puzzle(puzzle)

    assert result['success'] is False
    assert 'error' in result
    assert 'reason' in result


def test_api_invalid_puzzle():
    puzzle = """not a valid puzzle"""

    result = solve_puzzle(puzzle)

    assert result['success'] is False
    assert result['reason'] == 'invalid_puzzle'


def test_api_timeout():
    # 6 boxes puzzle with very short timeout
    puzzle = """##########
#        #
# $$$$$$ #
# ...... #
#@       #
##########"""

    result = solve_puzzle(puzzle, timeout=0.01)

    assert result['success'] is False
    assert result['reason'] == 'timeout'


def test_api_empty_puzzle():
    result = solve_puzzle("")

    assert result['success'] is False
    assert result['reason'] == 'invalid_puzzle'


def test_api_no_player():
    puzzle = """####
#$.#
####"""

    result = solve_puzzle(puzzle)

    assert result['success'] is False
    assert result['reason'] == 'invalid_puzzle'
