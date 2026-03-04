from flask import Flask, render_template, request, jsonify, session
from game.state import GameState
from game.mcts import MCTS, _DIFFICULTY

app = Flask(__name__)
app.secret_key = "uttt-secret-key-change-in-prod"


def _get_state() -> GameState | None:
    d = session.get("game_state")
    if d is None:
        return None
    return GameState.from_dict(d)


def _save_state(gs: GameState):
    session["game_state"] = gs.to_dict()


def _make_mcts(difficulty: str) -> MCTS:
    iterations = _DIFFICULTY.get(difficulty, _DIFFICULTY["easy"])
    return MCTS(iterations=iterations)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/new_game", methods=["POST"])
def new_game():
    data = request.get_json(force=True)
    difficulty = data.get("difficulty", "easy").lower()
    human_plays = data.get("human_plays", "X").upper()

    gs = GameState()
    ai_move = None

    if human_plays == "O":
        # AI is X — make first move immediately
        mcts = _make_mcts(difficulty)
        move = mcts.search(gs)
        gs = gs.apply_move(*move)
        ai_move = list(move)

    session["difficulty"] = difficulty
    session["human_player"] = 1 if human_plays == "X" else 2
    _save_state(gs)

    return jsonify({"state": gs.to_dict(), "ai_move": ai_move})


@app.route("/api/move", methods=["POST"])
def move():
    gs = _get_state()
    if gs is None:
        return jsonify({"error": "No active game", "state": None, "ai_move": None}), 400

    data = request.get_json(force=True)
    board_index = data.get("board_index")
    cell_index = data.get("cell_index")

    if board_index is None or cell_index is None:
        return jsonify({"error": "Missing board_index or cell_index",
                        "state": gs.to_dict(), "ai_move": None}), 400

    legal = gs.get_legal_moves()
    if (board_index, cell_index) not in legal:
        return jsonify({"error": "Illegal move",
                        "state": gs.to_dict(), "ai_move": None})

    gs = gs.apply_move(board_index, cell_index)
    ai_move = None

    if not gs.is_terminal():
        difficulty = session.get("difficulty", "easy")
        mcts = _make_mcts(difficulty)
        move_chosen = mcts.search(gs)
        gs = gs.apply_move(*move_chosen)
        ai_move = list(move_chosen)

    _save_state(gs)
    return jsonify({"state": gs.to_dict(), "ai_move": ai_move, "error": None})


@app.route("/api/state", methods=["GET"])
def get_state():
    gs = _get_state()
    if gs is None:
        return jsonify({"error": "No active game"}), 404
    return jsonify(gs.to_dict())


if __name__ == "__main__":
    app.run(debug=True)
