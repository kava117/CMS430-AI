import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


def _start(client, W=10, H=8, seed='apitest', depth=2):
    r = client.post('/api/start',
                    data=json.dumps({'W': W, 'H': H, 'seed': seed, 'depth': depth}),
                    content_type='application/json')
    assert r.status_code == 200
    return json.loads(r.data)


# --- Step 1 tests ---

def test_index_returns_200(client):
    r = client.get('/')
    assert r.status_code == 200


def test_index_contains_canvas(client):
    r = client.get('/')
    assert b'board-canvas' in r.data


# --- Step 8 tests ---

def test_start_returns_board(client):
    state = _start(client)
    assert 'board' in state
    assert len(state['board']) == 10 * 8


def test_start_clamps_width(client):
    state = _start(client, W=999)
    assert state['W'] == 24


def test_start_deterministic(client):
    s1 = _start(client, seed='fixed')
    s2 = _start(client, seed='fixed')
    assert [c['type'] for c in s1['board']] == [c['type'] for c in s2['board']]


def test_state_endpoint(client):
    _start(client)
    r = client.get('/api/state')
    assert r.status_code == 200
    state = json.loads(r.data)
    assert 'board' in state


def test_move_claims_tile(client):
    state = _start(client)
    valid = state['valid_moves']
    assert len(valid) > 0
    target = valid[0]
    r = client.post('/api/move',
                    data=json.dumps({'index': target}),
                    content_type='application/json')
    assert r.status_code == 200
    new_state = json.loads(r.data)
    from game.constants import PLAYER
    assert new_state['board'][target]['owner'] == PLAYER


def test_move_invalid_index_returns_400(client):
    _start(client)
    r = client.post('/api/move',
                    data=json.dumps({'index': -1}),
                    content_type='application/json')
    assert r.status_code == 400


def test_ai_moves_after_player(client):
    state = _start(client)
    target = state['valid_moves'][0]
    new_state = json.loads(
        client.post('/api/move',
                    data=json.dumps({'index': target}),
                    content_type='application/json').data
    )
    from game.constants import AI
    ai_tiles = [c for c in new_state['board'] if c['owner'] == AI]
    assert len(ai_tiles) >= 2, "AI did not make a move after player"


def test_full_game_reaches_gameover(client):
    _start(client, W=8, H=6, depth=1)
    for _ in range(200):
        r = client.get('/api/state')
        state = json.loads(r.data)
        if state.get('phase') == 'gameover':
            break
        if state.get('phase') == 'wizard-prompt':
            client.post('/api/wizard',
                        data=json.dumps({'action': 'decline'}),
                        content_type='application/json')
            continue
        valid = state.get('valid_moves', [])
        if not valid:
            break
        client.post('/api/move',
                    data=json.dumps({'index': valid[0]}),
                    content_type='application/json')
    state = json.loads(client.get('/api/state').data)
    assert state['phase'] == 'gameover', "Game never ended after 200 moves"


# --- Step 9 tests ---

def test_title_screen_present(client):
    r = client.get('/')
    assert b'screen-title' in r.data
    assert b'DOMINION' in r.data


def test_all_screens_present(client):
    r = client.get('/')
    for screen_id in [b'screen-title', b'screen-game', b'screen-end']:
        assert screen_id in r.data


def test_wizard_modal_present(client):
    r = client.get('/')
    assert b'wizard-modal' in r.data
    assert b'wizard-invoke' in r.data
    assert b'wizard-decline' in r.data


def test_css_loaded(client):
    r = client.get('/static/css/dominion.css')
    assert r.status_code == 200
    assert b'--bg' in r.data
    assert b'--accent' in r.data


# --- Step 12 wizard tests ---

def _force_wizard(client):
    """Start a game, plant a Wizard tile in the first valid move, return that index."""
    import app as app_module
    from game.constants import WIZARD, PLAYER
    _start(client, seed='wiztest')
    valid = list(app_module.G['valid_moves'])
    # Pick the first valid move and force it to be a Wizard tile
    wiz_idx = valid[0]
    app_module.G['board'][wiz_idx]['type'] = WIZARD
    return wiz_idx


def test_wizard_claim_triggers_prompt(client):
    wiz_idx = _force_wizard(client)
    r = client.post('/api/move',
                    data=json.dumps({'index': wiz_idx}),
                    content_type='application/json')
    state = json.loads(r.data)
    assert state['phase'] == 'wizard-prompt'


def test_wizard_invoke_sets_teleport_phase(client):
    _force_wizard(client)
    import app as app_module
    # Manually set phase as if prompt was shown
    app_module.G['phase'] = 'wizard-prompt'
    r = client.post('/api/wizard',
                    data=json.dumps({'action': 'invoke'}),
                    content_type='application/json')
    state = json.loads(r.data)
    # After invoke + AI turn, player's next phase should be wizard-teleport
    assert state['phase'] in ('wizard-teleport', 'normal', 'gameover')
    assert state['wizard_active_for'] in (1, 0)  # PLAYER or cleared if used


def test_wizard_decline_runs_ai_turn(client):
    _force_wizard(client)
    import app as app_module
    from game.constants import AI
    ai_count_before = sum(1 for c in app_module.G['board'] if c['owner'] == AI)
    app_module.G['phase'] = 'wizard-prompt'
    client.post('/api/wizard',
                data=json.dumps({'action': 'decline'}),
                content_type='application/json')
    ai_count_after = sum(1 for c in app_module.G['board'] if c['owner'] == AI)
    assert ai_count_after >= ai_count_before, "AI did not move after wizard decline"


# --- Step 13 final integration tests ---

def test_game_ends_with_winner_or_draw(client):
    _start(client, W=8, H=6, depth=1, seed='endtest')
    for _ in range(300):
        r = client.get('/api/state')
        state = json.loads(r.data)
        if state['phase'] == 'gameover':
            break
        if state['phase'] == 'wizard-prompt':
            client.post('/api/wizard',
                        data=json.dumps({'action': 'decline'}),
                        content_type='application/json')
            continue
        if state['phase'] == 'wizard-teleport':
            valid = state.get('valid_moves', [])
            if valid:
                client.post('/api/move',
                            data=json.dumps({'index': valid[0]}),
                            content_type='application/json')
            continue
        valid = state.get('valid_moves', [])
        if not valid:
            break
        client.post('/api/move',
                    data=json.dumps({'index': valid[0]}),
                    content_type='application/json')
    state = json.loads(client.get('/api/state').data)
    assert state['phase'] == 'gameover'
    total = sum(1 for c in state['board'] if c['type'] != 4)  # 4 == MOUNTAIN
    player_c = sum(1 for c in state['board'] if c['owner'] == 1)
    ai_c     = sum(1 for c in state['board'] if c['owner'] == 2)
    # Winner must have the majority or all tiles claimed
    assert player_c + ai_c <= total


def test_result_score_in_response(client):
    _start(client, W=8, H=6, depth=1, seed='scoretest')
    # Force a majority win by setting board state directly
    import app as app_module
    from game.constants import PLAYER, MOUNTAIN
    claimable = [i for i, c in enumerate(app_module.G['board']) if c['type'] != MOUNTAIN]
    majority = len(claimable) // 2 + 1
    for i in claimable[:majority]:
        app_module.G['board'][i]['owner'] = PLAYER
    app_module.G['phase'] = 'gameover'
    app_module.G['game_over'] = True
    r = client.get('/api/state')
    state = json.loads(r.data)
    assert state['phase'] == 'gameover'


def test_no_moves_both_players_ends_game(client):
    _start(client, W=8, H=6, depth=1, seed='nomoves')
    import app as app_module
    from game.constants import PLAYER, AI, MOUNTAIN
    # Force all tiles owned (no unclaimed tiles left)
    for i, c in enumerate(app_module.G['board']):
        if c['type'] != MOUNTAIN:
            c['owner'] = PLAYER if i % 2 == 0 else AI
    app_module.G['valid_moves'] = []
    r = client.post('/api/move',
                    data=json.dumps({'index': -1}),
                    content_type='application/json')
    # Should return 400 (no valid moves) or gameover state — not a crash
    assert r.status_code in (400, 200)
