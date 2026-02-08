import json
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web.app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# --- Step 2.1: Flask setup ---

def test_app_runs(client):
    response = client.get('/')
    assert response.status_code == 200


# --- Step 2.2: Puzzle list API ---

def test_get_puzzles(client):
    response = client.get('/api/puzzles')

    assert response.status_code == 200
    data = response.get_json()
    assert 'puzzles' in data
    assert len(data['puzzles']) > 0
    assert 'id' in data['puzzles'][0]
    assert 'name' in data['puzzles'][0]
    assert 'difficulty' in data['puzzles'][0]


# --- Step 2.3: Get single puzzle ---

def test_get_puzzle_valid(client):
    response = client.get('/api/puzzle/easy_1')

    assert response.status_code == 200
    data = response.get_json()
    assert 'id' in data
    assert 'puzzle' in data
    assert 'grid' in data
    assert data['id'] == 'easy_1'


def test_get_puzzle_invalid(client):
    response = client.get('/api/puzzle/nonexistent')
    assert response.status_code == 404


def test_get_puzzle_grid_format(client):
    response = client.get('/api/puzzle/easy_1')
    data = response.get_json()

    grid = data['grid']
    assert isinstance(grid, list)
    assert isinstance(grid[0], list)
    assert '#' in grid[0]


# --- Step 2.4: Solve API ---

def test_solve_valid_puzzle(client):
    puzzle = "####\n#. #\n#$ #\n#@ #\n####"

    response = client.post(
        '/api/solve',
        data=json.dumps({'puzzle': puzzle}),
        content_type='application/json',
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'solution' in data
    assert 'moves' in data
    assert 'length' in data
    assert 'stats' in data
    assert 'initial_state' in data


def test_solve_no_puzzle(client):
    response = client.post(
        '/api/solve',
        data=json.dumps({}),
        content_type='application/json',
    )
    assert response.status_code == 400


def test_solve_impossible_puzzle(client):
    puzzle = "####\n#$ #\n#  #\n#@.#\n####"

    response = client.post(
        '/api/solve',
        data=json.dumps({'puzzle': puzzle}),
        content_type='application/json',
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is False


# --- Step 2.5: HTML template ---

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Sokoban' in response.data


# --- Step 3.1: Validation API ---

def test_validate_valid_puzzle(client):
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', ' ', '#'],
        ['#', '$', ' ', '#'],
        ['#', '@', ' ', '#'],
        ['#', '#', '#', '#'],
    ]

    response = client.post(
        '/api/validate',
        data=json.dumps({'grid': grid}),
        content_type='application/json',
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] is True
    assert len(data['errors']) == 0


def test_validate_no_player(client):
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', ' ', '#'],
        ['#', '$', ' ', '#'],
        ['#', ' ', ' ', '#'],
        ['#', '#', '#', '#'],
    ]

    response = client.post(
        '/api/validate',
        data=json.dumps({'grid': grid}),
        content_type='application/json',
    )

    data = response.get_json()
    assert data['valid'] is False
    assert any('player' in e.lower() for e in data['errors'])


def test_validate_no_boxes(client):
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', ' ', '#'],
        ['#', ' ', ' ', '#'],
        ['#', '@', ' ', '#'],
        ['#', '#', '#', '#'],
    ]

    response = client.post(
        '/api/validate',
        data=json.dumps({'grid': grid}),
        content_type='application/json',
    )

    data = response.get_json()
    assert data['valid'] is False
    assert any('box' in e.lower() for e in data['errors'])


def test_validate_box_goal_mismatch(client):
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', '.', '#'],
        ['#', '$', ' ', '#'],
        ['#', '@', ' ', '#'],
        ['#', '#', '#', '#'],
    ]

    response = client.post(
        '/api/validate',
        data=json.dumps({'grid': grid}),
        content_type='application/json',
    )

    data = response.get_json()
    # Valid (has player, box, goal) but warning about mismatch
    assert data['valid'] is True
    assert len(data['warnings']) > 0


def test_validate_box_on_goal_counted(client):
    """A '*' counts as both a box and a goal."""
    grid = [
        ['#', '#', '#', '#'],
        ['#', '*', ' ', '#'],
        ['#', ' ', ' ', '#'],
        ['#', '@', ' ', '#'],
        ['#', '#', '#', '#'],
    ]

    response = client.post(
        '/api/validate',
        data=json.dumps({'grid': grid}),
        content_type='application/json',
    )

    data = response.get_json()
    assert data['valid'] is True
    assert len(data['warnings']) == 0
