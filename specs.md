# Ultimate Tic-Tac-Toe — Project Specification

## Overview

Build a web-based implementation of **Ultimate Tic-Tac-Toe** (also called Super Tic-Tac-Toe) where a human plays against an AI powered by **Monte Carlo Tree Search (MCTS)**. The stack is **Flask** (Python backend) with a vanilla **HTML/CSS/JS** frontend. The game must be fully playable in a browser with no page reloads during a match.

---

## Game Rules

Ultimate Tic-Tac-Toe is played on a 3×3 grid of small tic-tac-toe boards, forming a 9×9 playing surface.

1. **X always goes first** and may place their mark on any cell of any small board on the very first move.
2. **Routing rule:** The cell position (0–8, reading left-to-right, top-to-bottom within a small board) chosen by the current player determines *which small board* the opponent must play in next. For example, if a player places in cell position 4 (center) of their board, the opponent must play in small board 4 (the center board of the large grid).
3. This routing rule repeats every turn — the position within the small board always determines the opponent's next board.
4. **Won boards:** When a player completes a row, column, or diagonal in a small board, that board is **claimed** with their symbol. No further moves are allowed on a claimed board.
5. **Free choice:** If the routing rule would send a player to a claimed board (or a full board with no winner), that player may instead place their mark on **any cell of any remaining active board**.
6. **Victory:** The first player to claim three small boards in a row (row, column, or diagonal) on the large meta-board wins the game.
7. **Draw:** If all small boards are resolved and no player has won the meta-board, the game is a draw.

---

## Project Structure

```
ultimate-ttt/
├── app.py                  # Flask application entry point
├── game/
│   ├── __init__.py
│   ├── state.py            # Game state representation and rules logic
│   └── mcts.py             # Monte Carlo Tree Search implementation
├── static/
│   ├── style.css
│   └── game.js             # All frontend game logic and rendering
├── templates/
│   └── index.html          # Single page shell
└── requirements.txt
```

---

## Backend Specification

### `game/state.py` — Game State

Define a `GameState` class (or equivalent dataclass) with the following responsibilities:

**Attributes:**
- `board`: a 9×9 array (or `9` arrays of `9` cells). Each cell value is `0` (empty), `1` (X), or `2` (O).
- `meta_board`: a `3×3` array (or flat array of 9) tracking which small boards have been won: `0` (active), `1` (won by X), `2` (won by O), `3` (drawn/full with no winner).
- `current_player`: `1` (X) or `2` (O).
- `active_board`: an integer `0–8` indicating which small board the current player must play in, or `None` if the player has free choice.

**Methods:**

- `get_legal_moves() -> list[tuple[int, int]]`
  Returns a list of `(board_index, cell_index)` pairs. If `active_board` is set, only return empty cells in that board. If `active_board` is `None`, return all empty cells across all active (unclaimed) boards.

- `apply_move(board_index: int, cell_index: int) -> GameState`
  Returns a **new** `GameState` (do not mutate in place) reflecting the move. Steps:
  1. Place the current player's mark at `board[board_index][cell_index]`.
  2. Check if the small board at `board_index` is now won or drawn; update `meta_board` accordingly.
  3. Check if the meta-board is now won or drawn; if so, set a terminal flag.
  4. Determine `active_board` for the next turn: if `meta_board[cell_index]` is still active, set `active_board = cell_index`; otherwise set `active_board = None`.
  5. Switch `current_player`.

- `check_winner(board: list[int]) -> int`
  Given a flat list of 9 values, return `1`, `2`, or `0` (no winner yet). Checks all 8 winning lines (3 rows, 3 columns, 2 diagonals).

- `is_terminal() -> bool`
  Returns `True` if the game is over (someone won the meta-board, or all boards are resolved).

- `get_result(perspective_player: int) -> float`
  Returns `+1.0` if `perspective_player` won, `-1.0` if they lost, `0.0` for draw. Only valid when `is_terminal()` is `True`.

- `clone() -> GameState`
  Returns a deep copy of the state.

- `to_dict() -> dict`
  Serializes the state to a JSON-serializable dictionary for sending to the frontend.

---

### `game/mcts.py` — Monte Carlo Tree Search

Implement MCTS with the **UCB1 tree descent policy**.

#### `MCTSNode` class

**Attributes:**
- `state: GameState`
- `parent: MCTSNode | None`
- `children: dict[tuple[int,int], MCTSNode]` — maps move to child node
- `untried_moves: list[tuple[int,int]]` — legal moves not yet expanded
- `visit_count: int`
- `total_score: float`
- `move: tuple[int,int] | None` — the move that led to this node

**Methods:**

- `ucb1(exploration_constant: float = 1.414) -> float`
  Returns the UCB1 value: `(total_score / visit_count) + C * sqrt(ln(parent.visit_count) / visit_count)`. Return `+infinity` if `visit_count == 0`.

- `best_child(c: float) -> MCTSNode`
  Returns the child with the highest UCB1 value given exploration constant `c`.

- `expand() -> MCTSNode`
  Pops one move from `untried_moves`, creates a new child node for it, adds it to `children`, and returns it.

- `is_fully_expanded() -> bool`
  Returns `True` when `untried_moves` is empty.

- `is_terminal() -> bool`
  Delegates to `self.state.is_terminal()`.

#### `MCTS` class

**Constructor:** `__init__(self, iterations: int)`

**Method:** `search(root_state: GameState) -> tuple[int, int]`

Implements the four MCTS phases in a loop for `self.iterations` iterations:

1. **Selection:** Starting from the root node, repeatedly call `best_child(c=1.414)` to descend the tree while the node is fully expanded and non-terminal.
2. **Expansion:** If the node is not terminal and not fully expanded, call `expand()` to add one new child.
3. **Rollout (simulation):** From the expanded node's state, play random legal moves until reaching a terminal state. Do **not** create tree nodes during rollout — just simulate on cloned states.
4. **Backpropagation:** Walk back up the tree from the expanded node to the root, updating each node: `visit_count += 1`, `total_score += result`. The result should be from the perspective of the node's **parent's** current player (i.e., the player who made the move to reach this node).

After all iterations, return the move corresponding to the child of the root with the **highest `visit_count`** (not UCB1 — exploitation only at the final selection step).

**Difficulty settings** (iterations):

| Difficulty | Iterations |
|---|---|
| Easy | 200 |
| Medium | 1 500 |
| Hard | 10 000 |

---

### `app.py` — Flask Routes

All game state lives **server-side** in a Flask session (or in-memory dict keyed by session ID). The frontend communicates via JSON API.

#### `GET /`
Serves `index.html`.

#### `POST /api/new_game`
**Request body:** `{ "difficulty": "easy" | "medium" | "hard", "human_plays": "X" | "O" }`

Initializes a fresh `GameState`. Stores it in the session. If the human plays O, immediately run MCTS to get X's first move and apply it.

**Response:**
```json
{
  "state": { ...GameState.to_dict()... },
  "ai_move": [board_index, cell_index] | null
}
```

#### `POST /api/move`
**Request body:** `{ "board_index": int, "cell_index": int }`

Validates the move is legal. Applies it. If the game is not over, runs MCTS to get the AI's response move and applies that too.

**Response:**
```json
{
  "state": { ...GameState.to_dict()... },
  "ai_move": [board_index, cell_index] | null,
  "error": null | "string describing invalid move"
}
```

#### `GET /api/state`
Returns the current `GameState.to_dict()` for the session. Useful for page refresh recovery.

---

### `GameState.to_dict()` Schema

```json
{
  "board": [[int × 9] × 9],
  "meta_board": [int × 9],
  "current_player": 1 | 2,
  "active_board": int | null,
  "is_terminal": bool,
  "winner": 1 | 2 | 0 | null
}
```

- `board[i][j]`: cell `j` of small board `i`. Values: `0`=empty, `1`=X, `2`=O.
- `meta_board[i]`: `0`=active, `1`=X won, `2`=O won, `3`=drawn.
- `winner`: `1` or `2` if someone won the meta-board, `0` for draw, `null` if game is ongoing.

---

## Frontend Specification

### `templates/index.html`

Single-page shell. Loads `style.css` and `game.js`. Contains:
- A header with the game title.
- A **setup panel** (shown before a game starts and after one ends): difficulty selector (Easy / Medium / Hard), side selector (Play as X / Play as O), and a "Start Game" button.
- A **game panel** (shown during a game): the board, a status bar, and a "New Game" button.

### `static/game.js`

Handles all rendering and API calls. No page reloads. Key responsibilities:

**Board rendering:**
- Render a 9×9 grid visually grouped into nine 3×3 sub-boards with a clearly thicker border between sub-boards than between cells.
- Claimed small boards: overlay the board with a large semi-transparent X or O symbol. Cells within claimed boards are not clickable.
- **Highlight the active board** (the one the current player must play in) with a distinct background color or border. When the player has free choice, highlight all active boards.
- Each cell is clickable. On click, send `POST /api/move` with the appropriate `board_index` and `cell_index`.

**Status bar:**
- Display whose turn it is ("Your turn" / "AI is thinking...").
- Display the active board constraint ("You must play in board 5" / "You may play anywhere").
- Display the game result when terminal ("You win! 🎉" / "AI wins." / "Draw.").

**AI move display:**
- After the API returns the AI's move, briefly highlight the cell the AI played in (e.g., 600ms yellow flash) before rendering the final board state.

**Interactions:**
- Disable all cells while waiting for an API response.
- On game end, show the setup panel again so a new game can be started without a page reload.

---

## Styling (`static/style.css`)

- Clean, readable design. No external CSS frameworks.
- Color scheme: neutral background (e.g., `#f5f5f5`), dark text, blue accent for active board highlights.
- Board cells: minimum `48×48px`, centered X/O text, hover highlight on legal cells.
- Inner cell borders: `1px solid #aaa`. Sub-board borders: `3px solid #333`. Meta-board outer border: `4px solid #000`.
- Claimed board overlay: large centered symbol at ~60% opacity in the winner's color (blue for X, red for O).
- Responsive: the board should fit on a 375px-wide mobile screen (scale the board with `vmin` units or similar).

---

## Requirements (`requirements.txt`)

```
flask>=3.0
```

No other third-party dependencies. The MCTS and game logic must be implemented from scratch in pure Python.

---

## Implementation Notes & Constraints

- **Immutable state:** `apply_move` must return a new state object. Never mutate state in place — this is critical for MCTS correctness.
- **Rollout efficiency:** The rollout phase runs many times per AI turn. Use lightweight state cloning; avoid deep-copying anything unnecessary.
- **Session handling:** Use Flask's built-in session (cookie-based) with a `SECRET_KEY`. Store the serialized game state as a dict in the session, reconstructing the `GameState` object on each request.
- **Concurrency:** A single-threaded Flask dev server is fine. No async or threading required.
- **No external game libraries:** Implement all game logic and MCTS from scratch.
- **Testing:** Include a `test_game.py` file with at minimum: tests for `check_winner`, `get_legal_moves` on a free-choice state, `apply_move` routing logic, and `is_terminal` detection. Use Python's built-in `unittest`.

---

## Out of Scope

- User accounts or persistent storage
- AI vs AI mode or human vs human mode
- Move history / undo
- Animated transitions (beyond the AI move highlight)
- Any external JS libraries or CSS frameworks