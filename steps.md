# Sokoban Solver - Implementation Steps

Each step is small, testable, and builds on the previous. **Do not proceed to the next step until tests pass.**

---

## Phase 1: Core Solver

### Step 1.1: Project Setup

**Goal**: Create project structure and verify environment.

**Tasks**:
1. Create directory structure:
   ```
   sokoban_solver/
   ├── core/
   │   └── __init__.py
   ├── solver/
   │   └── __init__.py
   ├── visualization/
   │   └── __init__.py
   ├── tests/
   │   └── __init__.py
   ├── puzzles/
   └── main.py
   ```
2. Create `requirements.txt` with pytest
3. Create a simple test file

**Test**:
```python
# tests/test_setup.py
def test_imports():
    import core
    import solver
    import visualization
    assert True

def test_python_version():
    import sys
    assert sys.version_info >= (3, 8)
```

**Verify**: `pytest tests/test_setup.py -v`

---

### Step 1.2: Puzzle Parser - Basic Parsing

**Goal**: Parse a puzzle string into a 2D grid.

**Tasks**:
1. Create `core/parser.py`
2. Implement `parse_puzzle_string(puzzle_str) -> list[list[str]]`
3. Handle multi-line input and normalize whitespace

**Test**:
```python
# tests/test_parser.py
from core.parser import parse_puzzle_string

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
    # All rows should be padded to same length
    assert all(len(row) == len(grid[0]) for row in grid)
```

**Verify**: `pytest tests/test_parser.py -v`

---

### Step 1.3: Puzzle Parser - Element Extraction

**Goal**: Extract player, boxes, goals, and walls from parsed grid.

**Tasks**:
1. Add `extract_elements(grid)` function
2. Return dict with: `player`, `boxes`, `goals`, `walls`, `width`, `height`
3. Handle combined characters (`+` = player on goal, `*` = box on goal)

**Test**:
```python
# tests/test_parser.py (add to existing)
from core.parser import parse_puzzle_string, extract_elements

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
```

**Verify**: `pytest tests/test_parser.py -v`

---

### Step 1.4: State Representation

**Goal**: Create hashable state class for A* search.

**Tasks**:
1. Create `core/state.py`
2. Implement `State` class with `player_pos` and `boxes` (frozenset)
3. Implement `__hash__` and `__eq__` for set/dict usage

**Test**:
```python
# tests/test_state.py
from core.state import State

def test_state_creation():
    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (3, 3)]))
    assert state.player_pos == (1, 1)
    assert len(state.boxes) == 2

def test_state_hashable():
    state1 = State(player_pos=(1, 1), boxes=frozenset([(2, 2)]))
    state2 = State(player_pos=(1, 1), boxes=frozenset([(2, 2)]))

    # Same states should hash equal
    assert hash(state1) == hash(state2)

    # Should work in sets
    state_set = {state1}
    assert state2 in state_set

def test_state_equality():
    state1 = State(player_pos=(1, 1), boxes=frozenset([(2, 2)]))
    state2 = State(player_pos=(1, 1), boxes=frozenset([(2, 2)]))
    state3 = State(player_pos=(1, 2), boxes=frozenset([(2, 2)]))

    assert state1 == state2
    assert state1 != state3

def test_state_immutable_boxes():
    boxes = frozenset([(2, 2), (3, 3)])
    state = State(player_pos=(1, 1), boxes=boxes)
    # boxes should be a frozenset (immutable)
    assert isinstance(state.boxes, frozenset)
```

**Verify**: `pytest tests/test_state.py -v`

---

### Step 1.5: Static Puzzle Data

**Goal**: Create class to hold static puzzle information.

**Tasks**:
1. Create `PuzzleStatic` class in `core/state.py`
2. Store: `walls`, `goals`, `width`, `height`
3. Add factory method `from_elements(elements)`

**Test**:
```python
# tests/test_state.py (add to existing)
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements

def test_puzzle_static_creation():
    puzzle = """####
#.$#
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)

    assert static.width == 4
    assert static.height == 3
    assert (1, 1) in static.goals
    assert (0, 0) in static.walls

def test_puzzle_static_walls_frozenset():
    puzzle = """####
#  #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)

    assert isinstance(static.walls, frozenset)
    assert isinstance(static.goals, frozenset)
```

**Verify**: `pytest tests/test_state.py -v`

---

### Step 1.6: Player Reachability (BFS)

**Goal**: Determine which squares the player can reach without pushing boxes.

**Tasks**:
1. Create `core/moves.py`
2. Implement `get_reachable_positions(player_pos, boxes, walls, width, height)`
3. Return set of all positions player can reach via BFS

**Test**:
```python
# tests/test_moves.py
from core.moves import get_reachable_positions

def test_reachable_open_room():
    # Player at (1,1) in 3x3 open room
    walls = frozenset([(0,0), (1,0), (2,0), (3,0),
                       (0,1), (3,1),
                       (0,2), (3,2),
                       (0,3), (1,3), (2,3), (3,3)])
    boxes = frozenset()
    reachable = get_reachable_positions((1, 1), boxes, walls, 4, 4)

    assert (1, 1) in reachable
    assert (2, 1) in reachable
    assert (1, 2) in reachable
    assert (2, 2) in reachable
    # Walls not reachable
    assert (0, 0) not in reachable

def test_reachable_blocked_by_box():
    walls = frozenset([(0,0), (1,0), (2,0), (3,0),
                       (0,1), (3,1),
                       (0,2), (3,2),
                       (0,3), (1,3), (2,3), (3,3)])
    boxes = frozenset([(2, 1)])  # Box blocks path
    reachable = get_reachable_positions((1, 1), boxes, walls, 4, 4)

    assert (1, 1) in reachable
    assert (2, 1) not in reachable  # Box position
    assert (1, 2) in reachable  # Can go around

def test_reachable_completely_blocked():
    walls = frozenset([(0,0), (1,0), (2,0),
                       (0,1), (2,1),
                       (0,2), (1,2), (2,2)])
    boxes = frozenset([(1, 1)])  # Box at only open spot
    reachable = get_reachable_positions((1, 1), boxes, walls, 3, 3)

    # Player is on the box position? This shouldn't happen in valid state
    # Let's test player adjacent to box
    reachable = get_reachable_positions((0, 1), frozenset([(1, 1)]), walls, 3, 3)
    assert (1, 1) not in reachable  # Can't walk through box
```

**Verify**: `pytest tests/test_moves.py -v`

---

### Step 1.7: Move Generation

**Goal**: Generate all valid box pushes from a state.

**Tasks**:
1. Add `generate_moves(state, puzzle_static)` to `core/moves.py`
2. For each box, check if player can reach push position
3. Check if push destination is valid (not wall, not box)
4. Return list of `(direction, new_state)` tuples

**Test**:
```python
# tests/test_moves.py (add to existing)
from core.moves import generate_moves, get_reachable_positions
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements

def test_generate_simple_push():
    puzzle = """#####
#   #
# $ #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    moves = generate_moves(state, static)

    # Should be able to push box up (player below box)
    directions = [m[0] for m in moves]
    assert 'U' in directions

def test_generate_blocked_push():
    puzzle = """#####
#   #
##$ #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    moves = generate_moves(state, static)

    # Can't push left (wall behind box)
    # Can push up
    assert len(moves) >= 1

def test_move_updates_state():
    puzzle = """#####
#   #
# $ #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    moves = generate_moves(state, static)

    # Find the up push
    up_move = next((m for m in moves if m[0] == 'U'), None)
    assert up_move is not None

    new_state = up_move[1]
    # Player moves to where box was
    assert new_state.player_pos == (2, 2)
    # Box moves up one
    assert (2, 1) in new_state.boxes
    assert (2, 2) not in new_state.boxes
```

**Verify**: `pytest tests/test_moves.py -v`

---

### Step 1.8: Goal Check

**Goal**: Detect when puzzle is solved (all boxes on goals).

**Tasks**:
1. Add `is_goal_state(state, puzzle_static)` to `core/state.py`
2. Return True if all boxes are on goal positions

**Test**:
```python
# tests/test_state.py (add to existing)
from core.state import State, PuzzleStatic, is_goal_state

def test_goal_state_achieved():
    goals = frozenset([(2, 2), (3, 3)])
    static = PuzzleStatic(walls=frozenset(), goals=goals, width=5, height=5)

    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (3, 3)]))
    assert is_goal_state(state, static) == True

def test_goal_state_not_achieved():
    goals = frozenset([(2, 2), (3, 3)])
    static = PuzzleStatic(walls=frozenset(), goals=goals, width=5, height=5)

    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (4, 4)]))
    assert is_goal_state(state, static) == False

def test_goal_state_partial():
    goals = frozenset([(2, 2), (3, 3)])
    static = PuzzleStatic(walls=frozenset(), goals=goals, width=5, height=5)

    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (1, 1)]))
    assert is_goal_state(state, static) == False
```

**Verify**: `pytest tests/test_state.py -v`

---

### Step 1.9: Basic Heuristic (Manhattan Distance)

**Goal**: Implement simple heuristic to guide A* search.

**Tasks**:
1. Create `solver/heuristic.py`
2. Implement `manhattan_heuristic(state, goals)` - sum of minimum Manhattan distances from each box to nearest goal

**Test**:
```python
# tests/test_heuristic.py
from solver.heuristic import manhattan_heuristic

def test_heuristic_at_goal():
    boxes = frozenset([(2, 2)])
    goals = frozenset([(2, 2)])

    h = manhattan_heuristic(boxes, goals)
    assert h == 0

def test_heuristic_one_away():
    boxes = frozenset([(2, 2)])
    goals = frozenset([(2, 3)])

    h = manhattan_heuristic(boxes, goals)
    assert h == 1

def test_heuristic_multiple_boxes():
    boxes = frozenset([(1, 1), (3, 3)])
    goals = frozenset([(1, 2), (3, 4)])

    h = manhattan_heuristic(boxes, goals)
    # Box at (1,1) to goal (1,2) = 1
    # Box at (3,3) to goal (3,4) = 1
    assert h == 2

def test_heuristic_picks_nearest_goal():
    boxes = frozenset([(2, 2)])
    goals = frozenset([(2, 3), (5, 5)])

    h = manhattan_heuristic(boxes, goals)
    # Should pick distance to (2,3) = 1, not (5,5) = 6
    assert h == 1
```

**Verify**: `pytest tests/test_heuristic.py -v`

---

### Step 1.10: A* Search - Basic Implementation

**Goal**: Implement A* search that can solve trivial puzzles.

**Tasks**:
1. Create `solver/astar.py`
2. Implement `solve(initial_state, puzzle_static)` with A* algorithm
3. Use priority queue (heapq) with f-score
4. Return solution path (list of directions) or None

**Test**:
```python
# tests/test_solver.py
from solver.astar import solve
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements

def test_solve_trivial_one_push():
    puzzle = """####
#. #
#$ #
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert result is not None
    assert result['success'] == True
    assert result['solution'] == 'U'  # One push up

def test_solve_trivial_two_pushes():
    puzzle = """#####
#.  #
#   #
#$  #
#@  #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert result is not None
    assert result['success'] == True
    assert len(result['solution']) == 2
    assert result['solution'] == 'UU'

def test_solve_already_solved():
    puzzle = """####
#* #
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert result['success'] == True
    assert result['solution'] == ''  # No moves needed
```

**Verify**: `pytest tests/test_solver.py -v`

---

### Step 1.11: A* Search - Handle No Solution

**Goal**: Properly detect when no solution exists.

**Tasks**:
1. Update `solve()` to return failure when queue exhausted
2. Add `states_explored` to result statistics

**Test**:
```python
# tests/test_solver.py (add to existing)
def test_solve_impossible_corner():
    # Box in corner with no goal there
    puzzle = """####
#$ #
#  #
#@.#
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert result['success'] == False
    assert 'states_explored' in result['stats']

def test_solve_returns_stats():
    puzzle = """####
#. #
#$ #
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert 'stats' in result
    assert 'states_explored' in result['stats']
    assert result['stats']['states_explored'] >= 1
```

**Verify**: `pytest tests/test_solver.py -v`

---

### Step 1.12: Precomputed Goal Distances

**Goal**: Replace Manhattan heuristic with actual maze distances.

**Tasks**:
1. Add `precompute_goal_distances(walls, goals, width, height)` to `solver/heuristic.py`
2. BFS from each goal to compute actual distances
3. Update heuristic to use precomputed distances

**Test**:
```python
# tests/test_heuristic.py (add to existing)
from solver.heuristic import precompute_goal_distances, distance_heuristic

def test_precompute_open_room():
    walls = frozenset([(0,0), (1,0), (2,0), (3,0), (4,0),
                       (0,1), (4,1),
                       (0,2), (4,2),
                       (0,3), (4,3),
                       (0,4), (1,4), (2,4), (3,4), (4,4)])
    goals = frozenset([(2, 2)])

    distances = precompute_goal_distances(walls, goals, 5, 5)

    # Distance from goal to itself is 0
    assert distances[(2, 2, 0)] == 0
    # Adjacent squares are 1 away
    assert distances[(2, 1, 0)] == 1
    assert distances[(1, 2, 0)] == 1

def test_precompute_with_wall_obstacle():
    # Wall blocks direct path
    walls = frozenset([(0,0), (1,0), (2,0), (3,0), (4,0),
                       (0,1), (4,1),
                       (0,2), (2,2), (4,2),  # Wall at (2,2)
                       (0,3), (4,3),
                       (0,4), (1,4), (2,4), (3,4), (4,4)])
    goals = frozenset([(1, 2)])

    distances = precompute_goal_distances(walls, goals, 5, 5)

    # (3,2) must go around the wall at (2,2)
    # Path: (3,2) -> (3,1) -> (2,1) -> (1,1) -> (1,2) = 4 steps
    # Or: (3,2) -> (3,3) -> (2,3) -> (1,3) -> (1,2) = 4 steps
    assert distances[(3, 2, 0)] == 4

def test_distance_heuristic_uses_precomputed():
    walls = frozenset([(0,0), (1,0), (2,0), (3,0),
                       (0,1), (3,1),
                       (0,2), (3,2),
                       (0,3), (1,3), (2,3), (3,3)])
    goals = frozenset([(1, 1)])

    distances = precompute_goal_distances(walls, goals, 4, 4)
    boxes = frozenset([(2, 2)])

    h = distance_heuristic(boxes, goals, distances)

    # Actual maze distance, not Manhattan
    assert h == 2  # (2,2) -> (2,1) -> (1,1)
```

**Verify**: `pytest tests/test_heuristic.py -v`

---

### Step 1.13: Integrate Better Heuristic into Solver

**Goal**: Update A* solver to use precomputed distances.

**Tasks**:
1. Precompute distances during puzzle initialization
2. Store in `PuzzleStatic` or pass separately
3. Update solver to use `distance_heuristic`

**Test**:
```python
# tests/test_solver.py (add to existing)
def test_solve_uses_distance_heuristic():
    # Puzzle where Manhattan would give wrong estimate
    puzzle = """######
#.   #
#### #
#$   #
#@   #
######"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert result['success'] == True
    # Solver should still find optimal path
```

**Verify**: `pytest tests/test_solver.py -v`

---

### Step 1.14: Corner Deadlock Detection

**Goal**: Detect boxes stuck in corners.

**Tasks**:
1. Create `solver/deadlock.py`
2. Implement `is_corner_deadlock(pos, walls, goals)`
3. Add `compute_static_deadlocks(walls, goals, width, height)` to precompute all corner deadlocks

**Test**:
```python
# tests/test_deadlock.py
from solver.deadlock import is_corner_deadlock, compute_static_deadlocks

def test_corner_deadlock_top_left():
    walls = frozenset([(0,0), (1,0), (2,0),
                       (0,1), (2,1),
                       (0,2), (1,2), (2,2)])
    goals = frozenset([(1, 1)])  # Goal not in corner

    # Position (1,1) is not a corner
    assert is_corner_deadlock((1, 1), walls, goals) == False

    # But if we check a corner position without wall...
    # Let's create a proper corner
    walls2 = frozenset([(0,0), (1,0), (2,0), (3,0),
                        (0,1), (3,1),
                        (0,2), (3,2),
                        (0,3), (1,3), (2,3), (3,3)])
    goals2 = frozenset([(2, 2)])

    # (1,1) has walls at (0,1) and (1,0) - top-left corner
    assert is_corner_deadlock((1, 1), walls2, goals2) == True

def test_corner_deadlock_is_goal():
    walls = frozenset([(0,0), (1,0), (2,0), (3,0),
                       (0,1), (3,1),
                       (0,2), (3,2),
                       (0,3), (1,3), (2,3), (3,3)])
    goals = frozenset([(1, 1)])  # Goal IS the corner

    # Not a deadlock if it's a goal
    assert is_corner_deadlock((1, 1), walls, goals) == False

def test_compute_static_deadlocks():
    walls = frozenset([(0,0), (1,0), (2,0), (3,0),
                       (0,1), (3,1),
                       (0,2), (3,2),
                       (0,3), (1,3), (2,3), (3,3)])
    goals = frozenset([(2, 2)])

    deadlocks = compute_static_deadlocks(walls, goals, 4, 4)

    # All four corners should be deadlocks (except the goal corner)
    assert (1, 1) in deadlocks  # top-left inner corner
    assert (2, 1) in deadlocks  # top-right inner corner
    assert (1, 2) in deadlocks  # bottom-left inner corner
    assert (2, 2) not in deadlocks  # This is the goal
```

**Verify**: `pytest tests/test_deadlock.py -v`

---

### Step 1.15: Integrate Static Deadlock Detection

**Goal**: Skip states where box is on static deadlock square.

**Tasks**:
1. Add `deadlock_squares` to `PuzzleStatic`
2. Update `generate_moves()` to skip pushes that create deadlocks
3. Or check in A* loop before adding to queue

**Test**:
```python
# tests/test_solver.py (add to existing)
def test_solver_prunes_corner_deadlock():
    # Pushing box into corner should be pruned
    puzzle = """#####
#   #
#$  #
#@. #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    # Should find solution going right then down, not up into corner
    assert result['success'] == True
    # First move should NOT be pushing up into corner
    assert result['solution'][0] != 'U' or len(result['solution']) > 1
```

**Verify**: `pytest tests/test_solver.py -v`

---

### Step 1.16: Freeze Deadlock Detection

**Goal**: Detect boxes that cannot move in any direction.

**Tasks**:
1. Add `is_freeze_deadlock(boxes, walls, goals)` to `solver/deadlock.py`
2. Check each box for mobility (can it be pushed in any direction?)

**Test**:
```python
# tests/test_deadlock.py (add to existing)
from solver.deadlock import is_freeze_deadlock

def test_freeze_deadlock_single_box():
    walls = frozenset([(0,0), (1,0), (2,0), (3,0), (4,0),
                       (0,1), (4,1),
                       (0,2), (2,2), (4,2),  # Wall at (2,2)
                       (0,3), (4,3),
                       (0,4), (1,4), (2,4), (3,4), (4,4)])
    goals = frozenset([(1, 1)])

    # Box at (1,2) with wall above at (1,0) - not frozen if can push left/right
    boxes = frozenset([(1, 2)])
    assert is_freeze_deadlock(boxes, walls, goals) == False

    # Box at (1,2) with wall to left (0,2) and wall to right (2,2)
    # Can still push up or down
    assert is_freeze_deadlock(boxes, walls, goals) == False

def test_freeze_deadlock_box_against_wall_and_box():
    walls = frozenset([(0,0), (1,0), (2,0), (3,0),
                       (0,1), (3,1),
                       (0,2), (3,2),
                       (0,3), (1,3), (2,3), (3,3)])
    goals = frozenset([(2, 2)])

    # Two boxes side by side against top wall
    boxes = frozenset([(1, 1), (2, 1)])
    # (1,1) blocked: wall above, box to right, wall to left
    # (2,1) blocked: wall above, box to left, wall to right
    # Both frozen and not both on goals
    result = is_freeze_deadlock(boxes, walls, goals)
    assert result == True

def test_freeze_deadlock_on_goal_ok():
    walls = frozenset([(0,0), (1,0), (2,0),
                       (0,1), (2,1),
                       (0,2), (1,2), (2,2)])
    goals = frozenset([(1, 1)])

    # Box frozen but on goal - not a deadlock
    boxes = frozenset([(1, 1)])
    # Actually this box IS movable since no obstructions
    # Let's make it properly frozen
    walls2 = frozenset([(0,0), (1,0), (2,0),
                        (0,1), (2,1),
                        (0,2), (1,2), (2,2)])
    # Box at (1,1) with walls at (0,1), (2,1), (1,0), (1,2) - frozen
    # But it's on goal so OK
    assert is_freeze_deadlock(frozenset([(1, 1)]), walls2, frozenset([(1, 1)])) == False
```

**Verify**: `pytest tests/test_deadlock.py -v`

---

### Step 1.17: 2x2 Box Deadlock Detection

**Goal**: Detect four boxes forming an immovable square.

**Tasks**:
1. Add `is_2x2_deadlock(boxes, walls, goals)` to `solver/deadlock.py`

**Test**:
```python
# tests/test_deadlock.py (add to existing)
from solver.deadlock import is_2x2_deadlock

def test_2x2_deadlock():
    walls = frozenset()  # No walls needed for this test
    goals = frozenset([(10, 10)])  # Goals elsewhere

    # Four boxes in square
    boxes = frozenset([(1, 1), (2, 1), (1, 2), (2, 2)])

    assert is_2x2_deadlock(boxes, walls, goals) == True

def test_2x2_no_deadlock_missing_box():
    walls = frozenset()
    goals = frozenset([(10, 10)])

    # Only three boxes
    boxes = frozenset([(1, 1), (2, 1), (1, 2)])

    assert is_2x2_deadlock(boxes, walls, goals) == False

def test_2x2_deadlock_with_walls():
    # 2x2 can also form with walls
    walls = frozenset([(2, 1), (2, 2)])  # Walls on right side
    goals = frozenset([(10, 10)])

    # Two boxes + two walls form deadlock
    boxes = frozenset([(1, 1), (1, 2)])

    # This is actually a wall-based freeze, not pure 2x2
    # For pure 2x2, all four must be boxes
    assert is_2x2_deadlock(boxes, walls, goals) == False

def test_2x2_all_goals_ok():
    walls = frozenset()
    goals = frozenset([(1, 1), (2, 1), (1, 2), (2, 2)])  # All four are goals

    boxes = frozenset([(1, 1), (2, 1), (1, 2), (2, 2)])

    # All boxes on goals - not a deadlock
    assert is_2x2_deadlock(boxes, walls, goals) == False
```

**Verify**: `pytest tests/test_deadlock.py -v`

---

### Step 1.18: Combined Deadlock Check

**Goal**: Create unified deadlock detection function.

**Tasks**:
1. Add `is_deadlocked(state, puzzle_static)` that combines all checks
2. Order checks by cost (static first, then dynamic)

**Test**:
```python
# tests/test_deadlock.py (add to existing)
from solver.deadlock import is_deadlocked
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements

def test_is_deadlocked_static():
    puzzle = """####
#$ #
#. #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)

    # Box in corner (1,1) - static deadlock
    state = State(player_pos=(2, 2), boxes=frozenset([(1, 1)]))

    assert is_deadlocked(state, static) == True

def test_is_deadlocked_2x2():
    puzzle = """######
#    #
# $$ #
# $$ #
#....#
######"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)

    # Four boxes in 2x2 formation
    state = State(player_pos=(1, 1), boxes=frozenset([(2, 2), (3, 2), (2, 3), (3, 3)]))

    assert is_deadlocked(state, static) == True

def test_is_deadlocked_valid_state():
    puzzle = """####
#  #
#$.#
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    # Initial state should not be deadlocked
    assert is_deadlocked(initial, static) == False
```

**Verify**: `pytest tests/test_deadlock.py -v`

---

### Step 1.19: Integrate All Deadlock Detection into Solver

**Goal**: Update solver to use combined deadlock detection.

**Tasks**:
1. Call `is_deadlocked()` before adding states to queue
2. Verify solver prunes deadlocked states efficiently

**Test**:
```python
# tests/test_solver.py (add to existing)
def test_solver_prunes_2x2_deadlock():
    puzzle = """######
#    #
# $$ #
#  . #
#@...#
######"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    # Should find a solution that avoids creating 2x2
    assert result['success'] == True

def test_solver_with_deadlock_detection_faster():
    # A puzzle where deadlock detection significantly prunes search space
    puzzle = """#######
#     #
# $$$ #
# ... #
#@    #
#######"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert result['success'] == True
    # Should explore relatively few states
    assert result['stats']['states_explored'] < 10000
```

**Verify**: `pytest tests/test_solver.py -v`

---

### Step 1.20: Terminal Visualization

**Goal**: Display puzzle state in terminal.

**Tasks**:
1. Create `visualization/terminal.py`
2. Implement `display_state(state, puzzle_static)`
3. Print colored ASCII representation

**Test**:
```python
# tests/test_visualization.py
from visualization.terminal import display_state, state_to_string
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements

def test_state_to_string():
    puzzle = """####
#$.#
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    output = state_to_string(state, static)

    assert '#' in output
    assert '$' in output or '*' in output
    assert '@' in output or '+' in output

def test_state_to_string_box_on_goal():
    puzzle = """####
#* #
#@ #
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    output = state_to_string(state, static)

    # Box on goal should show as *
    assert '*' in output
```

**Verify**: `pytest tests/test_visualization.py -v`

---

### Step 1.21: Solution Playback

**Goal**: Animate solution step by step.

**Tasks**:
1. Add `apply_move(state, direction, puzzle_static)` to `core/moves.py`
2. Add `playback_solution(initial_state, solution, puzzle_static)` to visualization

**Test**:
```python
# tests/test_moves.py (add to existing)
from core.moves import apply_move

def test_apply_move_up():
    puzzle = """#####
#   #
# $ #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    new_state = apply_move(state, 'U', static)

    # Player moved up to box position
    assert new_state.player_pos == (2, 2)
    # Box moved up
    assert (2, 1) in new_state.boxes
    assert (2, 2) not in new_state.boxes

def test_apply_move_sequence():
    puzzle = """#####
#.  #
#   #
#$  #
#@  #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    state = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    # Apply two moves
    state = apply_move(state, 'U', static)
    state = apply_move(state, 'U', static)

    # Box should now be on goal
    assert (1, 1) in state.boxes
```

**Verify**: `pytest tests/test_moves.py -v`

---

### Step 1.22: CLI Interface

**Goal**: Create command-line entry point.

**Tasks**:
1. Update `main.py` with argument parsing
2. Support: puzzle file input, timeout, verbose mode
3. Print solution and statistics

**Test**:
```python
# tests/test_cli.py
import subprocess
import os

def test_cli_solve_file(tmp_path):
    # Create a test puzzle file
    puzzle_file = tmp_path / "test_puzzle.txt"
    puzzle_file.write_text("""####
#. #
#$ #
#@ #
####""")

    result = subprocess.run(
        ['python', 'main.py', str(puzzle_file)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert 'Solution' in result.stdout or 'solution' in result.stdout.lower()

def test_cli_no_solution(tmp_path):
    puzzle_file = tmp_path / "impossible.txt"
    puzzle_file.write_text("""####
#$ #
#  #
#@.#
####""")

    result = subprocess.run(
        ['python', 'main.py', str(puzzle_file)],
        capture_output=True,
        text=True
    )

    # Should handle gracefully
    assert 'No solution' in result.stdout or 'no solution' in result.stdout.lower()

def test_cli_help():
    result = subprocess.run(
        ['python', 'main.py', '--help'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert 'usage' in result.stdout.lower() or 'help' in result.stdout.lower()
```

**Verify**: `pytest tests/test_cli.py -v`

---

### Step 1.23: Multi-Box Puzzle Tests

**Goal**: Verify solver works on realistic puzzles.

**Tasks**:
1. Create test puzzles with 3-5 boxes
2. Verify optimal solutions
3. Add performance assertions

**Test**:
```python
# tests/test_solver_integration.py
from solver.astar import solve
from core.state import State, PuzzleStatic
from core.parser import parse_puzzle_string, extract_elements
import time

def test_three_box_puzzle():
    puzzle = """########
#      #
# $$$  #
# ...  #
#@     #
########"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    start = time.time()
    result = solve(initial, static)
    elapsed = time.time() - start

    assert result['success'] == True
    assert elapsed < 5.0  # Should solve in under 5 seconds

def test_microban_level_1():
    # Classic easy puzzle
    puzzle = """####
# .#
#  ###
#*@  #
#  $ #
#  ###
####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert result['success'] == True
    # Known optimal solution length
    assert len(result['solution']) <= 10

def test_solver_returns_optimal():
    # Simple puzzle with known optimal
    puzzle = """#####
#   #
#.$.#
#   #
# @ #
#####"""
    grid = parse_puzzle_string(puzzle)
    elements = extract_elements(grid)
    static = PuzzleStatic.from_elements(elements)
    initial = State(player_pos=elements['player'], boxes=frozenset(elements['boxes']))

    result = solve(initial, static)

    assert result['success'] == True
    # Optimal is 2 pushes (left or right)
    assert len(result['solution']) == 2
```

**Verify**: `pytest tests/test_solver_integration.py -v`

---

### Step 1.24: Solver API Wrapper

**Goal**: Create clean API for web integration.

**Tasks**:
1. Create `solve_puzzle(puzzle_string, timeout=60, max_states=10000000)` wrapper
2. Return standardized result dict matching specs
3. Handle all error cases gracefully

**Test**:
```python
# tests/test_solver_api.py
from solver.astar import solve_puzzle

def test_api_success():
    puzzle = """####
#. #
#$ #
#@ #
####"""

    result = solve_puzzle(puzzle)

    assert result['success'] == True
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

    assert result['success'] == False
    assert 'error' in result
    assert 'reason' in result

def test_api_invalid_puzzle():
    puzzle = """not a valid puzzle"""

    result = solve_puzzle(puzzle)

    assert result['success'] == False
    assert result['reason'] == 'invalid_puzzle'

def test_api_timeout():
    # Very hard puzzle that will timeout
    puzzle = """##########
#        #
# $$$$$$ #
# ...... #
#@       #
##########"""

    result = solve_puzzle(puzzle, timeout=0.1)  # Very short timeout

    # Should timeout gracefully
    assert result['success'] == False
    assert result['reason'] == 'timeout'
```

**Verify**: `pytest tests/test_solver_api.py -v`

---

## Phase 2: Web Interface

**Prerequisites**: All Phase 1 tests must pass before starting Phase 2.

---

### Step 2.1: Flask Setup

**Goal**: Create basic Flask application.

**Tasks**:
1. Create `web/app.py`
2. Add Flask and flask-cors to requirements.txt
3. Create basic route that returns "OK"

**Test**:
```python
# tests/test_web.py
import pytest
from web.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_app_runs(client):
    response = client.get('/')
    assert response.status_code == 200
```

**Verify**: `pytest tests/test_web.py -v`

---

### Step 2.2: Puzzle List API

**Goal**: API endpoint to list available puzzles.

**Tasks**:
1. Add `PRESET_PUZZLES` dict to app
2. Create `/api/puzzles` endpoint
3. Return JSON list of puzzle metadata

**Test**:
```python
# tests/test_web.py (add to existing)
def test_get_puzzles(client):
    response = client.get('/api/puzzles')

    assert response.status_code == 200
    data = response.get_json()
    assert 'puzzles' in data
    assert len(data['puzzles']) > 0
    assert 'id' in data['puzzles'][0]
    assert 'name' in data['puzzles'][0]
```

**Verify**: `pytest tests/test_web.py -v`

---

### Step 2.3: Get Single Puzzle API

**Goal**: API endpoint to get puzzle by ID.

**Tasks**:
1. Create `/api/puzzle/<puzzle_id>` endpoint
2. Return puzzle string and 2D grid
3. Handle 404 for invalid ID

**Test**:
```python
# tests/test_web.py (add to existing)
def test_get_puzzle_valid(client):
    response = client.get('/api/puzzle/easy_1')

    assert response.status_code == 200
    data = response.get_json()
    assert 'id' in data
    assert 'puzzle' in data
    assert 'grid' in data

def test_get_puzzle_invalid(client):
    response = client.get('/api/puzzle/nonexistent')

    assert response.status_code == 404
```

**Verify**: `pytest tests/test_web.py -v`

---

### Step 2.4: Solve API Endpoint

**Goal**: API endpoint to solve submitted puzzles.

**Tasks**:
1. Create `/api/solve` POST endpoint
2. Accept puzzle string in JSON body
3. Call solver and return result

**Test**:
```python
# tests/test_web.py (add to existing)
import json

def test_solve_valid_puzzle(client):
    puzzle = """####
#. #
#$ #
#@ #
####"""

    response = client.post(
        '/api/solve',
        data=json.dumps({'puzzle': puzzle}),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == True
    assert 'solution' in data
    assert 'stats' in data

def test_solve_no_puzzle(client):
    response = client.post(
        '/api/solve',
        data=json.dumps({}),
        content_type='application/json'
    )

    assert response.status_code == 400

def test_solve_impossible_puzzle(client):
    puzzle = """####
#$ #
#  #
#@.#
####"""

    response = client.post(
        '/api/solve',
        data=json.dumps({'puzzle': puzzle}),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] == False
```

**Verify**: `pytest tests/test_web.py -v`

---

### Step 2.5: HTML Template

**Goal**: Create main HTML page.

**Tasks**:
1. Create `web/templates/index.html`
2. Add basic structure with sidebar and main content
3. Include placeholders for puzzle display and controls

**Test**:
```python
# tests/test_web.py (add to existing)
def test_index_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sokoban' in response.data
```

**Verify**: `pytest tests/test_web.py -v` and manual browser check at http://localhost:5000

---

### Step 2.6: Static Files Setup

**Goal**: Set up CSS and JavaScript files.

**Tasks**:
1. Create `web/static/css/style.css`
2. Create `web/static/js/app.js`
3. Create `web/static/js/renderer.js`
4. Verify files load in browser

**Test**: Manual verification in browser - open Network tab and verify CSS/JS load with 200 status.

---

### Step 2.7: Puzzle Renderer (Canvas)

**Goal**: Render puzzle on HTML canvas.

**Tasks**:
1. Implement `PuzzleRenderer` class in `renderer.js`
2. Draw walls, floors, goals, boxes, player
3. Test with static puzzle data

**Test**: Manual verification - puzzle should display correctly in browser.

---

### Step 2.8: Puzzle Selection UI

**Goal**: Load and display puzzle list in sidebar.

**Tasks**:
1. Fetch puzzles from `/api/puzzles` on page load
2. Create clickable buttons for each puzzle
3. Load and render selected puzzle

**Test**: Manual verification - clicking puzzle buttons should render puzzles.

---

### Step 2.9: Solve Button Integration

**Goal**: Connect solve button to API.

**Tasks**:
1. Send selected puzzle to `/api/solve`
2. Display loading state
3. Show solution statistics on success

**Test**:
```python
# tests/test_web_integration.py
def test_full_solve_flow(client):
    # Get puzzle list
    puzzles = client.get('/api/puzzles').get_json()['puzzles']

    # Get first puzzle
    puzzle_id = puzzles[0]['id']
    puzzle_data = client.get(f'/api/puzzle/{puzzle_id}').get_json()

    # Solve it
    response = client.post(
        '/api/solve',
        data=json.dumps({'puzzle': puzzle_data['puzzle']}),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert response.get_json()['success'] == True
```

**Verify**: `pytest tests/test_web_integration.py -v` and manual browser test

---

### Step 2.10: Solution State Reconstruction

**Goal**: Reconstruct puzzle state at each move.

**Tasks**:
1. Implement `getStateAtMove(moveIndex)` in JavaScript
2. Start from initial state and apply moves
3. Return player position and box positions

**Test**: Manual verification - step through solution and verify state updates correctly.

---

### Step 2.11: Playback Controls

**Goal**: Implement play/pause/reset/step controls.

**Tasks**:
1. Implement play button (auto-advance)
2. Implement pause button
3. Implement reset button
4. Implement step forward button
5. Add speed slider

**Test**: Manual verification - all controls should work correctly.

---

### Step 2.12: Progress Display

**Goal**: Show current move number and total.

**Tasks**:
1. Display "Move X / Y" during playback
2. Update on each step
3. Show "Complete!" at end

**Test**: Manual verification - progress should update during playback.

---

### Step 2.13: Error Handling UI

**Goal**: Display errors gracefully in UI.

**Tasks**:
1. Show error message when solve fails
2. Show loading spinner during solve
3. Handle network errors

**Test**: Manual verification - test with invalid puzzle, very hard puzzle, network disconnection.

---

### Step 2.14: End-to-End Web Tests

**Goal**: Automated browser tests for full flow.

**Tasks**:
1. Add playwright or selenium to requirements
2. Test full flow: select puzzle → solve → playback

**Test**:
```python
# tests/test_e2e.py (optional, requires playwright)
# Run: pytest tests/test_e2e.py

def test_solve_and_playback(page):
    page.goto('http://localhost:5000')

    # Click first puzzle
    page.click('.puzzle-btn:first-child')

    # Click solve
    page.click('#solve-btn')

    # Wait for solution
    page.wait_for_selector('#controls:not(.hidden)')

    # Verify stats shown
    assert page.locator('#stats').is_visible()
```

**Verify**: `pytest tests/test_e2e.py -v` (if implemented)

---

## Phase 3: Puzzle Builder

**Prerequisites**: All Phase 2 tests must pass before starting Phase 3.

---

### Step 3.1: Validation API

**Goal**: API endpoint to validate custom puzzles.

**Tasks**:
1. Create `/api/validate` POST endpoint
2. Check: exactly one player, boxes == goals, proper walls
3. Return errors and warnings

**Test**:
```python
# tests/test_web.py (add to existing)
def test_validate_valid_puzzle(client):
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', ' ', '#'],
        ['#', '$', ' ', '#'],
        ['#', '@', ' ', '#'],
        ['#', '#', '#', '#']
    ]

    response = client.post(
        '/api/validate',
        data=json.dumps({'grid': grid}),
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data['valid'] == True

def test_validate_no_player(client):
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', ' ', '#'],
        ['#', '$', ' ', '#'],
        ['#', ' ', ' ', '#'],
        ['#', '#', '#', '#']
    ]

    response = client.post(
        '/api/validate',
        data=json.dumps({'grid': grid}),
        content_type='application/json'
    )

    data = response.get_json()
    assert data['valid'] == False
    assert any('player' in e.lower() for e in data['errors'])

def test_validate_box_goal_mismatch(client):
    grid = [
        ['#', '#', '#', '#'],
        ['#', '.', '.', '#'],  # 2 goals
        ['#', '$', ' ', '#'],  # 1 box
        ['#', '@', ' ', '#'],
        ['#', '#', '#', '#']
    ]

    response = client.post(
        '/api/validate',
        data=json.dumps({'grid': grid}),
        content_type='application/json'
    )

    data = response.get_json()
    assert len(data['warnings']) > 0
```

**Verify**: `pytest tests/test_web.py::test_validate* -v`

---

### Step 3.2: Builder HTML Page

**Goal**: Create puzzle builder page.

**Tasks**:
1. Create `web/templates/builder.html` or add builder section to index
2. Add grid canvas and tool palette
3. Add grid size controls

**Test**: Manual verification - page loads with empty grid.

---

### Step 3.3: Builder Tool Selection

**Goal**: Implement tool palette.

**Tasks**:
1. Create tool buttons: Wall, Floor, Goal, Box, Player, Eraser
2. Highlight selected tool
3. Store current tool in JavaScript state

**Test**: Manual verification - clicking tools should highlight them.

---

### Step 3.4: Grid Click Handling

**Goal**: Place elements on grid click.

**Tasks**:
1. Add click listener to canvas
2. Calculate clicked cell from coordinates
3. Place current tool's element in grid
4. Re-render grid

**Test**: Manual verification - clicking grid should place elements.

---

### Step 3.5: Player Uniqueness

**Goal**: Ensure only one player exists.

**Tasks**:
1. When placing player, remove existing player first
2. Apply same logic for `+` (player on goal)

**Test**: Manual verification - placing second player should remove first.

---

### Step 3.6: Grid Resize

**Goal**: Allow changing grid dimensions.

**Tasks**:
1. Add width/height input controls
2. Implement resize that preserves existing content
3. Pad or truncate as needed

**Test**: Manual verification - resize should preserve content where possible.

---

### Step 3.7: Validate Button

**Goal**: Validate custom puzzle in builder.

**Tasks**:
1. Add "Validate" button
2. Send grid to `/api/validate`
3. Display errors/warnings

**Test**: Manual verification - validation messages should display.

---

### Step 3.8: Solve Custom Puzzle

**Goal**: Solve puzzle from builder.

**Tasks**:
1. Convert grid to puzzle string
2. Send to `/api/solve`
3. Display solution or error

**Test**: Manual verification - building and solving a puzzle should work.

---

### Step 3.9: Clear Grid

**Goal**: Reset grid to empty state.

**Tasks**:
1. Add "Clear" button
2. Reset all cells to empty space
3. Re-render

**Test**: Manual verification - clear should empty the grid.

---

### Step 3.10: Builder Integration

**Goal**: Integrate builder with main app.

**Tasks**:
1. Add tab/mode switching between Solver and Builder
2. Share renderer code
3. Allow custom puzzles to be solved and played back

**Test**: Manual verification - full flow: build → validate → solve → playback.

---

## Verification Checklist

Before marking a phase complete, verify:

### Phase 1 Complete
- [ ] All parser tests pass
- [ ] All state tests pass
- [ ] All move tests pass
- [ ] All heuristic tests pass
- [ ] All deadlock tests pass
- [ ] All solver tests pass
- [ ] CLI works for provided puzzles
- [ ] Terminal visualization works

### Phase 2 Complete
- [ ] All API tests pass
- [ ] Web page loads correctly
- [ ] Puzzle selection works
- [ ] Solve button returns results
- [ ] Solution playback works
- [ ] All controls function

### Phase 3 Complete
- [ ] Validation API works
- [ ] Builder tool selection works
- [ ] Grid editing works
- [ ] Custom puzzles can be solved
- [ ] Full integration works

---

## Running All Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific phase
pytest tests/test_parser.py tests/test_state.py tests/test_moves.py tests/test_heuristic.py tests/test_deadlock.py tests/test_solver.py -v

# Run web tests only
pytest tests/test_web.py -v
```
