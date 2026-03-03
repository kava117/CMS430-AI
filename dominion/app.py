import time
from flask import Flask, render_template, request, jsonify

from game.constants import NONE, PLAYER, AI, MOUNTAIN
from game.board import generate_board
from game.fog import compute_fog
from game.moves import compute_valid_moves
from game.claim import claim_tile, check_win_condition
from game.ai import minimax_root, wizard_teleport_decision

app = Flask(__name__)
app.secret_key = 'dominion-dev'

# Module-level game state (single-user dev mode)
G: dict = {}


MAX_TURNS = 150  # Force game end after this many player turns to prevent infinite loops


def state_snapshot(G: dict) -> dict:
    """Convert G to a JSON-serialisable dict."""
    return {
        'W': G.get('W', 0),
        'H': G.get('H', 0),
        'board': G.get('board', []),
        'fog': sorted(G.get('fog', set())),
        'turn': G.get('turn', PLAYER),
        'phase': G.get('phase', 'normal'),
        'wizard_active_for': G.get('wizard_active_for', NONE),
        'valid_moves': sorted(G.get('valid_moves', set())),
        'game_over': G.get('game_over', False),
        'depth': G.get('depth', 2),
        'seed': G.get('seed', ''),
        'log': G.get('log', []),
    }


def end_game_by_score(G: dict):
    """Force game over by current score (used for stalemate/max-turn detection)."""
    G['game_over'] = True
    G['phase'] = 'gameover'
    G['valid_moves'] = []


def run_ai_turn(G: dict):
    """Run the AI's turn: pick best move, claim it, handle wizard if needed."""
    ai_moves = compute_valid_moves(G, AI)
    if not ai_moves:
        G['log'].append("AI has no moves — skipping.")
        return

    depth = G.get('depth', 2)

    # Handle wizard teleport turn for AI
    if G.get('wizard_active_for') == AI:
        from game.ai import wizard_teleport_decision
        tele = wizard_teleport_decision(G)
        if tele is not None:
            claim_tile(G, tele, AI)
            G['wizard_active_for'] = NONE
        else:
            G['wizard_active_for'] = NONE
        G['fog'] = compute_fog(G)
        return

    ai_idx = minimax_root(G, depth)
    if ai_idx < 0:
        G['log'].append("AI has no moves — skipping.")
        return

    was_wizard = claim_tile(G, ai_idx, AI)
    G['fog'] = compute_fog(G)

    if was_wizard:
        board = G['board']
        if not board[ai_idx]['used']:
            tele = wizard_teleport_decision(G)
            if tele is not None:
                G['wizard_active_for'] = AI
                board[ai_idx]['used'] = True
                # Run wizard teleport immediately
                claim_tile(G, tele, AI)
                G['wizard_active_for'] = NONE
                G['fog'] = compute_fog(G)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def api_start():
    global G
    data = request.get_json() or {}

    W = max(8, min(24, int(data.get('W', 14))))
    H = max(6, min(18, int(data.get('H', 10))))
    seed = str(data.get('seed', '')).strip() or str(time.time_ns())
    depth_map = {1: 1, 2: 2, 3: 3, 4: 4}
    depth = depth_map.get(int(data.get('depth', 2)), 2)

    board = generate_board(seed, W, H)
    G = {
        'W': W,
        'H': H,
        'board': board,
        'fog': set(),
        'turn': PLAYER,
        'phase': 'normal',
        'wizard_active_for': NONE,
        'valid_moves': set(),
        'game_over': False,
        'depth': depth,
        'seed': seed,
        'log': [],
        'turn_count': 0,
    }
    G['fog'] = compute_fog(G)
    G['valid_moves'] = compute_valid_moves(G, PLAYER)

    return jsonify(state_snapshot(G))


@app.route('/api/state', methods=['GET'])
def api_state():
    return jsonify(state_snapshot(G))


@app.route('/api/move', methods=['POST'])
def api_move():
    global G
    data = request.get_json() or {}
    index = data.get('index', -1)

    valid = G.get('valid_moves', set())
    # valid_moves may be a set or list
    if index not in (valid if isinstance(valid, set) else set(valid)):
        return jsonify({'error': 'Invalid move', 'index': index}), 400

    # Player claims tile
    G['turn_count'] = G.get('turn_count', 0) + 1
    was_wizard = claim_tile(G, index, PLAYER)
    G['fog'] = compute_fog(G)

    if was_wizard:
        G['phase'] = 'wizard-prompt'
        G['valid_moves'] = []
        return jsonify(state_snapshot(G))

    # Check win condition after player move
    winner = check_win_condition(G)
    if winner is not None:
        end_game_by_score(G)
        return jsonify(state_snapshot(G))

    # Max turns stalemate detection
    if G['turn_count'] >= MAX_TURNS:
        G['log'].append(f"Stalemate after {MAX_TURNS} turns.")
        end_game_by_score(G)
        return jsonify(state_snapshot(G))

    # AI turn
    run_ai_turn(G)
    G['fog'] = compute_fog(G)

    # Check win condition after AI move
    winner = check_win_condition(G)
    if winner is not None:
        end_game_by_score(G)
        return jsonify(state_snapshot(G))

    # Compute next player valid moves
    player_moves = compute_valid_moves(G, PLAYER)
    if not player_moves:
        # Check if AI also has no moves
        ai_moves = compute_valid_moves(G, AI)
        if not ai_moves:
            winner = check_win_condition(G)
            G['game_over'] = True
            G['phase'] = 'gameover'
            G['valid_moves'] = []
            return jsonify(state_snapshot(G))
        # AI gets consecutive turns
        while not player_moves:
            run_ai_turn(G)
            G['fog'] = compute_fog(G)
            winner = check_win_condition(G)
            if winner is not None:
                G['game_over'] = True
                G['phase'] = 'gameover'
                G['valid_moves'] = []
                return jsonify(state_snapshot(G))
            player_moves = compute_valid_moves(G, PLAYER)
            if not compute_valid_moves(G, AI):
                break

    G['valid_moves'] = player_moves
    G['phase'] = 'normal'

    return jsonify(state_snapshot(G))


@app.route('/api/wizard', methods=['POST'])
def api_wizard():
    global G
    data = request.get_json() or {}
    action = data.get('action', 'decline')

    if action == 'invoke':
        # Find the wizard tile the player just claimed
        board = G['board']
        from game.constants import WIZARD
        wiz_idx = next(
            (i for i, c in enumerate(board)
             if c['type'] == WIZARD and c['owner'] == PLAYER and not c['used']),
            None
        )
        if wiz_idx is not None:
            board[wiz_idx]['used'] = True
        G['wizard_active_for'] = PLAYER

        # Run AI turn first
        run_ai_turn(G)
        G['fog'] = compute_fog(G)

        winner = check_win_condition(G)
        if winner is not None:
            G['game_over'] = True
            G['phase'] = 'gameover'
            G['valid_moves'] = []
            return jsonify(state_snapshot(G))

        # Player gets wizard teleport next
        G['phase'] = 'wizard-teleport'
        G['valid_moves'] = compute_valid_moves(G, PLAYER)

    else:  # decline
        G['wizard_active_for'] = NONE

        run_ai_turn(G)
        G['fog'] = compute_fog(G)

        winner = check_win_condition(G)
        if winner is not None:
            G['game_over'] = True
            G['phase'] = 'gameover'
            G['valid_moves'] = []
            return jsonify(state_snapshot(G))

        G['phase'] = 'normal'
        G['valid_moves'] = compute_valid_moves(G, PLAYER)

    return jsonify(state_snapshot(G))


if __name__ == '__main__':
    app.run(debug=True, port=5000)
