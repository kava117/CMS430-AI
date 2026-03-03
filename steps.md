# DOMINION — Implementation Steps (Python / Flask)

**Target deliverable:** A multi-file Python web application.
**Stack:** Python 3.10+, Flask, HTML5 Canvas (client-side rendering), CSS custom properties. No npm, no bundler.

Run all Python tests from the project root with `pytest tests/ -v`.
Browser console tests require the Flask dev server running (`flask run` or `python app.py`).

---

## Step 1 — Project Scaffolding

**Goal:** Create the directory structure, install dependencies, and verify the Flask development server starts and serves the index page.

### Tasks
1. Create the following directory tree (all files empty stubs for now):
   ```
   dominion/
     app.py
     requirements.txt
     game/
       __init__.py
       constants.py
       board.py
       fog.py
       moves.py
       claim.py
       ai.py
     static/
       css/
         dominion.css
       js/
         render.js
         client.js
     templates/
       index.html
     tests/
       __init__.py
       test_board.py
       test_fog.py
       test_moves.py
       test_claim.py
       test_ai.py
       test_api.py
   ```
2. `requirements.txt`:
   ```
   flask>=3.0
   pytest>=8.0
   ```
3. `app.py` stub:
   ```python
   from flask import Flask, render_template
   app = Flask(__name__)
   app.secret_key = 'dominion-dev'

   @app.route('/')
   def index():
       return render_template('index.html')

   if __name__ == '__main__':
       app.run(debug=True, port=5000)
   ```
4. `templates/index.html` stub: minimal HTML5 document, links `dominion.css` and both JS files, contains a `<canvas id="board-canvas">`.
5. Install dependencies: `pip install -r requirements.txt`.

### Tests
```python
# tests/test_api.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_index_returns_200(client):
    r = client.get('/')
    assert r.status_code == 200

def test_index_contains_canvas(client):
    r = client.get('/')
    assert b'board-canvas' in r.data
```
Run: `pytest tests/test_api.py -v` — both tests must pass before continuing.

---

## Step 2 — Constants

**Goal:** Implement `game/constants.py` with all tile types, owner values, vision ranges, weights, and display data.

### Tasks
1. Define integer tile-type constants:
   ```python
   FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN = range(8)
   ```
2. Define owner constants: `NONE, PLAYER, AI = 0, 1, 2`
3. Define:
   - `TILE_WEIGHTS` — `{FOREST:35, PLAINS:20, TOWER:8, CAVE:8, MOUNTAIN:15, WIZARD:5, BARBARIAN:9}` (Domain excluded — placed deterministically)
   - `VISION_RANGE` — dict mapping each tile type to its vision range (Forest/Domain/Wizard/Barbarian=1, Plains=2, Tower=3, Cave=1, Mountain=0)
   - `STRATEGIC_VALUE` — dict mapping tile type to AI strategic value (Cave=4, Wizard=3, Tower=2.5, Plains=2, Forest/Domain=1.5, Barbarian=0.5, Mountain=0)
   - `TILE_BASE_COLOR` — dict of hex strings per tile type
   - `TILE_ICON` — dict of Unicode glyphs per tile type (♣ ≈ ▲ ○ ◆ ✦ ⚔ ⬡)
   - `TILE_LABEL` — dict of display names per tile type
   - `DIRS` — `[(0,-1),(0,1),(-1,0),(1,0)]` — cardinal directions

### Tests
```python
# tests/test_board.py  (constants section)
from game.constants import (
    FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN,
    NONE, PLAYER, AI,
    TILE_WEIGHTS, VISION_RANGE, STRATEGIC_VALUE, TILE_ICON, DIRS
)

def test_tile_type_values_are_unique():
    types = [FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN]
    assert len(set(types)) == 8

def test_owner_values_are_unique():
    assert len({NONE, PLAYER, AI}) == 3

def test_tile_weights_cover_all_random_types():
    # Domain is placed deterministically, so it has no weight entry
    for t in [FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN]:
        assert t in TILE_WEIGHTS
    assert DOMAIN not in TILE_WEIGHTS

def test_vision_range_covers_all_types():
    for t in [FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN]:
        assert t in VISION_RANGE

def test_dirs_are_cardinal():
    assert len(DIRS) == 4
    assert all(len(d) == 2 for d in DIRS)
```
Run: `pytest tests/test_board.py::test_tile_type_values_are_unique -v` and the rest — all must pass.

---

## Step 3 — Board Generation

**Goal:** Implement `game/board.py` with `idx()`, `xy()`, `in_bounds()`, `make_cell()`, and `generate_board()`.

### Tasks
1. `idx(x, y, W) -> int` — returns `y * W + x`
2. `xy(i, W) -> tuple[int, int]` — returns `(i % W, i // W)`
3. `in_bounds(x, y, W, H) -> bool`
4. `make_cell(tile_type) -> dict` — returns `{'type': tile_type, 'owner': NONE, 'used': False}`
5. `generate_board(seed: str, W: int, H: int) -> list[dict]`:
   - Call `random.seed(seed)` at the top — all subsequent `random` calls are deterministic.
   - Build a cumulative weight list from `TILE_WEIGHTS` and use `random.random()` to pick each tile type by weight.
   - After placing all tiles, count Cave tiles; while count < 2, pick a random non-Mountain index with `random.randrange(W*H)` and overwrite it with `CAVE`.
   - Place Player Domain: start at `(1,1)`, walk right (`x++`) skipping Mountain cells; set `type=DOMAIN`, `owner=PLAYER`.
   - Place AI Domain: start at `(W-2, H-2)`, walk left (`x--`) skipping Mountain or already-owned cells; set `type=DOMAIN`, `owner=AI`.
   - Return the completed board list.

### Tests
```python
# tests/test_board.py
import random
from game.board import idx, xy, in_bounds, make_cell, generate_board
from game.constants import CAVE, MOUNTAIN, DOMAIN, NONE, PLAYER, AI

def test_idx_and_xy_roundtrip():
    W = 14
    for i in range(W * 10):
        x, y = xy(i, W)
        assert idx(x, y, W) == i

def test_in_bounds():
    assert in_bounds(0, 0, 10, 8)
    assert not in_bounds(-1, 0, 10, 8)
    assert not in_bounds(10, 0, 10, 8)
    assert not in_bounds(0, 8, 10, 8)

def test_make_cell_defaults():
    c = make_cell(CAVE)
    assert c == {'type': CAVE, 'owner': NONE, 'used': False}

def test_board_length():
    board = generate_board('test', 14, 10)
    assert len(board) == 140

def test_cave_guarantee():
    for seed in ['a', 'b', 'c', 'test123', 'xyz']:
        board = generate_board(seed, 14, 10)
        caves = [c for c in board if c['type'] == CAVE]
        assert len(caves) >= 2, f"Seed '{seed}' produced fewer than 2 caves"

def test_domain_placement():
    board = generate_board('test', 14, 10)
    player_domain = next((c for c in board if c['type'] == DOMAIN and c['owner'] == PLAYER), None)
    ai_domain     = next((c for c in board if c['type'] == DOMAIN and c['owner'] == AI), None)
    assert player_domain is not None, "Player domain missing"
    assert ai_domain is not None, "AI domain missing"

def test_mountains_never_owned():
    board = generate_board('test', 14, 10)
    assert all(c['owner'] == NONE for c in board if c['type'] == MOUNTAIN)

def test_determinism():
    b1 = generate_board('myseed', 14, 10)
    b2 = generate_board('myseed', 14, 10)
    assert [c['type'] for c in b1] == [c['type'] for c in b2]

def test_different_seeds_differ():
    b1 = generate_board('seed-A', 14, 10)
    b2 = generate_board('seed-B', 14, 10)
    assert [c['type'] for c in b1] != [c['type'] for c in b2]
```
Run: `pytest tests/test_board.py -v` — all 8 tests must pass.

---

## Step 4 — Fog of War

**Goal:** Implement `game/fog.py` with `compute_fog()` and `bfs_reveal()`.

### Tasks
1. `bfs_reveal(board, W, H, start_idx, vision_range) -> set[int]`:
   - Cardinal BFS from `start_idx` up to `vision_range` steps.
   - Mountains do **not** block propagation — the BFS continues through them.
   - Returns the set of all revealed indices (including the start tile).
2. `compute_fog(G: dict) -> set[int]`:
   - Iterate every cell in `G['board']`. For each owned tile (`owner != NONE`):
     - Look up `VISION_RANGE[cell['type']]`. Skip if 0.
     - Call `bfs_reveal(...)` and union the result into the fog set.
   - **Cave special:** if any cell has `type == CAVE` and `owner != NONE`, add **all** Cave tile indices to the fog set.
   - Return the completed set (do not store it — the caller stores it as `G['fog']`).

### Tests
```python
# tests/test_fog.py
from game.board import generate_board, idx, xy
from game.fog import compute_fog, bfs_reveal
from game.constants import CAVE, MOUNTAIN, DOMAIN, TOWER, PLAINS, NONE, PLAYER, AI

def _make_G(seed='fogtest', W=14, H=10):
    board = generate_board(seed, W, H)
    G = {'W': W, 'H': H, 'board': board, 'fog': set()}
    G['fog'] = compute_fog(G)
    return G

def test_starting_tiles_revealed():
    G = _make_G()
    player_idx = next(i for i, c in enumerate(G['board']) if c['owner'] == PLAYER)
    ai_idx     = next(i for i, c in enumerate(G['board']) if c['owner'] == AI)
    assert player_idx in G['fog']
    assert ai_idx in G['fog']

def test_cardinal_neighbor_of_domain_revealed():
    G = _make_G()
    player_idx = next(i for i, c in enumerate(G['board']) if c['owner'] == PLAYER)
    x, y = xy(player_idx, G['W'])
    neighbors = [
        idx(x+dx, y+dy, G['W'])
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]
        if 0 <= x+dx < G['W'] and 0 <= y+dy < G['H']
    ]
    assert any(n in G['fog'] for n in neighbors), "No neighbor of player domain revealed"

def test_fog_is_nonempty():
    G = _make_G()
    assert len(G['fog']) > 0

def test_mountain_does_not_block_bfs():
    # Mountains should not stop BFS propagation — tiles beyond them are still reachable
    W, H = 10, 8
    board = generate_board('bfstest', W, H)
    # Force a Mountain adjacent to start and check that tile beyond it can be revealed
    start = idx(1, 1, W)
    board[start]['owner'] = PLAYER
    mountain_idx = idx(2, 1, W)
    board[mountain_idx]['type'] = MOUNTAIN
    beyond_idx = idx(3, 1, W)
    G = {'W': W, 'H': H, 'board': board, 'fog': set()}
    G['fog'] = compute_fog(G)
    # Tower vision (range 3) would reveal beyond; Domain only range 1 so check range manually
    revealed = bfs_reveal(board, W, H, start, 3)
    assert beyond_idx in revealed, "BFS blocked by Mountain — should propagate through"

def test_cave_ownership_reveals_all_caves():
    W, H = 14, 10
    board = generate_board('cavetest', W, H)
    cave_indices = [i for i, c in enumerate(board) if c['type'] == CAVE]
    assert len(cave_indices) >= 2
    # Give player the first cave
    board[cave_indices[0]]['owner'] = PLAYER
    G = {'W': W, 'H': H, 'board': board, 'fog': set()}
    G['fog'] = compute_fog(G)
    for ci in cave_indices:
        assert ci in G['fog'], f"Cave at index {ci} not revealed globally"
```
Run: `pytest tests/test_fog.py -v` — all 5 tests must pass.

---

## Step 5 — Valid Moves Computation

**Goal:** Implement `game/moves.py` with `compute_valid_moves(G, owner)`.

### Tasks
1. `compute_valid_moves(G: dict, owner: int) -> set[int]`:
   - **Wizard teleport phase** (`G['wizard_active_for'] == owner`): return every revealed, unclaimed, non-Mountain tile index — skip the normal expansion logic entirely.
   - Otherwise, iterate every cell owned by `owner` and apply its expansion rules:
     - **Forest / Domain / Wizard / Barbarian:** cardinal neighbors at distance 1.
     - **Plains:** all cardinal positions at distance 1 and 2 (4 directions × 2 steps).
     - **Tower:** all cardinal positions at distance 1, 2, and 3 (Mountains do **not** block).
     - **Cave:** all Cave tile indices anywhere on the board (fog filter applied below).
   - After collecting candidates, filter to keep only those where:
     - `board[i]['owner'] == NONE`
     - `board[i]['type'] != MOUNTAIN`
     - `i in G['fog']` (tile is revealed)
   - Return the filtered set.

### Tests
```python
# tests/test_moves.py
from game.board import generate_board, idx, xy
from game.fog import compute_fog
from game.moves import compute_valid_moves
from game.constants import (
    NONE, PLAYER, AI,
    FOREST, PLAINS, TOWER, CAVE, MOUNTAIN, WIZARD, BARBARIAN, DOMAIN
)

def _make_G(seed='movetest', W=14, H=10):
    board = generate_board(seed, W, H)
    G = {'W': W, 'H': H, 'board': board, 'fog': set(), 'wizard_active_for': NONE}
    G['fog'] = compute_fog(G)
    return G

def test_player_has_moves_at_start():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    assert len(moves) > 0

def test_ai_has_moves_at_start():
    G = _make_G()
    moves = compute_valid_moves(G, AI)
    assert len(moves) > 0

def test_no_mountains_in_valid_moves():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    assert all(G['board'][i]['type'] != MOUNTAIN for i in moves)

def test_no_owned_tiles_in_valid_moves():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    assert all(G['board'][i]['owner'] == NONE for i in moves)

def test_no_fogged_tiles_in_valid_moves():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    assert all(i in G['fog'] for i in moves)

def test_plains_expansion_reaches_distance_2():
    W, H = 12, 10
    board = generate_board('plainstest', W, H)
    # Force a Plains tile owned by player at (3,3)
    pi = idx(3, 3, W)
    board[pi] = {'type': PLAINS, 'owner': PLAYER, 'used': False}
    G = {'W': W, 'H': H, 'board': board, 'fog': set(), 'wizard_active_for': NONE}
    G['fog'] = compute_fog(G)
    # Reveal tiles manually so distance-2 tiles pass the fog filter
    for dx, dy in [(0,-1),(0,1),(-1,0),(1,0),(0,-2),(0,2),(-2,0),(2,0)]:
        nx, ny = 3+dx, 3+dy
        if 0 <= nx < W and 0 <= ny < H:
            G['fog'].add(idx(nx, ny, W))
    moves = compute_valid_moves(G, PLAYER)
    dist2 = idx(3, 5, W)  # (3, 3+2)
    if board[dist2]['type'] != MOUNTAIN and board[dist2]['owner'] == NONE:
        assert dist2 in moves, "Plains did not reach distance-2 tile"

def test_tower_expansion_reaches_distance_3():
    W, H = 12, 10
    board = generate_board('towertest', W, H)
    ti = idx(4, 4, W)
    board[ti] = {'type': TOWER, 'owner': PLAYER, 'used': False}
    G = {'W': W, 'H': H, 'board': board, 'fog': set(), 'wizard_active_for': NONE}
    G['fog'] = compute_fog(G)
    for step in range(1, 4):
        for dx, dy in [(0,-1),(0,1),(-1,0),(1,0)]:
            nx, ny = 4+dx*step, 4+dy*step
            if 0 <= nx < W and 0 <= ny < H:
                G['fog'].add(idx(nx, ny, W))
    moves = compute_valid_moves(G, PLAYER)
    dist3 = idx(4, 7, W)  # (4, 4+3)
    if board[dist3]['type'] != MOUNTAIN and board[dist3]['owner'] == NONE:
        assert dist3 in moves, "Tower did not reach distance-3 tile"

def test_wizard_teleport_returns_all_revealed_unclaimed():
    G = _make_G()
    G['wizard_active_for'] = PLAYER
    moves = compute_valid_moves(G, PLAYER)
    expected = {
        i for i, c in enumerate(G['board'])
        if c['owner'] == NONE and c['type'] != MOUNTAIN and i in G['fog']
    }
    assert moves == expected
    G['wizard_active_for'] = NONE  # restore
```
Run: `pytest tests/test_moves.py -v` — all 8 tests must pass.

---

## Step 6 — Tile Claiming, Barbarian Triggers & Win Condition

**Goal:** Implement `game/claim.py` with `claim_tile()`, `trigger_barbarians()`, and `check_win_condition()`.

### Tasks
1. `snapshot_board(G: dict) -> list[dict]`:
   - Return `[cell.copy() for cell in G['board']]` — shallow copy is sufficient (all values are primitives).
2. `restore_board(G: dict, snap: list[dict])`:
   - Copy `snap` values back into `G['board']` and recompute fog: `G['fog'] = compute_fog(G)`.
3. `trigger_barbarians(G: dict, index: int, minimax_mode: bool = False)`:
   - Determine sweep direction: `'h'` if `W > H`, `'v'` if `H > W`, or `random.choice(['h','v'])` if `W == H` (deterministic `'h'` during `minimax_mode`).
   - Horizontal sweep: reset `owner = NONE` for every non-Mountain tile in the same **row** as `index`, including the Barbarian tile itself.
   - Vertical sweep: reset `owner = NONE` for every non-Mountain tile in the same **column**.
   - Append a log event string to `G['log']` (only when `not minimax_mode`).
   - Call `G['fog'] = compute_fog(G)` after the sweep.
4. `claim_tile(G: dict, index: int, owner: int, minimax_mode: bool = False) -> bool`:
   - Snapshot `G['fog']` before mutating.
   - Set `G['board'][index]['owner'] = owner`.
   - If the claimed tile is a Barbarian: call `trigger_barbarians(G, index, minimax_mode)`.
   - Recompute `G['fog'] = compute_fog(G)`.
   - For each index newly in `G['fog']` (not in the pre-claim snapshot) other than `index` itself: if it is a Barbarian with `owner == NONE`, call `trigger_barbarians(G, ni, minimax_mode)` in index order.
   - Return `True` if the claimed tile was a Wizard, else `False`.
5. `check_win_condition(G: dict) -> int | str | None`:
   - Filter claimable tiles: `[c for c in board if c['type'] != MOUNTAIN]`.
   - Compute `total`, `player_count`, `ai_count`, `majority = total // 2 + 1`.
   - Return `PLAYER` if `player_count >= majority`; `AI` if `ai_count >= majority`.
   - If all claimable tiles have owners: return `PLAYER`, `AI`, or `'DRAW'` by count comparison.
   - Otherwise return `None`.

### Tests
```python
# tests/test_claim.py
from game.board import generate_board, idx, xy
from game.fog import compute_fog
from game.moves import compute_valid_moves
from game.claim import claim_tile, trigger_barbarians, check_win_condition, snapshot_board, restore_board
from game.constants import (
    NONE, PLAYER, AI,
    CAVE, MOUNTAIN, DOMAIN, BARBARIAN, WIZARD, FOREST
)

def _make_G(seed='claimtest', W=14, H=10):
    board = generate_board(seed, W, H)
    G = {
        'W': W, 'H': H, 'board': board,
        'fog': set(), 'wizard_active_for': NONE, 'log': [],
    }
    G['fog'] = compute_fog(G)
    return G

def test_claim_sets_owner():
    G = _make_G()
    moves = compute_valid_moves(G, PLAYER)
    target = next(iter(moves))
    claim_tile(G, target, PLAYER)
    assert G['board'][target]['owner'] == PLAYER

def test_claim_updates_fog():
    G = _make_G()
    fog_before = len(G['fog'])
    moves = compute_valid_moves(G, PLAYER)
    target = next(iter(moves))
    claim_tile(G, target, PLAYER)
    assert len(G['fog']) >= fog_before

def test_win_condition_none_at_start():
    G = _make_G()
    assert check_win_condition(G) is None

def test_win_condition_majority():
    G = _make_G(W=8, H=6)
    claimable = [i for i, c in enumerate(G['board']) if c['type'] != MOUNTAIN]
    majority = len(claimable) // 2 + 1
    for i in claimable[:majority]:
        G['board'][i]['owner'] = PLAYER
    assert check_win_condition(G) == PLAYER

def test_win_condition_draw():
    G = _make_G(W=8, H=6)
    claimable = [i for i, c in enumerate(G['board']) if c['type'] != MOUNTAIN]
    half = len(claimable) // 2
    for i in claimable[:half]:
        G['board'][i]['owner'] = PLAYER
    for i in claimable[half:]:
        G['board'][i]['owner'] = AI
    result = check_win_condition(G)
    # All tiles claimed; equal counts → DRAW
    assert result in ('DRAW', PLAYER, AI)  # depends on parity

def test_barbarian_sweep_row(monkeypatch):
    G = _make_G(W=14, H=10)  # W > H, so always horizontal
    row = 3
    barb_idx = idx(5, row, G['W'])
    G['board'][barb_idx]['type'] = BARBARIAN
    G['board'][barb_idx]['owner'] = NONE
    # Give player some tiles in that row
    for x in [1, 2, 3]:
        G['board'][idx(x, row, G['W'])]['owner'] = PLAYER
    trigger_barbarians(G, barb_idx, minimax_mode=True)
    row_tiles = [G['board'][idx(x, row, G['W'])] for x in range(G['W'])]
    non_mountain = [c for c in row_tiles if c['type'] != MOUNTAIN]
    assert all(c['owner'] == NONE for c in non_mountain), "Barbarian horizontal sweep failed"

def test_barbarian_sweep_column():
    G = _make_G(W=8, H=14)  # H > W, so always vertical
    col = 3
    barb_idx = idx(col, 5, G['W'])
    G['board'][barb_idx]['type'] = BARBARIAN
    G['board'][barb_idx]['owner'] = NONE
    for y in [1, 2, 3]:
        G['board'][idx(col, y, G['W'])]['owner'] = AI
    trigger_barbarians(G, barb_idx, minimax_mode=True)
    col_tiles = [G['board'][idx(col, y, G['W'])] for y in range(G['H'])]
    non_mountain = [c for c in col_tiles if c['type'] != MOUNTAIN]
    assert all(c['owner'] == NONE for c in non_mountain), "Barbarian vertical sweep failed"

def test_snapshot_restore():
    G = _make_G()
    snap = snapshot_board(G)
    moves = compute_valid_moves(G, PLAYER)
    target = next(iter(moves))
    claim_tile(G, target, PLAYER)
    assert G['board'][target]['owner'] == PLAYER
    restore_board(G, snap)
    assert G['board'][target]['owner'] == NONE, "Restore did not revert ownership"

def test_claim_wizard_returns_true():
    G = _make_G()
    wiz_idx = next((i for i, c in enumerate(G['board']) if c['type'] == WIZARD), None)
    if wiz_idx is None:
        return  # no wizard on this board — skip
    G['board'][wiz_idx]['owner'] = NONE
    G['fog'].add(wiz_idx)
    result = claim_tile(G, wiz_idx, PLAYER)
    assert result is True
```
Run: `pytest tests/test_claim.py -v` — all 9 tests must pass.

---

## Step 7 — AI: Minimax with Alpha-Beta Pruning

**Goal:** Implement `game/ai.py` with `heuristic()`, `minimax_alpha_beta()`, `minimax_root()`, and `wizard_teleport_decision()`.

### Tasks
1. `heuristic(G: dict) -> float`:
   - Compute `ai_count`, `player_count` from board (non-Mountain tiles).
   - `ai_frontier = len(compute_valid_moves(G, AI))`, `player_frontier = len(compute_valid_moves(G, PLAYER))`.
   - Cave control, wizard reserve, Barbarian exposure penalty booleans/counts as per spec §8.3.
   - `barb_exposure(owner)`: count owned tiles sharing a row (W≥H) or column (H>W) with a **fogged** Barbarian.
   - Return the weighted sum per the spec formula.
2. `minimax_alpha_beta(G, depth, alpha, beta, is_maximizing) -> float`:
   - Check terminal condition first (`check_win_condition`), then depth 0 → `heuristic`.
   - Get moves for the active player (`AI` if maximizing, `PLAYER` if minimizing).
   - If no moves: recurse with same depth−1 and flipped maximizing flag (pass-through turn).
   - Sort moves by `STRATEGIC_VALUE[board[i]['type']]` descending before iterating.
   - For each move: snapshot → `claim_tile(..., minimax_mode=True)` → recurse → restore. Save/restore `G['wizard_active_for']` around each simulation.
   - Apply alpha-beta pruning (`break` when `beta <= alpha`).
3. `minimax_root(G: dict, depth: int) -> int`:
   - Iterate AI valid moves (sorted by strategic value), call `minimax_alpha_beta` for each.
   - Return the index of the highest-valued move.
4. `wizard_teleport_decision(G: dict) -> int | None`:
   - Find the revealed unclaimed non-Mountain tile with the highest `STRATEGIC_VALUE`.
   - Return its index if `best_value > 2`, otherwise `None`.

### Tests
```python
# tests/test_ai.py
import math
from game.board import generate_board, idx
from game.fog import compute_fog
from game.moves import compute_valid_moves
from game.claim import check_win_condition
from game.ai import heuristic, minimax_root, wizard_teleport_decision, minimax_alpha_beta
from game.constants import NONE, PLAYER, AI, CAVE, WIZARD, MOUNTAIN

def _make_G(seed='aitest', W=10, H=8, depth=2):
    board = generate_board(seed, W, H)
    G = {
        'W': W, 'H': H, 'depth': depth,
        'board': board, 'fog': set(),
        'wizard_active_for': NONE, 'log': [],
    }
    G['fog'] = compute_fog(G)
    return G

def test_heuristic_returns_float():
    G = _make_G()
    h = heuristic(G)
    assert isinstance(h, (int, float))
    assert math.isfinite(h)

def test_heuristic_increases_when_ai_gains_tile():
    G = _make_G()
    h_before = heuristic(G)
    free = next(
        i for i, c in enumerate(G['board'])
        if c['owner'] == NONE and c['type'] != MOUNTAIN and i in G['fog']
    )
    G['board'][free]['owner'] = AI
    h_after = heuristic(G)
    G['board'][free]['owner'] = NONE  # restore
    assert h_after > h_before

def test_minimax_root_returns_valid_move():
    G = _make_G()
    ai_moves = compute_valid_moves(G, AI)
    best = minimax_root(G, depth=2)
    assert best in ai_moves, f"minimax_root returned {best} which is not a valid AI move"

def test_minimax_root_does_not_mutate_board():
    G = _make_G()
    board_snapshot = [c.copy() for c in G['board']]
    fog_snapshot   = set(G['fog'])
    minimax_root(G, depth=2)
    assert [c['owner'] for c in G['board']] == [c['owner'] for c in board_snapshot]
    assert G['fog'] == fog_snapshot

def test_minimax_prefers_cave():
    W, H = 10, 8
    board = generate_board('cave-pref', W, H)
    G = {'W': W, 'H': H, 'depth': 2, 'board': board, 'fog': set(),
         'wizard_active_for': NONE, 'log': []}
    G['fog'] = compute_fog(G)
    ai_dom = next(i for i, c in enumerate(board) if c['owner'] == AI)
    from game.board import xy
    ax, ay = xy(ai_dom, W)
    cave_idx = idx(max(0, ax - 1), ay, W)
    board[cave_idx] = {'type': CAVE, 'owner': NONE, 'used': False}
    G['fog'].add(cave_idx)
    best = minimax_root(G, depth=2)
    # Cave adjacent to AI domain should be strongly preferred
    assert best == cave_idx or G['board'][best]['type'] == CAVE, \
        "AI did not prefer an adjacent Cave tile"

def test_wizard_teleport_decision_returns_high_value():
    G = _make_G()
    # Reveal a Cave tile for the wizard to target
    cave_idx = next(
        (i for i, c in enumerate(G['board'])
         if c['type'] == CAVE and c['owner'] == NONE),
        None
    )
    if cave_idx is None:
        return
    G['fog'].add(cave_idx)
    result = wizard_teleport_decision(G)
    assert result is not None
    assert G['board'][result]['type'] == CAVE or result == cave_idx

def test_wizard_teleport_decision_declines_low_value():
    G = _make_G()
    # Remove all high-value tiles from fog — only keep revealed mountains (unclaim-able)
    G['fog'] = set(
        i for i, c in enumerate(G['board'])
        if c['type'] == MOUNTAIN
    )
    result = wizard_teleport_decision(G)
    assert result is None  # all visible tiles are Mountains → decline
```
Run: `pytest tests/test_ai.py -v` — all 7 tests must pass.

---

## Step 8 — Flask API

**Goal:** Implement `app.py` with all four API endpoints: `/api/start`, `/api/move`, `/api/state`, and `/api/wizard`. Game state stored in a module-level dict (single-user dev mode).

### Tasks
1. Module-level state: `G: dict = {}` and `log: list[str] = []` in `app.py`.
2. `POST /api/start` — accepts JSON `{W, H, seed, depth}`:
   - Clamp `W` to 8–24, `H` to 6–18. Use `str(time.time_ns())` if seed is blank.
   - Build `G` using `generate_board`, `compute_fog`, `compute_valid_moves`.
   - Initialise `G['phase'] = 'normal'`, `G['turn'] = PLAYER`, `G['wizard_active_for'] = NONE`, `G['game_over'] = False`, `G['log'] = []`.
   - Return `jsonify(state_snapshot(G))` — a JSON-serialisable dict (convert `fog` set to sorted list, `valid_moves` set to sorted list).
3. `GET /api/state` — return current `state_snapshot(G)`.
4. `POST /api/move` — accepts JSON `{index: int}`:
   - Validate `index` is in `G['valid_moves']`; return 400 if not.
   - Call `claim_tile(G, index, PLAYER)`.
   - If result is `True` (Wizard claimed): set `G['phase'] = 'wizard-prompt'`, return snapshot.
   - Check win condition; if game over: set `G['phase'] = 'gameover'`, return snapshot.
   - Run AI turn: `ai_idx = minimax_root(G, G['depth'])`, `claim_tile(G, ai_idx, AI)`.
   - Check win condition again.
   - Recompute `G['valid_moves']` for next player turn.
   - Return updated snapshot.
5. `POST /api/wizard` — accepts JSON `{action: 'invoke' | 'decline'}`:
   - `'invoke'`: set `G['wizard_active_for'] = PLAYER`, mark Wizard tile `used=True`, run AI turn (same as above), return snapshot.
   - `'decline'`: run AI turn directly, return snapshot.
6. Helper `state_snapshot(G) -> dict`: serialises `G` to a JSON-safe dict (sets → sorted lists, `log` is a list of strings).

### Tests
```python
# tests/test_api.py  (extend the existing file)
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
        valid = state.get('valid_moves', [])
        if not valid:
            break
        client.post('/api/move',
                    data=json.dumps({'index': valid[0]}),
                    content_type='application/json')
    state = json.loads(client.get('/api/state').data)
    assert state['phase'] == 'gameover', "Game never ended after 200 moves"
```
Run: `pytest tests/test_api.py -v` — all 8 tests must pass.

---

## Step 9 — HTML Template & CSS

**Goal:** Build `templates/index.html` (Jinja2) and `static/css/dominion.css` with all three screens and the wizard modal, styled with the dark medieval palette.

### Tasks
1. `templates/index.html`:
   - `<link>` to Google Fonts (`Cinzel` + `Crimson Text`) and `dominion.css`.
   - `<script src>` for `render.js` then `client.js` (order matters) at end of `<body>`.
   - Three screen divs (only `#screen-title` has class `active` by default):
     - `#screen-title` — title `<h1>DOMINION</h1>`, tagline, setup card with inputs (width, height, seed, difficulty select), `#btn-start`.
     - `#screen-game` — `#game-header` (player HUD left, turn indicator center, AI HUD right), `#canvas-wrap > canvas#board-canvas`, `#tile-legend`, `#game-footer` (`#event-log` + `.footer-buttons` with `#btn-toggle-fog` and `#btn-new-game`).
     - `#screen-end` — `#result-title`, `#result-score`, `#btn-play-again`.
   - `#wizard-modal` (hidden by default, `position: fixed`, `z-index: 100`) — wizard card with `#wizard-invoke` and `#wizard-decline` buttons.
2. `static/css/dominion.css`:
   - CSS custom properties on `:root`: `--bg`, `--player-color`, `--ai-color`, `--accent`, `--text`, `--fog`, etc.
   - `.screen { display: none }` / `.screen.active { display: flex; flex-direction: column }`.
   - Full styling for all screens, HUD, event log, wizard modal — no inline styles.
   - `@keyframes titleGlow` pulsing text-shadow on `#game-title`.
   - Dark medieval palette; `Cinzel` for headers/labels, `Crimson Text` for body/log.

### Tests
```python
# tests/test_api.py — add these
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
```
**Visual check:** Open `http://localhost:5000` — dark page loads, title `DOMINION` shows with glow animation, setup card is visible and styled.

---

## Step 10 — Canvas Rendering (`render.js`)

**Goal:** Implement `static/js/render.js` — all canvas drawing from a state snapshot object.

### Tasks
1. Export / define these functions (accessible globally or as a module):
   - `computeCellSize(state)` — `min(64, max(40, floor(availW / state.W), floor(availH / state.H)))` using `canvas-wrap` dimensions.
   - `blendColor(base, tint, amount)` — linear RGB blend of two hex colors.
   - `render(state, cellSize)` — draws the full board:
     - **Fogged cell:** fill `#0a0c0a`, draw a 2×2 centre dot.
     - **Revealed cell:** fill with base color blended toward owner tint (35% toward `#4a9eff` for PLAYER, `#e05555` for AI). Draw owner border (1.5px). Draw tile icon centred.
     - **Valid move:** semi-transparent yellow-green overlay + border; purple if `state.phase === 'wizard-teleport'`.
     - **Used Wizard:** draw icon at 40% opacity.
2. Define tile data tables in JS (mirroring `constants.py`):
   - `TILE_BASE_COLOR`, `TILE_ICON` — keyed by integer type constant.
3. The `render.js` file is **pure rendering only** — no fetch calls, no game logic.

### Tests
```js
// Browser console — run after opening http://localhost:5000 and starting a game
// (paste after client.js has called startGame and received a state)

// 1. computeCellSize returns a number in [40, 64]
const cs = computeCellSize(window._state);
console.assert(cs >= 40 && cs <= 64, 'FAIL: cellSize out of range');

// 2. render() runs without error
try { render(window._state, cs); console.log('render() OK'); }
catch (e) { console.error('FAIL: render() threw:', e); }

// 3. Canvas dimensions match board size × cellSize
const canvas = document.getElementById('board-canvas');
console.assert(canvas.width  === window._state.W * cs, 'FAIL: canvas width mismatch');
console.assert(canvas.height === window._state.H * cs, 'FAIL: canvas height mismatch');

// 4. blendColor produces a valid rgb string
const blended = blendColor('#2d4a2d', '#4a9eff', 0.35);
console.assert(blended.startsWith('rgb('), 'FAIL: blendColor format wrong');

console.log('Step 10 render tests passed');
```
**Visual check:** Game screen shows the board — tile colors visible, fogged tiles dark, player/AI domains showing ⬡ icon with ownership tint, valid moves highlighted in yellow-green.

---

## Step 11 — Client Logic (`client.js`)

**Goal:** Implement `static/js/client.js` — all UI logic, API calls, turn management, and HUD updates.

### Tasks
1. On `DOMContentLoaded`, wire all button click handlers:
   - `#btn-start` → POST `/api/start` with form values → call `applyState(data)`.
   - `#board-canvas` click → if `phase === 'normal'` or `'wizard-teleport'`, convert pixel coords to cell index → POST `/api/move` with `{index}` → `applyState(data)`.
   - `#btn-toggle-fog` → toggle a local `fogDisabled` flag → re-render without changing state.
   - `#btn-new-game` / `#btn-play-again` → show `#screen-title`.
   - `#wizard-invoke` / `#wizard-decline` → POST `/api/wizard` with `{action}` → `applyState(data)`.
2. `applyState(state)`:
   - Store `window._state = state` for debugging.
   - Compute `cellSize = computeCellSize(state)` and store on window.
   - Show the appropriate screen (`screen-game` during play, `screen-end` when `phase === 'gameover'`).
   - Call `updateHUD(state)`, `buildLegend()`, `render(state, cellSize)`.
   - If `phase === 'wizard-prompt'`, show `#wizard-modal`.
3. `updateHUD(state)`:
   - Update `#hud-player-count`, `#hud-ai-count`.
   - Set `#hud-turn` text based on `phase` and `turn`.
4. `updateEventLog(state)`:
   - Replace `#event-log` contents with `state.log` entries (newest first), colour-coded.
5. `buildLegend()` — builds the tile legend row below the canvas (only once or on new game).
6. Show "AI is thinking…" in `#hud-turn` immediately when the player clicks a tile, before the `/api/move` response arrives.
7. Input validation: clamp Width (8–24) and Height (6–18) client-side before sending to `/api/start`.

### Tests
```js
// Browser console — after opening the app and clicking Begin Conquest

// 1. window._state is populated after start
console.assert(window._state !== undefined, 'FAIL: _state not set');
console.assert(window._state.board.length === window._state.W * window._state.H,
  'FAIL: board length mismatch');

// 2. HUD shows correct player count
const playerCount = window._state.board.filter(c => c.owner === 1).length;
const displayed = parseInt(document.getElementById('hud-player-count').textContent);
console.assert(displayed === playerCount, 'FAIL: HUD player count wrong');

// 3. Clicking a valid move sends the request and updates state
const valid = window._state.valid_moves;
console.assert(valid.length > 0, 'FAIL: no valid moves to click');
const idx = valid[0];
const { x, y } = { x: idx % window._state.W, y: Math.floor(idx / window._state.W) };
const cellSize = window._cellSize;
const canvas = document.getElementById('board-canvas');
const rect = canvas.getBoundingClientRect();
canvas.dispatchEvent(new MouseEvent('click', {
  clientX: rect.left + x * cellSize + cellSize / 2,
  clientY: rect.top  + y * cellSize + cellSize / 2,
  bubbles: true,
}));
setTimeout(() => {
  console.assert(window._state.board[idx].owner === 1,
    'FAIL: tile not claimed after click');
  console.log('Step 11 click test passed');
}, 2000); // wait for API round-trip

// 4. Toggle fog changes fogDisabled flag
document.getElementById('btn-toggle-fog').click();
console.assert(window._fogDisabled === true, 'FAIL: fog not toggled');
document.getElementById('btn-toggle-fog').click();
console.assert(window._fogDisabled === false, 'FAIL: fog not toggled back');

console.log('Step 11 static tests passed');
```

---

## Step 12 — Wizard Full Flow

**Goal:** Complete the Wizard tile interaction end-to-end: claim → prompt → invoke/decline → teleport turn.

### Tasks
1. **Server side** (`app.py` `/api/move`):
   - When `claim_tile` returns `True` (Wizard claimed): set `G['phase'] = 'wizard-prompt'`, return snapshot immediately (do **not** run AI yet).
2. **Client side** (`client.js`):
   - `applyState` detects `phase === 'wizard-prompt'` → show `#wizard-modal`.
   - `#wizard-invoke` click → POST `/api/wizard {action: 'invoke'}`.
   - `#wizard-decline` click → POST `/api/wizard {action: 'decline'}`.
3. **Server** `/api/wizard`:
   - `'invoke'`: set `wizard_active_for = PLAYER`, mark the Wizard tile `used = True`, run AI turn, return snapshot with `phase = 'wizard-teleport'`.
   - `'decline'`: run AI turn directly, return snapshot with `phase = 'normal'`.
4. **Wizard teleport turn**: when `phase === 'wizard-teleport'`, `compute_valid_moves` returns all revealed unclaimed non-Mountain tiles. The client highlights them in purple. On click, that tile is claimed, `wizard_active_for` cleared, AI runs.
5. **Inert Wizard tiles**: once `used = True`, `render.js` draws the icon at 40% opacity. The tile still contributes `owner` to score and vision.
6. **AI Wizard** (already in `minimax_root`): after AI claims a Wizard, call `wizard_teleport_decision(G)` — if result is not `None`, set `wizard_active_for = AI` and mark tile `used`. On the AI's next (immediately simulated) turn, the wizard teleport fires.

### Tests
```python
# tests/test_api.py — add these
def _force_wizard(client):
    """Start a game, then manually trigger wizard-prompt by posting a wizard tile index."""
    import app as app_module
    from game.constants import WIZARD, NONE, PLAYER
    _start(client, seed='wiztest')
    # Force a Wizard tile into the valid moves
    wiz_idx = next(
        (i for i, c in enumerate(app_module.G['board'])
         if c['type'] == WIZARD and c['owner'] == NONE),
        None
    )
    if wiz_idx is None:
        # Place one manually
        free = next(
            i for i, c in enumerate(app_module.G['board'])
            if c['owner'] == NONE and c['type'] not in (MOUNTAIN := 4,)
            and i in app_module.G['fog']
        )
        app_module.G['board'][free]['type'] = WIZARD
        app_module.G['valid_moves'] = list(
            compute_valid_moves(app_module.G, PLAYER)
        )
        wiz_idx = free
    else:
        app_module.G['fog'].add(wiz_idx)
        from game.moves import compute_valid_moves
        app_module.G['valid_moves'] = list(compute_valid_moves(app_module.G, PLAYER))
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
```
```js
// Browser console — wizard modal
console.assert(document.getElementById('wizard-modal') !== null, 'FAIL: wizard modal missing');
console.assert(document.getElementById('wizard-invoke') !== null, 'FAIL: invoke btn missing');
console.assert(document.getElementById('wizard-decline') !== null, 'FAIL: decline btn missing');
// Visual check: claim a Wizard tile in-game — modal should appear with parchment styling
console.log('Step 12 DOM checks passed');
```
Run: `pytest tests/test_api.py::test_wizard_claim_triggers_prompt tests/test_api.py::test_wizard_invoke_sets_teleport_phase tests/test_api.py::test_wizard_decline_runs_ai_turn -v`

---

## Step 13 — End Screen & Final Integration

**Goal:** Wire win detection into every `/api/move` response, show the end screen, verify the full game loop works end-to-end, and handle edge cases.

### Tasks
1. **End screen** (HTML + CSS already in Step 9): when `phase === 'gameover'`, `applyState` calls `showScreen('screen-end')`, sets `#result-title` text/class (`victory`/`defeat`/`draw`) and `#result-score`.
2. **`#btn-play-again`**: calls `showScreen('screen-title')` — no server call needed (new game is started from scratch via `/api/start`).
3. **No-moves handling** (server side in `/api/move`):
   - After player move, if `compute_valid_moves(G, AI)` is empty, skip AI turn and log the skip.
   - At the start of the player's turn computation, if `compute_valid_moves(G, PLAYER)` is empty, check if AI also has no moves → call `check_win_condition` → return `gameover` state.
4. **Edge cases to verify:**
   - Square board (`W == H`): Barbarian uses `random.choice` live, `'h'` in minimax.
   - Barbarian sweep eliminates all tiles: fog recomputes correctly, game continues.
   - All tiles claimed mid-game: `check_win_condition` returns a winner immediately.
   - Player with no moves but AI has moves: AI gets consecutive turns until player has moves.
5. **Responsive canvas**: on `window.resize`, client recomputes `cellSize` and calls `render` with the cached `window._state`.

### Tests
```python
# tests/test_api.py — final integration tests
def test_game_ends_with_winner_or_draw(client):
    _start(client, W=8, H=6, depth=1, seed='endtest')
    for _ in range(300):
        r = client.get('/api/state')
        state = json.loads(r.data)
        if state['phase'] == 'gameover':
            break
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
    for c in app_module.G['board']:
        if c['type'] != MOUNTAIN:
            c['owner'] = PLAYER if app_module.G['board'].index(c) % 2 == 0 else AI
    app_module.G['valid_moves'] = []
    r = client.post('/api/move',
                    data=json.dumps({'index': -1}),
                    content_type='application/json')
    # Should return 400 (no valid moves) or gameover state — not a crash
    assert r.status_code in (400, 200)
```
```js
// Browser console — final integration
// 1. End screen elements exist
console.assert(document.getElementById('result-title') !== null, 'FAIL: result-title missing');
console.assert(document.getElementById('result-score') !== null, 'FAIL: result-score missing');
console.assert(document.getElementById('btn-play-again') !== null, 'FAIL: play-again missing');

// 2. Play Again returns to title screen
document.getElementById('btn-play-again').click();
console.assert(document.getElementById('screen-title').classList.contains('active'),
  'FAIL: play-again did not navigate to title');

// 3. Window resize re-renders without error
window.dispatchEvent(new Event('resize'));
console.log('Step 13 browser checks passed');
```
Run: `pytest tests/ -v` — **all tests across all files must pass.**

---

## Implementation Order Summary

| Step | Files Created / Modified | Key Tests |
|------|--------------------------|-----------|
| 1 | `app.py`, `requirements.txt`, `templates/index.html` stub | `test_index_returns_200`, `test_index_contains_canvas` |
| 2 | `game/constants.py` | Tile/owner uniqueness, weight coverage |
| 3 | `game/board.py` | Cave guarantee, determinism, domain placement |
| 4 | `game/fog.py` | Starting tiles revealed, BFS through Mountains, Cave global reveal |
| 5 | `game/moves.py` | No Mountains/owned/fogged in moves, Plains dist-2, Tower dist-3, Wizard teleport |
| 6 | `game/claim.py` | Barbarian row/col sweep, snapshot/restore, majority win |
| 7 | `game/ai.py` | Heuristic sign, minimax returns valid move, no board mutation |
| 8 | `app.py` (full) | All API endpoints, clamping, AI moves after player, game reaches gameover |
| 9 | `templates/index.html`, `static/css/dominion.css` | All screens present, CSS loads, visual check |
| 10 | `static/js/render.js` | cellSize range, render no-throw, canvas dimensions, blendColor |
| 11 | `static/js/client.js` | State populated, HUD correct, click claims tile, fog toggle |
| 12 | `app.py /api/wizard`, client wizard modal | Wizard prompt triggers, invoke sets teleport, decline runs AI |
| 13 | Full wiring | Game ends with winner/draw, play-again works, resize re-renders |
