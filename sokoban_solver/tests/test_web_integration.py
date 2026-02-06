"""End-to-end integration tests for the web API."""

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


def test_full_solve_flow(client):
    """Complete flow: list puzzles -> get puzzle -> solve it."""
    # Get puzzle list
    puzzles = client.get('/api/puzzles').get_json()['puzzles']
    assert len(puzzles) > 0

    # Get first puzzle
    puzzle_id = puzzles[0]['id']
    puzzle_data = client.get(f'/api/puzzle/{puzzle_id}').get_json()
    assert 'puzzle' in puzzle_data

    # Solve it
    response = client.post(
        '/api/solve',
        data=json.dumps({'puzzle': puzzle_data['puzzle']}),
        content_type='application/json',
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result['success'] is True
    assert len(result['moves']) == result['length']


def test_solve_all_presets(client):
    """Verify all preset puzzles are solvable."""
    puzzles = client.get('/api/puzzles').get_json()['puzzles']

    for puzzle_meta in puzzles:
        puzzle_data = client.get(f'/api/puzzle/{puzzle_meta["id"]}').get_json()

        response = client.post(
            '/api/solve',
            data=json.dumps({'puzzle': puzzle_data['puzzle']}),
            content_type='application/json',
        )

        result = response.get_json()
        assert result['success'] is True, (
            f"Preset puzzle '{puzzle_meta['id']}' failed to solve: {result.get('error')}"
        )
        assert result['length'] > 0 or result['solution'] == ''


def test_solve_response_has_initial_state(client):
    """Verify the solve response includes initial state for frontend."""
    puzzle = "####\n#. #\n#$ #\n#@ #\n####"

    response = client.post(
        '/api/solve',
        data=json.dumps({'puzzle': puzzle}),
        content_type='application/json',
    )

    data = response.get_json()
    assert data['success'] is True
    assert 'initial_state' in data
    assert 'player' in data['initial_state']
    assert 'boxes' in data['initial_state']
    assert 'goals' in data['initial_state']
    assert len(data['initial_state']['player']) == 2
    assert len(data['initial_state']['boxes']) > 0
    assert len(data['initial_state']['goals']) > 0


def test_solve_with_custom_timeout(client):
    """Verify timeout parameter is respected."""
    puzzle = "####\n#. #\n#$ #\n#@ #\n####"

    response = client.post(
        '/api/solve',
        data=json.dumps({'puzzle': puzzle, 'timeout': 5}),
        content_type='application/json',
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
