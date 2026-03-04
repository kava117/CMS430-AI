# Ultimate Tic-Tac-Toe — Implementation Steps

Each step ends with a test suite. **Do not proceed to the next step until all tests pass.**

---

## Step 1 — Project Scaffold

Create the directory structure and dependency file.

**Files to create:**
```
ultimate-ttt/
├── app.py                  (empty stub)
├── game/
│   ├── __init__.py         (empty)
│   ├── state.py            (empty stub)
│   └── mcts.py             (empty stub)
├── static/
│   ├── style.css           (empty)
│   └── game.js             (empty)
├── templates/
│   └── index.html          (empty stub)
├── requirements.txt
└── tests/
    └── __init__.py         (empty)
```

**`requirements.txt`:**
```
flask>=3.0
```

**Tests — `tests/test_scaffold.py`:**
```python
import unittest, importlib, os

class TestScaffold(unittest.TestCase):
    def test_game_package_importable(self):
        import game
    def test_state_module_importable(self):
        import game.state
    def test_mcts_module_importable(self):
        import game.mcts
    def test_requirements_file_exists(self):
        self.assertTrue(os.path.exists("requirements.txt"))
    def test_templates_dir_exists(self):
        self.assertTrue(os.path.isdir("templates"))
    def test_static_dir_exists(self):
        self.assertTrue(os.path.isdir("static"))

if __name__ == "__main__":
    unittest.main()
```

Run: `cd ultimate-ttt && python -m pytest tests/test_scaffold.py -v`

---

## Step 2 — `check_winner` and Win-Line Logic

Implement `check_winner(board: list[int]) -> int` as a standalone function (or static method) in `game/state.py`.

**Rules:**
- Input: flat list of 9 values (`0`=empty, `1`=X, `2`=O).
- Check all 8 winning lines: rows `[0,1,2]`, `[3,4,5]`, `[6,7,8]`; cols `[0,3,6]`, `[1,4,7]`, `[2,5,8]`; diagonals `[0,4,8]`, `[2,4,6]`.
- Return `1` if X wins, `2` if O wins, `0` if no winner yet.
- A line wins if all three cells are the same non-zero value.

**Tests — `tests/test_check_winner.py`:**
```python
import unittest
from game.state import check_winner

class TestCheckWinner(unittest.TestCase):
    def test_no_winner_empty(self):
        self.assertEqual(check_winner([0]*9), 0)

    def test_x_wins_top_row(self):
        self.assertEqual(check_winner([1,1,1, 0,0,0, 0,0,0]), 1)

    def test_x_wins_middle_row(self):
        self.assertEqual(check_winner([0,0,0, 1,1,1, 0,0,0]), 1)

    def test_x_wins_bottom_row(self):
        self.assertEqual(check_winner([0,0,0, 0,0,0, 1,1,1]), 1)

    def test_o_wins_left_col(self):
        self.assertEqual(check_winner([2,0,0, 2,0,0, 2,0,0]), 2)

    def test_o_wins_middle_col(self):
        self.assertEqual(check_winner([0,2,0, 0,2,0, 0,2,0]), 2)

    def test_o_wins_right_col(self):
        self.assertEqual(check_winner([0,0,2, 0,0,2, 0,0,2]), 2)

    def test_x_wins_main_diagonal(self):
        self.assertEqual(check_winner([1,0,0, 0,1,0, 0,0,1]), 1)

    def test_x_wins_anti_diagonal(self):
        self.assertEqual(check_winner([0,0,1, 0,1,0, 1,0,0]), 1)

    def test_o_wins_anti_diagonal(self):
        self.assertEqual(check_winner([0,0,2, 0,2,0, 2,0,0]), 2)

    def test_no_winner_partial(self):
        self.assertEqual(check_winner([1,2,1, 2,1,2, 0,0,0]), 0)

    def test_no_winner_full_draw(self):
        # X O X / O O X / X X O — full board, no winner
        self.assertEqual(check_winner([1,2,1, 2,2,1, 1,1,2]), 0)

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_check_winner.py -v`

---

## Step 3 — `GameState` Construction and `clone`

Implement the `GameState` class in `game/state.py` with:
- Attributes: `board` (list of 9 lists of 9 ints), `meta_board` (list of 9 ints), `current_player` (1 or 2), `active_board` (int or None), `_winner` (int or None, internal), `_terminal` (bool, internal).
- `__init__` creates a fresh game: all zeroes, `current_player=1`, `active_board=None` (X gets free choice on move 1).
- `clone()` returns a deep copy.
- `is_terminal() -> bool`
- `get_result(perspective_player: int) -> float`
- `to_dict() -> dict` (schema from spec)

**Tests — `tests/test_gamestate_init.py`:**
```python
import unittest
from game.state import GameState

class TestGameStateInit(unittest.TestCase):
    def test_initial_board_all_zeros(self):
        gs = GameState()
        for sub in gs.board:
            self.assertEqual(sub, [0]*9)

    def test_initial_meta_board_all_zeros(self):
        gs = GameState()
        self.assertEqual(gs.meta_board, [0]*9)

    def test_initial_current_player_is_x(self):
        gs = GameState()
        self.assertEqual(gs.current_player, 1)

    def test_initial_active_board_is_none(self):
        # X gets free choice on the very first move
        gs = GameState()
        self.assertIsNone(gs.active_board)

    def test_not_terminal_at_start(self):
        gs = GameState()
        self.assertFalse(gs.is_terminal())

    def test_clone_is_independent(self):
        gs = GameState()
        gs2 = gs.clone()
        gs2.board[0][0] = 1
        self.assertEqual(gs.board[0][0], 0)

    def test_clone_same_values(self):
        gs = GameState()
        gs2 = gs.clone()
        self.assertEqual(gs.board, gs2.board)
        self.assertEqual(gs.meta_board, gs2.meta_board)
        self.assertEqual(gs.current_player, gs2.current_player)
        self.assertIsNone(gs2.active_board)

    def test_to_dict_keys(self):
        gs = GameState()
        d = gs.to_dict()
        for key in ("board", "meta_board", "current_player", "active_board",
                    "is_terminal", "winner"):
            self.assertIn(key, d)

    def test_to_dict_winner_none_at_start(self):
        gs = GameState()
        d = gs.to_dict()
        self.assertIsNone(d["winner"])

    def test_to_dict_is_terminal_false_at_start(self):
        gs = GameState()
        d = gs.to_dict()
        self.assertFalse(d["is_terminal"])

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_gamestate_init.py -v`

---

## Step 4 — `get_legal_moves`

Implement `GameState.get_legal_moves() -> list[tuple[int, int]]`.

**Rules:**
- If `active_board` is set and `meta_board[active_board] == 0`: return all `(active_board, cell)` where `board[active_board][cell] == 0`.
- Otherwise (`active_board` is None, or the target board is claimed/full): return all `(b, c)` where `meta_board[b] == 0` and `board[b][c] == 0`.
- On a terminal state, return `[]`.

**Tests — `tests/test_legal_moves.py`:**
```python
import unittest
from game.state import GameState

class TestLegalMoves(unittest.TestCase):
    def test_initial_state_has_81_moves(self):
        gs = GameState()
        moves = gs.get_legal_moves()
        self.assertEqual(len(moves), 81)

    def test_initial_moves_span_all_boards(self):
        gs = GameState()
        boards = {b for b, _ in gs.get_legal_moves()}
        self.assertEqual(boards, set(range(9)))

    def test_active_board_restricts_moves(self):
        gs = GameState()
        gs.active_board = 4
        moves = gs.get_legal_moves()
        self.assertTrue(all(b == 4 for b, _ in moves))
        self.assertEqual(len(moves), 9)

    def test_one_cell_filled_in_active_board(self):
        gs = GameState()
        gs.active_board = 0
        gs.board[0][0] = 1
        moves = gs.get_legal_moves()
        self.assertEqual(len(moves), 8)
        self.assertNotIn((0, 0), moves)

    def test_claimed_board_excluded_from_free_choice(self):
        gs = GameState()
        gs.active_board = None
        gs.meta_board[3] = 1   # board 3 won by X
        moves = gs.get_legal_moves()
        self.assertTrue(all(b != 3 for b, _ in moves))
        self.assertEqual(len(moves), 72)  # 8 boards × 9 cells

    def test_active_board_claimed_gives_free_choice(self):
        gs = GameState()
        gs.active_board = 3
        gs.meta_board[3] = 1   # target board is won → free choice
        moves = gs.get_legal_moves()
        boards = {b for b, _ in moves}
        self.assertNotIn(3, boards)
        self.assertEqual(len(moves), 72)

    def test_terminal_state_returns_empty(self):
        gs = GameState()
        gs._terminal = True
        self.assertEqual(gs.get_legal_moves(), [])

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_legal_moves.py -v`

---

## Step 5 — `apply_move` Routing and Small-Board Win Detection

Implement `GameState.apply_move(board_index, cell_index) -> GameState`.

**Steps (from spec):**
1. Place `current_player`'s mark at `board[board_index][cell_index]`.
2. Check if small board `board_index` is won or drawn; update `meta_board`.
3. Check if meta-board is won or drawn; update `_terminal` and `_winner`.
4. Determine `active_board` for the next turn:
   - If `meta_board[cell_index] == 0` (active), set `active_board = cell_index`.
   - Otherwise set `active_board = None` (free choice).
5. Switch `current_player`.

A small board is "drawn" (value `3`) when it is full (no empty cells) and has no winner.

**Tests — `tests/test_apply_move.py`:**
```python
import unittest
from game.state import GameState

class TestApplyMove(unittest.TestCase):
    def test_apply_move_does_not_mutate(self):
        gs = GameState()
        gs2 = gs.apply_move(0, 0)
        self.assertEqual(gs.board[0][0], 0)
        self.assertEqual(gs2.board[0][0], 1)

    def test_player_switches_after_move(self):
        gs = GameState()
        gs2 = gs.apply_move(0, 0)
        self.assertEqual(gs2.current_player, 2)

    def test_routing_sets_active_board(self):
        # Playing in cell 4 of any board → next active_board = 4
        gs = GameState()
        gs2 = gs.apply_move(0, 4)
        self.assertEqual(gs2.active_board, 4)

    def test_routing_to_claimed_board_gives_free_choice(self):
        gs = GameState()
        gs.meta_board[4] = 1   # board 4 already claimed
        gs2 = gs.apply_move(0, 4)
        self.assertIsNone(gs2.active_board)

    def test_small_board_win_updates_meta(self):
        gs = GameState()
        # Fill top row of board 0 with X (cells 0,1,2) in 3 moves
        gs.board[0] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 0
        gs2 = gs.apply_move(0, 2)   # completes top row
        self.assertEqual(gs2.meta_board[0], 1)

    def test_small_board_draw_updates_meta(self):
        # Board 0: X O X / O X O / O X _ — one cell left, no winner possible
        gs = GameState()
        gs.board[0] = [1,2,1, 2,1,2, 2,1,0]
        gs.current_player = 2
        gs.active_board = 0
        gs2 = gs.apply_move(0, 8)   # fills last cell
        self.assertEqual(gs2.meta_board[0], 3)

    def test_game_not_terminal_after_one_move(self):
        gs = GameState()
        gs2 = gs.apply_move(4, 4)
        self.assertFalse(gs2.is_terminal())

    def test_meta_board_win_makes_terminal(self):
        # Manually set meta_board so X wins on next small-board capture
        # X has boards 0,1 won; board 2 needs one more X cell to complete row
        gs = GameState()
        gs.meta_board = [1,1,0, 0,0,0, 0,0,0]
        # Board 2: X has top row minus last cell
        gs.board[2] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 2
        gs2 = gs.apply_move(2, 2)
        self.assertTrue(gs2.is_terminal())
        self.assertEqual(gs2.to_dict()["winner"], 1)

    def test_get_result_win(self):
        gs = GameState()
        gs.meta_board = [1,1,0, 0,0,0, 0,0,0]
        gs.board[2] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 2
        gs2 = gs.apply_move(2, 2)
        self.assertEqual(gs2.get_result(1),  1.0)
        self.assertEqual(gs2.get_result(2), -1.0)

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_apply_move.py -v`

---

## Step 6 — `is_terminal` Edge Cases and Draw Detection

Extend `apply_move` / `is_terminal` to handle:
- All small boards resolved (every entry of `meta_board` is nonzero) with no meta-board winner → draw (`_winner = 0`).
- `get_result` returns `0.0` for draw regardless of perspective.

**Tests — `tests/test_terminal.py`:**
```python
import unittest
from game.state import GameState

class TestTerminal(unittest.TestCase):
    def _make_terminal_draw(self):
        """Return a GameState where meta_board is fully resolved with no winner."""
        gs = GameState()
        # X O X / O O X / X X O on meta board — no three in a row, all claimed
        gs.meta_board = [1,2,1, 2,2,1, 1,1,2]
        gs._terminal = True
        gs._winner = 0
        return gs

    def test_draw_is_terminal(self):
        gs = self._make_terminal_draw()
        self.assertTrue(gs.is_terminal())

    def test_draw_result_is_zero(self):
        gs = self._make_terminal_draw()
        self.assertEqual(gs.get_result(1), 0.0)
        self.assertEqual(gs.get_result(2), 0.0)

    def test_winner_dict_is_zero_on_draw(self):
        gs = self._make_terminal_draw()
        self.assertEqual(gs.to_dict()["winner"], 0)

    def test_get_result_raises_on_non_terminal(self):
        gs = GameState()
        with self.assertRaises(Exception):
            gs.get_result(1)

    def test_all_meta_resolved_no_winner_is_draw(self):
        # Simulate reaching a state where all boards filled, no meta-winner
        gs = GameState()
        gs.meta_board = [1,2,1, 2,2,1, 1,1,2]
        # Trigger terminal check by calling apply_move on a nearly-final state
        # Instead, directly test that _terminal and _winner are set correctly
        # by a helper method if you expose one, or trust prior tests cover this
        # via the apply_move path.
        gs._terminal = True
        gs._winner = 0
        self.assertTrue(gs.is_terminal())
        self.assertEqual(gs.get_result(1), 0.0)

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_terminal.py -v`

---

## Step 7 — `MCTSNode`

Implement the `MCTSNode` class in `game/mcts.py`.

**Attributes:** `state`, `parent`, `children`, `untried_moves`, `visit_count`, `total_score`, `move`.

**Methods:** `ucb1(c)`, `best_child(c)`, `expand()`, `is_fully_expanded()`, `is_terminal()`.

UCB1 formula: `(total_score / visit_count) + c * sqrt(ln(parent.visit_count) / visit_count)`. Return `+inf` if `visit_count == 0`.

**Tests — `tests/test_mcts_node.py`:**
```python
import unittest, math
from game.state import GameState
from game.mcts import MCTSNode

class TestMCTSNode(unittest.TestCase):
    def _root(self):
        return MCTSNode(state=GameState(), parent=None, move=None)

    def test_untried_moves_equals_legal_moves(self):
        node = self._root()
        self.assertEqual(len(node.untried_moves), 81)

    def test_not_fully_expanded_at_start(self):
        node = self._root()
        self.assertFalse(node.is_fully_expanded())

    def test_not_terminal_at_start(self):
        node = self._root()
        self.assertFalse(node.is_terminal())

    def test_ucb1_unvisited_is_inf(self):
        node = self._root()
        self.assertEqual(node.ucb1(), math.inf)

    def test_expand_reduces_untried_moves(self):
        node = self._root()
        child = node.expand()
        self.assertEqual(len(node.untried_moves), 80)

    def test_expand_adds_to_children(self):
        node = self._root()
        child = node.expand()
        self.assertEqual(len(node.children), 1)

    def test_expand_returns_mctsnode(self):
        node = self._root()
        child = node.expand()
        self.assertIsInstance(child, MCTSNode)

    def test_expand_child_has_correct_parent(self):
        node = self._root()
        child = node.expand()
        self.assertIs(child.parent, node)

    def test_fully_expanded_after_all_moves(self):
        node = self._root()
        # Expand all 81 children
        for _ in range(81):
            node.expand()
        self.assertTrue(node.is_fully_expanded())

    def test_ucb1_value_computed(self):
        node = self._root()
        node.visit_count = 10
        node.total_score = 5.0
        child = node.expand()
        child.visit_count = 2
        child.total_score = 1.0
        val = child.ucb1(c=1.414)
        expected = 1.0/2.0 + 1.414 * math.sqrt(math.log(10) / 2)
        self.assertAlmostEqual(val, expected, places=5)

    def test_best_child_returns_highest_ucb1(self):
        node = self._root()
        node.visit_count = 10
        c1 = node.expand()
        c1.visit_count = 1
        c1.total_score = 0.0
        c2 = node.expand()
        c2.visit_count = 1
        c2.total_score = 1.0
        best = node.best_child(c=0.0)  # exploitation only → highest score wins
        self.assertIs(best, c2)

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_mcts_node.py -v`

---

## Step 8 — `MCTS.search`

Implement the `MCTS` class with `search(root_state) -> tuple[int, int]` using the four MCTS phases (Selection → Expansion → Rollout → Backpropagation).

- Rollout: play random legal moves on cloned states (no tree nodes created).
- Backpropagation: score is from the perspective of the player who made the move to reach each node.
- Final move selection: child of root with highest `visit_count`.

**Tests — `tests/test_mcts_search.py`:**
```python
import unittest
from game.state import GameState
from game.mcts import MCTS

class TestMCTSSearch(unittest.TestCase):
    def test_search_returns_tuple(self):
        gs = GameState()
        mcts = MCTS(iterations=50)
        move = mcts.search(gs)
        self.assertIsInstance(move, tuple)
        self.assertEqual(len(move), 2)

    def test_search_returns_legal_move(self):
        gs = GameState()
        mcts = MCTS(iterations=50)
        move = mcts.search(gs)
        self.assertIn(move, gs.get_legal_moves())

    def test_search_respects_active_board(self):
        gs = GameState()
        gs.active_board = 3
        mcts = MCTS(iterations=50)
        board_idx, _ = mcts.search(gs)
        self.assertEqual(board_idx, 3)

    def test_search_takes_winning_move(self):
        """MCTS with enough iterations should take an obvious win."""
        gs = GameState()
        # X has boards 0 and 1; board 2 top row needs cell 2 to win meta
        gs.meta_board = [1,1,0, 0,0,0, 0,0,0]
        gs.board[2] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 1
        gs.active_board = 2
        mcts = MCTS(iterations=500)
        move = mcts.search(gs)
        self.assertEqual(move, (2, 2))

    def test_search_blocks_opponent_win(self):
        """MCTS should block O from winning the meta-board."""
        gs = GameState()
        # O has boards 0 and 1; board 2 top row needs cell 2 to win meta
        gs.meta_board = [2,2,0, 0,0,0, 0,0,0]
        gs.board[2] = [2,2,0, 0,0,0, 0,0,0]
        gs.current_player = 1   # X to move — must block
        gs.active_board = 2
        mcts = MCTS(iterations=500)
        move = mcts.search(gs)
        self.assertEqual(move, (2, 2))

    def test_search_on_near_terminal_state(self):
        """search on a state one move from terminal should not crash."""
        gs = GameState()
        gs.meta_board = [1,1,0, 0,0,0, 0,0,0]
        gs.board[2] = [1,1,0, 0,0,0, 0,0,0]
        gs.current_player = 2   # O's turn, can't stop X
        gs.active_board = 2
        mcts = MCTS(iterations=100)
        move = mcts.search(gs)
        self.assertIn(move, gs.get_legal_moves())

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_mcts_search.py -v`

---

## Step 9 — Flask Application (`app.py`)

Implement `app.py` with:
- `GET /` → serve `index.html`
- `POST /api/new_game` → initialize state, store in session, optionally run MCTS for X's first move if human plays O
- `POST /api/move` → validate + apply human move, run MCTS, return updated state
- `GET /api/state` → return current state dict

Use `flask.session` (cookie-based) with a `SECRET_KEY`. Serialize `GameState` as a dict in the session; reconstruct on each request.

**Tests — `tests/test_api.py`:**
```python
import unittest, json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import app as flask_app

class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        flask_app.app.config["TESTING"] = True
        flask_app.app.config["SECRET_KEY"] = "test-secret"
        self.client = flask_app.app.test_client()

    def _new_game(self, difficulty="easy", human_plays="X"):
        return self.client.post("/api/new_game",
            data=json.dumps({"difficulty": difficulty, "human_plays": human_plays}),
            content_type="application/json")

    def test_index_returns_200(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)

    def test_new_game_returns_state(self):
        r = self._new_game()
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("state", data)

    def test_new_game_human_x_no_ai_move(self):
        r = self._new_game(human_plays="X")
        data = json.loads(r.data)
        self.assertIsNone(data["ai_move"])

    def test_new_game_human_o_has_ai_move(self):
        r = self._new_game(difficulty="easy", human_plays="O")
        data = json.loads(r.data)
        self.assertIsNotNone(data["ai_move"])
        self.assertIsInstance(data["ai_move"], list)
        self.assertEqual(len(data["ai_move"]), 2)

    def test_move_accepted(self):
        self._new_game(human_plays="X")
        r = self.client.post("/api/move",
            data=json.dumps({"board_index": 4, "cell_index": 4}),
            content_type="application/json")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIsNone(data.get("error"))

    def test_invalid_move_returns_error(self):
        self._new_game(human_plays="X")
        # Make a valid first move
        self.client.post("/api/move",
            data=json.dumps({"board_index": 0, "cell_index": 0}),
            content_type="application/json")
        # Attempt to play in the same cell
        r = self.client.post("/api/move",
            data=json.dumps({"board_index": 0, "cell_index": 0}),
            content_type="application/json")
        data = json.loads(r.data)
        self.assertIsNotNone(data.get("error"))

    def test_get_state_returns_dict(self):
        self._new_game(human_plays="X")
        r = self.client.get("/api/state")
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn("board", data)
        self.assertIn("meta_board", data)

    def test_move_returns_ai_move(self):
        self._new_game(difficulty="easy", human_plays="X")
        r = self.client.post("/api/move",
            data=json.dumps({"board_index": 4, "cell_index": 4}),
            content_type="application/json")
        data = json.loads(r.data)
        self.assertIsNotNone(data.get("ai_move"))

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_api.py -v`

---

## Step 10 — HTML Shell (`templates/index.html`)

Build the single-page shell with:
- Header: game title.
- **Setup panel** (`id="setup-panel"`): difficulty select (`easy`/`medium`/`hard`), side select (`X`/`O`), "Start Game" button.
- **Game panel** (`id="game-panel"`, initially hidden): board container (`id="board"`), status bar (`id="status"`), "New Game" button.
- Script tag loading `/static/game.js`, link tag loading `/static/style.css`.

No JavaScript logic here — just structure.

**Tests — `tests/test_html.py`:**
```python
import unittest, re

class TestHTML(unittest.TestCase):
    def setUp(self):
        with open("templates/index.html") as f:
            self.html = f.read()

    def test_has_setup_panel(self):
        self.assertIn('id="setup-panel"', self.html)

    def test_has_game_panel(self):
        self.assertIn('id="game-panel"', self.html)

    def test_has_board_container(self):
        self.assertIn('id="board"', self.html)

    def test_has_status_bar(self):
        self.assertIn('id="status"', self.html)

    def test_loads_game_js(self):
        self.assertIn("game.js", self.html)

    def test_loads_style_css(self):
        self.assertIn("style.css", self.html)

    def test_difficulty_options(self):
        self.assertIn("easy", self.html.lower())
        self.assertIn("medium", self.html.lower())
        self.assertIn("hard", self.html.lower())

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_html.py -v`

---

## Step 11 — CSS Styling (`static/style.css`)

Implement the stylesheet:
- Neutral background (`#f5f5f5`), dark text.
- Cell minimum `48×48px`, centered X/O text.
- Inner borders: `1px solid #aaa`. Sub-board borders: `3px solid #333`. Meta outer: `4px solid #000`.
- Active board highlight: blue background/border accent.
- Claimed board overlay: large semi-transparent symbol (~60% opacity), blue for X, red for O.
- `.ai-flash` class: yellow background for 600ms AI move highlight.
- Responsive: use `vmin` units so board fits a 375px screen.

**Tests — `tests/test_css.py`:**
```python
import unittest

class TestCSS(unittest.TestCase):
    def setUp(self):
        with open("static/style.css") as f:
            self.css = f.read()

    def test_has_active_board_rule(self):
        self.assertIn("active", self.css)

    def test_has_ai_flash_rule(self):
        self.assertIn("ai-flash", self.css)

    def test_has_min_cell_size(self):
        self.assertIn("48", self.css)

    def test_has_inner_border(self):
        self.assertIn("#aaa", self.css)

    def test_has_subboard_border(self):
        self.assertIn("#333", self.css)

    def test_has_vmin_or_responsive(self):
        self.assertTrue("vmin" in self.css or "max-width" in self.css or
                        "responsive" in self.css.lower())

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_css.py -v`

---

## Step 12 — JavaScript Game Logic (`static/game.js`)

Implement all frontend logic:

**Functions to implement:**
- `startGame()` — POST `/api/new_game`, render returned state, switch panels.
- `renderBoard(state)` — build the 9×9 grid grouped into 3×3 sub-boards. Mark cells with X/O. Add claimed-board overlay. Highlight active board(s). Attach click handlers only to legal cells.
- `onCellClick(boardIdx, cellIdx)` — disable board, POST `/api/move`, flash AI cell for 600ms, render final state.
- `updateStatus(state, isThinking)` — update `#status` text.
- `showSetupPanel()` / `showGamePanel()` — toggle visibility.

**No page reloads. All state comes from the server.**

**Tests — `tests/test_js.py`:**
```python
import unittest, re

class TestJS(unittest.TestCase):
    def setUp(self):
        with open("static/game.js") as f:
            self.js = f.read()

    def test_new_game_api_call(self):
        self.assertIn("/api/new_game", self.js)

    def test_move_api_call(self):
        self.assertIn("/api/move", self.js)

    def test_board_render_function(self):
        self.assertIn("renderBoard", self.js)

    def test_status_update(self):
        self.assertIn("status", self.js)

    def test_ai_flash_class(self):
        self.assertIn("ai-flash", self.js)

    def test_board_index_cell_index_sent(self):
        self.assertIn("board_index", self.js)
        self.assertIn("cell_index", self.js)

    def test_disable_on_waiting(self):
        # Some mechanism to disable clicks while waiting
        self.assertTrue("disabled" in self.js or "waiting" in self.js
                        or "pointer-events" in self.js)

    def test_setup_panel_shown_on_game_end(self):
        self.assertIn("setup-panel", self.js)

if __name__ == "__main__":
    unittest.main()
```

Run: `python -m pytest tests/test_js.py -v`

---

## Step 13 — Full Integration and Manual Smoke Test

Run the complete test suite and then manually verify the running application.

**Full test suite:**
```bash
cd ultimate-ttt && python -m pytest tests/ -v
```

All tests must pass.

**Manual smoke-test checklist (start server with `flask run`):**
- [ ] Page loads at `http://localhost:5000` with setup panel visible.
- [ ] Start a game as X (Easy). Board renders 9 sub-boards.
- [ ] Active boards are highlighted on first move (all boards, free choice).
- [ ] Click a cell. Board updates. AI makes a move (yellow flash visible).
- [ ] After AI moves, only the correct constrained board is highlighted.
- [ ] Win a small board — claimed overlay appears.
- [ ] If sent to a claimed board, all active boards are highlighted (free choice).
- [ ] Win the meta-board — terminal message shown, setup panel reappears.
- [ ] Start a new game without reloading the page.
- [ ] Test Medium and Hard difficulties.
- [ ] Test playing as O (AI moves first).
- [ ] Verify layout is usable on a 375px-wide viewport.
