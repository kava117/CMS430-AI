# Sokoban Solver - Project Specifications

## Project Overview

A Python-based Sokoban puzzle solver that uses A* search with aggressive deadlock detection to find optimal solutions. The project includes both a command-line solver and visualization capabilities to display puzzle states and solution playback.

## Table of Contents

1. [Core Requirements](#core-requirements)
2. [Input/Output Specifications](#inputoutput-specifications)
3. [Algorithm Design](#algorithm-design)
4. [State Representation](#state-representation)
5. [Heuristic Function](#heuristic-function)
6. [Deadlock Detection](#deadlock-detection)
7. [Visualization](#visualization)
8. [Module Architecture](#module-architecture)
9. [Performance Targets](#performance-targets)
10. [Testing Requirements](#testing-requirements)

---

## Core Requirements

### Functional Requirements

1. **Puzzle Parsing**: Read standard Sokoban text format
2. **Optimal Solving**: Find minimum-push solutions using A* search
3. **Deadlock Detection**: Identify and prune unsolvable states aggressively
4. **Solution Output**: Display sequence of push moves (U/D/L/R)
5. **Visualization**: Graphical display of puzzle and solution playback
6. **Error Handling**: Gracefully handle invalid puzzles and unsolvable states

### Non-Functional Requirements

1. **Performance**: Solve 90% of standard puzzles in <10 seconds
2. **Optimality**: Guarantee shortest solution (fewest pushes)
3. **Stability**: No crashes on malformed or unsolvable input
4. **Usability**: Clear output and intuitive visualization
5. **Extensibility**: Modular design for future enhancements

---

## Input/Output Specifications

### Input Format

Standard Sokoban text format with the following characters:

| Character | Meaning |
|-----------|---------|
| `#` | Wall |
| `@` | Player |
| `$` | Box |
| `.` | Goal/Storage location |
| `+` | Player on goal |
| `*` | Box on goal |
| ` ` (space) | Empty floor |

**Example Puzzle:**
```
####
# .#
#  ###
#*@  #
#  $ #
#  ###
####
```

**Input Sources:**
- String literal (for testing)
- Text file (`.txt` extension)
- Standard input (stdin)

### Output Format

#### Solution Found
```
Puzzle: example_puzzle_01.txt
Solution found in 12 pushes!

Solution: RRUULLDDRRUL

Statistics:
  States explored: 1,247
  Time elapsed: 0.23 seconds
  Solution length: 12 pushes
  Optimality: Guaranteed (A*)

Move sequence:
  1. R (Right)
  2. R (Right)
  3. U (Up)
  ...
```

#### No Solution
```
Puzzle: impossible_puzzle.txt
No solution exists.

Statistics:
  States explored: 45,892
  Time elapsed: 3.71 seconds
  Termination reason: State space exhausted
```

#### Timeout
```
Puzzle: very_hard_puzzle.txt
Search terminated: timeout reached.

Statistics:
  States explored: 10,000,000
  Time elapsed: 60.00 seconds
  Termination reason: Maximum states explored
  Note: A solution may exist but was not found within limits.
```

---

## Algorithm Design

### A* Search Overview

The solver uses A* search with the evaluation function:

```
f(n) = g(n) + h(n)
```

Where:
- `g(n)`: Cost from start to node n (number of pushes)
- `h(n)`: Admissible heuristic estimate from n to goal
- `f(n)`: Estimated total cost through n

### Search Process

```python
1. Initialize:
   - Parse puzzle and extract initial state
   - Precompute goal distances (BFS from each goal)
   - Identify static deadlock squares
   - Create priority queue with start state

2. Main loop:
   while priority queue not empty:
     a. Pop state with lowest f-score
     b. Check if goal state (all boxes on goals)
     c. Generate all valid box pushes
     d. For each successor:
        - Check deadlock conditions
        - Skip if already visited or deadlocked
        - Compute g and h scores
        - Add to priority queue
     e. Add current state to closed set

3. Termination:
   - Return solution path if goal reached
   - Return None if queue empty (no solution)
   - Return timeout if limits exceeded
```

### Move Generation Strategy

We count **pushes**, not individual player steps:

1. For each box, try pushing in all 4 directions
2. Check if push destination is valid (not wall, not another box)
3. Use BFS to verify player can reach push position
4. Generate new state with updated box and player positions

**Key insight**: Player position after push is where the box was before push.

---

## State Representation

### Hybrid Approach

**Static Components** (computed once):
```python
class PuzzleStatic:
    walls: frozenset[tuple[int, int]]      # Wall positions
    goals: frozenset[tuple[int, int]]      # Goal positions
    width: int                              # Grid width
    height: int                             # Grid height
    goal_distances: dict                    # Precomputed distances
    deadlock_squares: frozenset             # Unsolvable positions
```

**Dynamic State** (changes during search):
```python
class State:
    player_pos: tuple[int, int]             # Player (x, y)
    boxes: frozenset[tuple[int, int]]       # Box positions
    
    def __hash__(self):
        return hash((self.player_pos, self.boxes))
    
    def __eq__(self, other):
        return (self.player_pos == other.player_pos and 
                self.boxes == other.boxes)
```

### Rationale

- **Efficiency**: Frozensets are hashable and enable O(1) state lookups
- **Memory**: Don't duplicate static data in every state
- **Clarity**: Separation of concerns (static vs dynamic)

---

## Heuristic Function

### Design Goal

Create an **admissible** heuristic (never overestimates) that's as **tight** as possible (close to true cost).

### Precomputation Phase

At puzzle load, run BFS from each goal square:

```python
def precompute_goal_distances(walls, goals, width, height):
    """
    For each goal, compute minimum push distance to all reachable squares.
    
    Returns:
        dict[(x, y, goal_idx)] = min_distance
    """
    distances = {}
    
    for goal_idx, goal_pos in enumerate(goals):
        # BFS from this goal
        queue = deque([(goal_pos, 0)])
        visited = {goal_pos}
        
        while queue:
            (x, y), dist = queue.popleft()
            distances[(x, y, goal_idx)] = dist
            
            # Explore neighbors
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                new_pos = (x + dx, y + dy)
                
                if (new_pos not in walls and 
                    new_pos not in visited and
                    0 <= new_pos[0] < width and 
                    0 <= new_pos[1] < height):
                    visited.add(new_pos)
                    queue.append((new_pos, dist + 1))
    
    return distances
```

### Heuristic Calculation

```python
def heuristic(state, goals, goal_distances):
    """
    Sum of minimum distances from each box to nearest goal.
    Uses precomputed actual distances (not Manhattan).
    
    Returns:
        int: Lower bound on remaining pushes
        float('inf'): If any box unreachable to any goal (implicit deadlock)
    """
    total = 0
    
    for box_x, box_y in state.boxes:
        min_dist = float('inf')
        
        # Find nearest goal
        for goal_idx in range(len(goals)):
            key = (box_x, box_y, goal_idx)
            if key in goal_distances:
                min_dist = min(min_dist, goal_distances[key])
        
        if min_dist == float('inf'):
            return float('inf')  # Box can't reach any goal
        
        total += min_dist
    
    return total
```

### Why This Works

1. **Lower bound**: Each box needs at least `min_distance` pushes to reach a goal
2. **Admissible**: Ignores box-box interactions (which only increase cost)
3. **Informed**: Uses actual maze distances, not straight-line
4. **Fast**: O(num_boxes × num_goals) lookup, all distances precomputed

### Alternative Heuristics (Future)

- **Hungarian algorithm**: Optimal box-to-goal assignment
- **Pattern databases**: Precompute subproblem solutions
- **Weighted sum**: Combine multiple heuristics

---

## Deadlock Detection

Aggressive pruning is critical for performance. We implement multiple deadlock detection strategies.

### 1. Static Deadlocks (Precomputed)

Identify squares where a box would always be stuck:

#### Corner Deadlocks
```python
def is_corner_deadlock(x, y, walls, goals):
    """
    Box in corner (two adjacent walls) that's not a goal.
    
    Examples:
        # #        # #
        #$    or    $#
        
    Where $ is the box position.
    """
    if (x, y) in goals:
        return False
    
    top_wall = (x, y-1) in walls
    bottom_wall = (x, y+1) in walls
    left_wall = (x-1, y) in walls
    right_wall = (x+1, y) in walls
    
    # Check all four corners
    return ((top_wall and left_wall) or
            (top_wall and right_wall) or
            (bottom_wall and left_wall) or
            (bottom_wall and right_wall))
```

#### Wall Deadlocks
```python
def is_wall_deadlock(x, y, walls, goals):
    """
    Box against a wall with no goals accessible along that wall.
    
    Example:
        ######
        #    #
        #$   #   <- Box against left wall, no goals on this wall
        #    #
        ######
    """
    if (x, y) in goals:
        return False
    
    # Check if against a wall
    against_left = (x-1, y) in walls
    against_right = (x+1, y) in walls
    against_top = (x, y-1) in walls
    against_bottom = (x, y+1) in walls
    
    # For each wall, check if any goal exists along that wall
    if against_left or against_right:
        wall_x = x - 1 if against_left else x + 1
        has_goal = any(
            gx == x and ((gx - 1, gy) in walls if against_left 
                        else (gx + 1, gy) in walls)
            for gx, gy in goals
        )
        if not has_goal:
            return True
    
    if against_top or against_bottom:
        wall_y = y - 1 if against_top else y + 1
        has_goal = any(
            gy == y and ((gx, gy - 1) in walls if against_top 
                        else (gx, gy + 1) in walls)
            for gx, gy in goals
        )
        if not has_goal:
            return True
    
    return False
```

### 2. Freeze Deadlocks

Boxes that cannot move in any direction:

```python
def is_freeze_deadlock(boxes, walls, goals):
    """
    Detect boxes that are completely immobile.
    A frozen box not on a goal = deadlock.
    """
    frozen_boxes = set()
    box_set = set(boxes)
    
    for bx, by in boxes:
        if (bx, by) in goals:
            continue
        
        can_move = False
        
        # Try all four directions
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            new_box_pos = (bx + dx, by + dy)
            push_from_pos = (bx - dx, by - dy)
            
            # Can this box be pushed?
            if (new_box_pos not in walls and 
                new_box_pos not in box_set and
                push_from_pos not in walls):
                can_move = True
                break
        
        if not can_move:
            frozen_boxes.add((bx, by))
    
    return len(frozen_boxes) > 0
```

### 3. Line Deadlocks

Multiple boxes in a row against a wall without enough goals:

```python
def is_line_deadlock(boxes, walls, goals):
    """
    Consecutive boxes along a wall with insufficient goals.
    
    Example:
        ######
        #$$$ #  <- 3 boxes against wall
        #.   #  <- Only 1 goal
        ######
    """
    box_set = set(boxes)
    
    # Group boxes by row
    rows = {}
    for x, y in boxes:
        if y not in rows:
            rows[y] = []
        rows[y].append(x)
    
    # Check horizontal lines
    for y, x_list in rows.items():
        if len(x_list) < 2:
            continue
        
        x_list.sort()
        
        # Find consecutive segments
        segments = []
        current_segment = [x_list[0]]
        
        for i in range(1, len(x_list)):
            if x_list[i] == current_segment[-1] + 1:
                current_segment.append(x_list[i])
            else:
                if len(current_segment) >= 2:
                    segments.append(current_segment)
                current_segment = [x_list[i]]
        
        if len(current_segment) >= 2:
            segments.append(current_segment)
        
        # Check each segment
        for segment in segments:
            # Is this segment against a wall?
            against_top = all((x, y-1) in walls for x in segment)
            against_bottom = all((x, y+1) in walls for x in segment)
            
            if against_top or against_bottom:
                # Count goals in this segment
                goals_in_segment = sum(
                    1 for x in segment if (x, y) in goals
                )
                
                if goals_in_segment < len(segment):
                    return True
    
    # Similar check for vertical lines (columns)
    cols = {}
    for x, y in boxes:
        if x not in cols:
            cols[x] = []
        cols[x].append(y)
    
    for x, y_list in cols.items():
        if len(y_list) < 2:
            continue
        
        y_list.sort()
        
        segments = []
        current_segment = [y_list[0]]
        
        for i in range(1, len(y_list)):
            if y_list[i] == current_segment[-1] + 1:
                current_segment.append(y_list[i])
            else:
                if len(current_segment) >= 2:
                    segments.append(current_segment)
                current_segment = [y_list[i]]
        
        if len(current_segment) >= 2:
            segments.append(current_segment)
        
        for segment in segments:
            against_left = all((x-1, y) in walls for y in segment)
            against_right = all((x+1, y) in walls for y in segment)
            
            if against_left or against_right:
                goals_in_segment = sum(
                    1 for y in segment if (x, y) in goals
                )
                
                if goals_in_segment < len(segment):
                    return True
    
    return False
```

### 4. 2×2 Square Deadlock

Four boxes forming a square:

```python
def is_2x2_deadlock(boxes, walls, goals):
    """
    Four boxes in a 2×2 configuration are immovable.
    Deadlock unless all four are on goals.
    
    Example:
        $$
        $$
    """
    box_set = set(boxes)
    
    for x, y in boxes:
        square = [
            (x, y),
            (x+1, y),
            (x, y+1),
            (x+1, y+1)
        ]
        
        if all(pos in box_set for pos in square):
            if not all(pos in goals for pos in square):
                return True
    
    return False
```

### 5. Bipartite Matching Deadlock

Check if boxes can reach enough distinct goals:

```python
def has_bipartite_deadlock(boxes, goals, goal_distances):
    """
    Verify that each box can reach at least one goal.
    Advanced: Could use Hungarian algorithm for optimal matching.
    """
    for bx, by in boxes:
        can_reach_goal = False
        
        for goal_idx in range(len(goals)):
            key = (bx, by, goal_idx)
            if key in goal_distances:
                can_reach_goal = True
                break
        
        if not can_reach_goal:
            return True  # This box can't reach any goal
    
    return False
```

### Combined Deadlock Check

```python
def is_deadlocked(state, puzzle_static):
    """
    Apply all deadlock detection strategies.
    Returns True if state is provably unsolvable.
    """
    boxes = state.boxes
    
    # Quick check: any box on precomputed deadlock square?
    if any(box in puzzle_static.deadlock_squares for box in boxes):
        return True
    
    # Dynamic deadlock checks
    if is_freeze_deadlock(boxes, puzzle_static.walls, puzzle_static.goals):
        return True
    
    if is_line_deadlock(boxes, puzzle_static.walls, puzzle_static.goals):
        return True
    
    if is_2x2_deadlock(boxes, puzzle_static.walls, puzzle_static.goals):
        return True
    
    # Note: Bipartite check happens in heuristic (returns inf)
    
    return False
```

---

## Visualization

### Phase 1: Terminal Visualization (ASCII)

Simple text-based display for debugging and initial testing.

#### Display Function
```python
def display_state(state, puzzle_static):
    """
    Print current puzzle state to terminal.
    """
    grid = [[' ' for _ in range(puzzle_static.width)] 
            for _ in range(puzzle_static.height)]
    
    # Draw walls
    for x, y in puzzle_static.walls:
        grid[y][x] = '#'
    
    # Draw goals
    for x, y in puzzle_static.goals:
        grid[y][x] = '.'
    
    # Draw boxes
    for x, y in state.boxes:
        if (x, y) in puzzle_static.goals:
            grid[y][x] = '*'  # Box on goal
        else:
            grid[y][x] = '$'
    
    # Draw player
    px, py = state.player_pos
    if (px, py) in puzzle_static.goals:
        grid[py][px] = '+'  # Player on goal
    else:
        grid[py][px] = '@'
    
    # Print grid
    for row in grid:
        print(''.join(row))
    print()
```

#### Solution Playback
```python
def playback_solution(initial_state, solution, puzzle_static, delay=0.5):
    """
    Animate solution in terminal with time delay.
    """
    import time
    import os
    
    current_state = initial_state
    
    print("Initial state:")
    display_state(current_state, puzzle_static)
    time.sleep(delay)
    
    for i, move in enumerate(solution):
        os.system('clear')  # or 'cls' on Windows
        
        print(f"Move {i+1}/{len(solution)}: {move}")
        current_state = apply_move(current_state, move, puzzle_static)
        display_state(current_state, puzzle_static)
        
        time.sleep(delay)
    
    print("Solution complete!")
```

### Phase 2: Web Interface with Flask Backend

**Prerequisites**: Solver must be fully working and encapsulated as a self-contained component before starting this phase.

#### Architecture Overview

```
┌─────────────┐         HTTP          ┌─────────────┐
│   Browser   │ ◄─────────────────► │ Flask Server │
│  (Frontend) │    JSON API          │  (Backend)   │
└─────────────┘                       └──────┬──────┘
                                             │
                                             │ imports
                                             │
                                      ┌──────▼──────┐
                                      │   Solver    │
                                      │  (Core API) │
                                      └─────────────┘
```

The key principle is **encapsulation**: the solver is a self-contained module that the Flask backend imports and uses. No solver code needs to be modified for web integration.

#### Backend Design (Flask)

**API Endpoint Specification:**

```python
# app.py - Flask Backend

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from solver.astar import solve_puzzle
from core.parser import parse_puzzle_string
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for development

# Pre-designed puzzles
PRESET_PUZZLES = {
    "easy_1": """
####
#  ###
#  $ #
# .@ #
#    #
######
""".strip(),
    "easy_2": """
  #####
  #   #
  #$  #
### .@#
#   ###
#    #
######
""".strip(),
    "medium_1": """
########
#      #
# .**$ #
# .**$ #
# @    #
########
""".strip(),
    "hard_1": """
    #####
    #   #
    #$  #
  ###  $##
  #  $ $ #
### # ## #
#   # ## #
# $  $   #
##### ####
    #  #
    ####
""".strip()
}

@app.route('/')
def index():
    """Serve the main HTML page."""
    return render_template('index.html')

@app.route('/api/puzzles', methods=['GET'])
def get_puzzles():
    """
    Return list of available preset puzzles.
    
    Response format:
    {
        "puzzles": [
            {"id": "easy_1", "name": "Easy Puzzle 1", "difficulty": "easy"},
            ...
        ]
    }
    """
    puzzles = [
        {"id": "easy_1", "name": "Easy Puzzle 1", "difficulty": "easy"},
        {"id": "easy_2", "name": "Easy Puzzle 2", "difficulty": "easy"},
        {"id": "medium_1", "name": "Medium Puzzle 1", "difficulty": "medium"},
        {"id": "hard_1", "name": "Hard Puzzle 1", "difficulty": "hard"}
    ]
    
    return jsonify({"puzzles": puzzles})

@app.route('/api/puzzle/<puzzle_id>', methods=['GET'])
def get_puzzle(puzzle_id):
    """
    Return a specific puzzle by ID.
    
    Response format:
    {
        "id": "easy_1",
        "puzzle": "####\n#  ###\n...",
        "grid": [["#", "#", ...], [...], ...]
    }
    """
    if puzzle_id not in PRESET_PUZZLES:
        return jsonify({"error": "Puzzle not found"}), 404
    
    puzzle_string = PRESET_PUZZLES[puzzle_id]
    
    # Convert to 2D grid for frontend rendering
    grid = [list(line) for line in puzzle_string.split('\n')]
    
    return jsonify({
        "id": puzzle_id,
        "puzzle": puzzle_string,
        "grid": grid
    })

@app.route('/api/solve', methods=['POST'])
def solve():
    """
    Solve a submitted puzzle.
    
    Request format:
    {
        "puzzle": "####\n#  ###\n# $  #\n...",
        "timeout": 60,  # optional, default 60
        "max_states": 10000000  # optional
    }
    
    Response format (success):
    {
        "success": true,
        "solution": "RRUULLDDRRUL",
        "moves": ["R", "R", "U", "U", "L", "L", "D", "D", "R", "R", "U", "L"],
        "length": 12,
        "stats": {
            "states_explored": 1247,
            "time_elapsed": 0.23,
            "optimal": true
        },
        "initial_state": {
            "player": [3, 2],
            "boxes": [[2, 2], [4, 3]],
            "goals": [[2, 3], [3, 3]]
        }
    }
    
    Response format (failure):
    {
        "success": false,
        "error": "No solution found",
        "reason": "timeout|unsolvable|invalid_puzzle",
        "stats": {
            "states_explored": 10000000,
            "time_elapsed": 60.0
        }
    }
    """
    try:
        data = request.get_json()
        puzzle_string = data.get('puzzle')
        timeout = data.get('timeout', 60)
        max_states = data.get('max_states', 10000000)
        
        if not puzzle_string:
            return jsonify({
                "success": False,
                "error": "No puzzle provided"
            }), 400
        
        # Call the solver (encapsulated, no modifications needed)
        result = solve_puzzle(
            puzzle_string,
            timeout=timeout,
            max_states=max_states
        )
        
        if result['success']:
            return jsonify({
                "success": True,
                "solution": result['solution'],  # "RRUULLD..."
                "moves": list(result['solution']),  # ["R", "R", "U", ...]
                "length": len(result['solution']),
                "stats": result['stats'],
                "initial_state": result['initial_state']
            })
        else:
            return jsonify({
                "success": False,
                "error": result['error'],
                "reason": result['reason'],
                "stats": result.get('stats', {})
            })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "reason": "server_error"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

**Solver API Contract:**

The solver must provide a clean interface:

```python
# solver/astar.py

def solve_puzzle(puzzle_string, timeout=60, max_states=10000000):
    """
    Solve a Sokoban puzzle.
    
    Args:
        puzzle_string: Standard Sokoban text format
        timeout: Maximum time in seconds
        max_states: Maximum states to explore
    
    Returns:
        dict with structure:
        {
            'success': bool,
            'solution': str,  # "RRUULLD..." or None
            'stats': {
                'states_explored': int,
                'time_elapsed': float,
                'optimal': bool
            },
            'initial_state': {
                'player': [x, y],
                'boxes': [[x1, y1], [x2, y2], ...],
                'goals': [[x1, y1], [x2, y2], ...]
            },
            'error': str,  # if success=False
            'reason': str  # 'timeout', 'unsolvable', 'invalid_puzzle'
        }
    """
    # Implementation details...
```

#### Frontend Design (HTML/CSS/JavaScript)

**File Structure:**
```
sokoban_solver/
├── app.py                 # Flask backend
├── templates/
│   └── index.html         # Main page
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       ├── app.js         # Main application logic
│       ├── renderer.js    # Puzzle rendering
│       └── solver.js      # API communication
```

**Main Page Layout:**

```html
<!-- templates/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sokoban Solver</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <div class="container">
        <header>
            <h1>Sokoban Solver</h1>
            <p>Select a puzzle and watch the optimal solution!</p>
        </header>
        
        <main>
            <div class="sidebar">
                <h2>Select Puzzle</h2>
                <div id="puzzle-list"></div>
                
                <button id="solve-btn" disabled>Solve Puzzle</button>
                
                <div id="stats" class="stats hidden">
                    <h3>Statistics</h3>
                    <p>States explored: <span id="states">-</span></p>
                    <p>Time elapsed: <span id="time">-</span></p>
                    <p>Solution length: <span id="length">-</span></p>
                </div>
            </div>
            
            <div class="main-content">
                <div id="puzzle-display">
                    <p class="placeholder">Select a puzzle to begin</p>
                </div>
                
                <div id="controls" class="controls hidden">
                    <button id="play-btn">▶ Play</button>
                    <button id="pause-btn">⏸ Pause</button>
                    <button id="reset-btn">↺ Reset</button>
                    <button id="step-btn">Step →</button>
                    
                    <div class="speed-control">
                        <label>Speed:</label>
                        <input type="range" id="speed-slider" min="1" max="10" value="3">
                        <span id="speed-value">3</span>
                    </div>
                    
                    <div class="progress">
                        <span>Move: <span id="current-move">0</span> / <span id="total-moves">0</span></span>
                    </div>
                </div>
                
                <div id="status" class="status"></div>
            </div>
        </main>
    </div>
    
    <script src="{{ url_for('static', filename='js/renderer.js') }}"></script>
    <script src="{{ url_for('static', filename='js/solver.js') }}"></script>
    <script src="{{ url_for('static', filename='js/app.js') }}"></script>
</body>
</html>
```

**Rendering Logic (JavaScript):**

```javascript
// static/js/renderer.js

class PuzzleRenderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.tileSize = 40;
        this.colors = {
            wall: '#5a5a5a',
            floor: '#d4c4a8',
            goal: '#90ee90',
            box: '#8b4513',
            boxOnGoal: '#228b22',
            player: '#4169e1',
            playerOnGoal: '#1e90ff'
        };
    }
    
    render(grid, playerPos, boxes, goals) {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        const rows = grid.length;
        const cols = grid[0].length;
        
        // Set canvas size
        this.canvas.width = cols * this.tileSize;
        this.canvas.height = rows * this.tileSize;
        
        // Draw each tile
        for (let y = 0; y < rows; y++) {
            for (let x = 0; x < cols; x++) {
                const char = grid[y][x];
                this.drawTile(x, y, char, playerPos, boxes, goals);
            }
        }
    }
    
    drawTile(x, y, char, playerPos, boxes, goals) {
        const px = x * this.tileSize;
        const py = y * this.tileSize;
        
        // Draw based on character
        if (char === '#') {
            this.drawWall(px, py);
        } else {
            this.drawFloor(px, py);
            
            // Check if goal
            if (goals.some(g => g[0] === x && g[1] === y)) {
                this.drawGoal(px, py);
            }
            
            // Check if box
            const isBox = boxes.some(b => b[0] === x && b[1] === y);
            const isGoal = goals.some(g => g[0] === x && g[1] === y);
            
            if (isBox) {
                if (isGoal) {
                    this.drawBoxOnGoal(px, py);
                } else {
                    this.drawBox(px, py);
                }
            }
            
            // Check if player
            if (playerPos && playerPos[0] === x && playerPos[1] === y) {
                if (isGoal) {
                    this.drawPlayerOnGoal(px, py);
                } else {
                    this.drawPlayer(px, py);
                }
            }
        }
    }
    
    drawWall(x, y) {
        this.ctx.fillStyle = this.colors.wall;
        this.ctx.fillRect(x, y, this.tileSize, this.tileSize);
        this.ctx.strokeStyle = '#3a3a3a';
        this.ctx.strokeRect(x, y, this.tileSize, this.tileSize);
    }
    
    drawFloor(x, y) {
        this.ctx.fillStyle = this.colors.floor;
        this.ctx.fillRect(x, y, this.tileSize, this.tileSize);
    }
    
    drawGoal(x, y) {
        this.ctx.fillStyle = this.colors.goal;
        this.ctx.fillRect(x + 8, y + 8, this.tileSize - 16, this.tileSize - 16);
    }
    
    drawBox(x, y) {
        this.ctx.fillStyle = this.colors.box;
        this.ctx.fillRect(x + 5, y + 5, this.tileSize - 10, this.tileSize - 10);
        this.ctx.strokeStyle = '#654321';
        this.ctx.strokeRect(x + 5, y + 5, this.tileSize - 10, this.tileSize - 10);
    }
    
    drawBoxOnGoal(x, y) {
        this.ctx.fillStyle = this.colors.boxOnGoal;
        this.ctx.fillRect(x + 5, y + 5, this.tileSize - 10, this.tileSize - 10);
        this.ctx.strokeStyle = '#1a5c1a';
        this.ctx.strokeRect(x + 5, y + 5, this.tileSize - 10, this.tileSize - 10);
    }
    
    drawPlayer(x, y) {
        this.ctx.fillStyle = this.colors.player;
        this.ctx.beginPath();
        this.ctx.arc(x + this.tileSize/2, y + this.tileSize/2, 
                     this.tileSize/3, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    drawPlayerOnGoal(x, y) {
        this.ctx.fillStyle = this.colors.playerOnGoal;
        this.ctx.beginPath();
        this.ctx.arc(x + this.tileSize/2, y + this.tileSize/2, 
                     this.tileSize/3, 0, 2 * Math.PI);
        this.ctx.fill();
    }
}
```

**Application Logic:**

```javascript
// static/js/app.js

let currentPuzzle = null;
let solution = null;
let currentMove = 0;
let isPlaying = false;
let playInterval = null;
let renderer = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Create canvas for rendering
    const displayDiv = document.getElementById('puzzle-display');
    displayDiv.innerHTML = '<canvas id="puzzle-canvas"></canvas>';
    
    renderer = new PuzzleRenderer('puzzle-canvas');
    
    // Load puzzle list
    await loadPuzzleList();
    
    // Setup event listeners
    document.getElementById('solve-btn').addEventListener('click', solvePuzzle);
    document.getElementById('play-btn').addEventListener('click', playSolution);
    document.getElementById('pause-btn').addEventListener('click', pauseSolution);
    document.getElementById('reset-btn').addEventListener('click', resetSolution);
    document.getElementById('step-btn').addEventListener('click', stepForward);
    
    const speedSlider = document.getElementById('speed-slider');
    speedSlider.addEventListener('input', (e) => {
        document.getElementById('speed-value').textContent = e.target.value;
    });
});

async function loadPuzzleList() {
    const response = await fetch('/api/puzzles');
    const data = await response.json();
    
    const listDiv = document.getElementById('puzzle-list');
    listDiv.innerHTML = '';
    
    data.puzzles.forEach(puzzle => {
        const btn = document.createElement('button');
        btn.className = 'puzzle-btn';
        btn.textContent = puzzle.name;
        btn.dataset.puzzleId = puzzle.id;
        btn.addEventListener('click', () => loadPuzzle(puzzle.id));
        listDiv.appendChild(btn);
    });
}

async function loadPuzzle(puzzleId) {
    const response = await fetch(`/api/puzzle/${puzzleId}`);
    currentPuzzle = await response.json();
    
    // Enable solve button
    document.getElementById('solve-btn').disabled = false;
    
    // Hide controls and stats
    document.getElementById('controls').classList.add('hidden');
    document.getElementById('stats').classList.add('hidden');
    
    // Render puzzle
    const initialState = extractInitialState(currentPuzzle.grid);
    renderer.render(
        currentPuzzle.grid,
        initialState.player,
        initialState.boxes,
        initialState.goals
    );
    
    document.getElementById('status').textContent = 'Puzzle loaded. Click "Solve Puzzle" to begin.';
}

async function solvePuzzle() {
    document.getElementById('status').textContent = 'Solving...';
    document.getElementById('solve-btn').disabled = true;
    
    const response = await fetch('/api/solve', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({puzzle: currentPuzzle.puzzle})
    });
    
    const result = await response.json();
    
    if (result.success) {
        solution = result;
        currentMove = 0;
        
        // Show stats
        document.getElementById('states').textContent = result.stats.states_explored;
        document.getElementById('time').textContent = result.stats.time_elapsed.toFixed(2) + 's';
        document.getElementById('length').textContent = result.length;
        document.getElementById('stats').classList.remove('hidden');
        
        // Show controls
        document.getElementById('total-moves').textContent = result.length;
        document.getElementById('current-move').textContent = '0';
        document.getElementById('controls').classList.remove('hidden');
        
        document.getElementById('status').textContent = 
            `Solution found! ${result.length} pushes. Press Play to watch.`;
    } else {
        document.getElementById('status').textContent = 
            `Failed: ${result.error}`;
    }
    
    document.getElementById('solve-btn').disabled = false;
}

function playSolution() {
    if (isPlaying) return;
    
    isPlaying = true;
    const speed = parseInt(document.getElementById('speed-slider').value);
    const delay = 1000 / speed;
    
    playInterval = setInterval(() => {
        if (currentMove < solution.length) {
            stepForward();
        } else {
            pauseSolution();
        }
    }, delay);
}

function pauseSolution() {
    isPlaying = false;
    if (playInterval) {
        clearInterval(playInterval);
        playInterval = null;
    }
}

function resetSolution() {
    pauseSolution();
    currentMove = 0;
    updateDisplay();
}

function stepForward() {
    if (currentMove < solution.length) {
        currentMove++;
        updateDisplay();
    }
}

function updateDisplay() {
    const state = getStateAtMove(currentMove);
    renderer.render(
        currentPuzzle.grid,
        state.player,
        state.boxes,
        solution.initial_state.goals
    );
    document.getElementById('current-move').textContent = currentMove;
}

// Helper functions...
function extractInitialState(grid) {
    // Extract player, boxes, goals from grid
    // Implementation details...
}

function getStateAtMove(moveIndex) {
    // Reconstruct state after moveIndex moves
    // Implementation details...
}
```

### Phase 3: Custom Puzzle Builder

Allow users to design their own puzzles through an interactive editor.

#### Design Principles

1. **Storage Format**: Maintain grid representation internally, convert to standard text format for solver
2. **Validation**: Check puzzle validity before allowing solve
3. **Encapsulation**: Puzzle builder is separate from solver - just generates valid input

#### Builder Interface

**Layout:**

```
┌─────────────────────────────────────────────────────┐
│  Sokoban Puzzle Builder                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  [New] [Load] [Save]          Grid Size: 8 x 8     │
│                                                     │
│  Tools:                        ┌─────────────┐     │
│  ◉ Wall (#)                    │             │     │
│  ○ Floor ( )                   │             │     │
│  ○ Goal (.)                    │  Edit Grid  │     │
│  ○ Box ($)                     │    Here     │     │
│  ○ Player (@)                  │             │     │
│  ○ Eraser                      │             │     │
│                                └─────────────┘     │
│  [Clear Grid]                                      │
│  [Validate Puzzle]                                 │
│  [Solve This Puzzle]                              │
│                                                     │
│  Status: Ready to build                            │
└─────────────────────────────────────────────────────┘
```

#### Backend Extensions

Add new API endpoints:

```python
@app.route('/api/validate', methods=['POST'])
def validate_puzzle():
    """
    Validate a user-created puzzle.
    
    Request format:
    {
        "grid": [["#", "#", ...], [...], ...]
    }
    
    Response:
    {
        "valid": true/false,
        "errors": ["Must have exactly one player", ...],
        "warnings": ["Puzzle may be unsolvable"]
    }
    """
    data = request.get_json()
    grid = data.get('grid')
    
    errors = []
    warnings = []
    
    # Count elements
    player_count = sum(row.count('@') + row.count('+') for row in grid)
    box_count = sum(row.count('$') + row.count('*') for row in grid)
    goal_count = sum(row.count('.') + row.count('*') + row.count('+') for row in grid)
    
    # Validation rules
    if player_count == 0:
        errors.append("Must have exactly one player (@)")
    elif player_count > 1:
        errors.append("Can only have one player")
    
    if box_count == 0:
        errors.append("Must have at least one box ($)")
    
    if goal_count == 0:
        errors.append("Must have at least one goal (.)")
    
    if box_count != goal_count:
        warnings.append(f"Box count ({box_count}) doesn't match goal count ({goal_count})")
    
    # Check if player is enclosed
    # (simplified - could be more sophisticated)
    
    return jsonify({
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    })

@app.route('/api/save_custom', methods=['POST'])
def save_custom_puzzle():
    """
    Save a custom puzzle (optional - could store in database or file).
    
    For simplicity, return a shareable link or ID.
    """
    pass
```

#### Frontend Builder

```javascript
// static/js/builder.js

class PuzzleBuilder {
    constructor(canvasId, width, height) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.width = width;
        this.height = height;
        this.tileSize = 40;
        
        // Initialize empty grid
        this.grid = Array(height).fill(null)
            .map(() => Array(width).fill(' '));
        
        // Current tool
        this.currentTool = '#';  // wall
        
        // Setup canvas
        this.canvas.width = width * this.tileSize;
        this.canvas.height = height * this.tileSize;
        
        // Add click listener
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        
        this.render();
    }
    
    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = Math.floor((event.clientX - rect.left) / this.tileSize);
        const y = Math.floor((event.clientY - rect.top) / this.tileSize);
        
        if (x >= 0 && x < this.width && y >= 0 && y < this.height) {
            // Special handling for player - only one allowed
            if (this.currentTool === '@') {
                // Remove existing player
                for (let row = 0; row < this.height; row++) {
                    for (let col = 0; col < this.width; col++) {
                        if (this.grid[row][col] === '@' || this.grid[row][col] === '+') {
                            this.grid[row][col] = ' ';
                        }
                    }
                }
            }
            
            this.grid[y][x] = this.currentTool;
            this.render();
        }
    }
    
    setTool(tool) {
        this.currentTool = tool;
    }
    
    clear() {
        this.grid = Array(this.height).fill(null)
            .map(() => Array(this.width).fill(' '));
        this.render();
    }
    
    resize(newWidth, newHeight) {
        // Create new grid, copy old data
        const newGrid = Array(newHeight).fill(null)
            .map(() => Array(newWidth).fill(' '));
        
        for (let y = 0; y < Math.min(this.height, newHeight); y++) {
            for (let x = 0; x < Math.min(this.width, newWidth); x++) {
                newGrid[y][x] = this.grid[y][x];
            }
        }
        
        this.grid = newGrid;
        this.width = newWidth;
        this.height = newHeight;
        
        this.canvas.width = newWidth * this.tileSize;
        this.canvas.height = newHeight * this.tileSize;
        
        this.render();
    }
    
    render() {
        // Similar to PuzzleRenderer, but editable
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let y = 0; y < this.height; y++) {
            for (let x = 0; x < this.width; x++) {
                this.drawTile(x, y, this.grid[y][x]);
            }
        }
        
        // Draw grid lines
        this.ctx.strokeStyle = '#ccc';
        for (let x = 0; x <= this.width; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.tileSize, 0);
            this.ctx.lineTo(x * this.tileSize, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = 0; y <= this.height; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.tileSize);
            this.ctx.lineTo(this.canvas.width, y * this.tileSize);
            this.ctx.stroke();
        }
    }
    
    drawTile(x, y, char) {
        // Same rendering as PuzzleRenderer
        // Implementation details...
    }
    
    getGridString() {
        // Convert grid to standard Sokoban format string
        return this.grid.map(row => row.join('')).join('\n');
    }
    
    async validate() {
        const response = await fetch('/api/validate', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({grid: this.grid})
        });
        
        return await response.json();
    }
    
    async solve() {
        // First validate
        const validation = await this.validate();
        
        if (!validation.valid) {
            alert('Puzzle is invalid:\n' + validation.errors.join('\n'));
            return;
        }
        
        // Then solve
        const puzzleString = this.getGridString();
        const response = await fetch('/api/solve', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({puzzle: puzzleString})
        });
        
        return await response.json();
    }
}
```

#### Integration with Main Interface

Add a "Builder" tab/mode that switches between:
1. **Solver Mode**: Load presets, solve, visualize
2. **Builder Mode**: Create custom puzzles, validate, solve

The builder generates standard format puzzles that feed into the same solver API - complete encapsulation maintained.

---

## Module Architecture

```
sokoban_solver/
│
├── core/
│   ├── __init__.py
│   ├── parser.py           # Puzzle parsing from text
│   ├── state.py            # State representation classes
│   ├── moves.py            # Move generation and validation
│   └── validator.py        # Solution validation
│
├── solver/
│   ├── __init__.py
│   ├── astar.py            # A* search implementation (main API)
│   ├── heuristic.py        # Heuristic functions
│   └── deadlock.py         # Deadlock detection
│
├── visualization/
│   ├── __init__.py
│   └── terminal.py         # ASCII visualization
│
├── web/
│   ├── app.py              # Flask backend server
│   ├── templates/
│   │   ├── index.html      # Main solver page
│   │   └── builder.html    # Puzzle builder page
│   └── static/
│       ├── css/
│       │   └── style.css   # Main styling
│       ├── js/
│       │   ├── app.js      # Main application logic
│       │   ├── renderer.js # Canvas-based puzzle rendering
│       │   ├── solver.js   # API communication
│       │   └── builder.js  # Puzzle builder interface
│       └── puzzles/
│           └── presets.json # Pre-designed puzzles
│
├── puzzles/                # Sample puzzle text files
│   ├── easy/
│   ├── medium/
│   └── hard/
│
├── tests/
│   ├── test_parser.py
│   ├── test_solver.py
│   ├── test_deadlock.py
│   ├── test_heuristic.py
│   └── test_api.py         # Flask API endpoint tests
│
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
└── README.md              # Project documentation
```

### Dependencies

```
# requirements.txt
# Core solver - no dependencies

# Web interface
flask>=2.3.0
flask-cors>=4.0.0

# Optional for development
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-flask>=1.2.0
```

---

## Performance Targets

### Solve Time by Difficulty

| Difficulty | Grid Size | Boxes | Target Time | Success Rate |
|------------|-----------|-------|-------------|--------------|
| Trivial    | 5×5       | 1-2   | <0.01s      | 100%         |
| Easy       | 8×8       | 3-4   | <0.5s       | 100%         |
| Medium     | 12×12     | 5-6   | <5s         | 95%          |
| Hard       | 15×15     | 7-8   | <30s        | 80%          |
| Expert     | 18×18     | 9-10  | <60s        | 50%          |

### Memory Constraints

- Maximum states in memory: 50 million
- Maximum closed set size: 10 million states
- Expected memory per state: ~100 bytes
- Peak memory usage: <5 GB

### Timeouts

- Default timeout: 60 seconds
- Configurable via command-line flag
- Graceful termination with partial statistics

---

## Testing Requirements

### Unit Tests

1. **Parser Tests**
   - Valid puzzle formats
   - Invalid input handling
   - Edge cases (empty puzzles, malformed)

2. **State Tests**
   - State hashing consistency
   - Equality comparisons
   - Serialization/deserialization

3. **Move Generation Tests**
   - Valid push detection
   - Player reachability
   - Boundary conditions

4. **Deadlock Tests**
   - Each deadlock type individually
   - Combined deadlock scenarios
   - False positive checks

5. **Heuristic Tests**
   - Admissibility verification
   - Consistency check
   - Precomputation correctness

### Integration Tests

1. **Solver Tests**
   - Known solvable puzzles
   - Known unsolvable puzzles
   - Solution optimality verification

2. **Performance Tests**
   - Benchmark puzzle suite
   - Memory usage profiling
   - Timeout handling

### Test Puzzle Suite

```
tests/puzzles/
├── trivial_01.txt          # 1 box, 1 goal, 3 moves
├── easy_01.txt             # 3 boxes, clear solution
├── easy_unsolvable.txt     # Obvious deadlock
├── medium_01.txt           # 5 boxes, branching paths
├── hard_01.txt             # 8 boxes, tight corridors
└── corner_trap.txt         # Tests corner deadlock detection
```

---

## Command-Line Interface

```bash
# Basic usage
python main.py puzzle.txt

# With options
python main.py puzzle.txt --timeout 120 --max-states 20000000

# Enable visualization
python main.py puzzle.txt --visualize

# Benchmark mode
python main.py --benchmark puzzles/easy/

# Verbose output
python main.py puzzle.txt --verbose

# Output solution to file
python main.py puzzle.txt --output solution.txt
```

### CLI Arguments

```
positional arguments:
  puzzle_file           Path to puzzle file

optional arguments:
  -h, --help            Show help message
  -t, --timeout         Timeout in seconds (default: 60)
  -m, --max-states      Maximum states to explore (default: 10000000)
  -v, --verbose         Enable verbose output
  -o, --output          Write solution to file
  --visualize           Show GUI visualization
  --no-deadlock         Disable deadlock detection (testing)
  --benchmark           Run benchmark on directory of puzzles
```

---

## Implementation Phases

### Phase 1: Core Solver (Days 1-3)
**Goal**: Working A* solver with terminal output

**Deliverables**:
- [ ] Puzzle parser (standard text format)
- [ ] State representation and hashing
- [ ] A* search implementation
- [ ] Heuristic with precomputed distances
- [ ] Deadlock detection (all 5 types)
- [ ] Terminal visualization
- [ ] CLI interface
- [ ] Unit tests for all components

**Success Criteria**: Solver can find optimal solutions for easy/medium puzzles in <10 seconds

### Phase 2: Web Interface (Days 4-5)
**Prerequisites**: Phase 1 completely working
**Goal**: Flask backend + frontend for puzzle solving

**Deliverables**:
- [ ] Flask API server with endpoints
- [ ] Solver API wrapper (clean interface)
- [ ] HTML/CSS/JS frontend
- [ ] Canvas-based rendering
- [ ] Preset puzzle selection
- [ ] Solution playback with controls
- [ ] Statistics display

**Success Criteria**: User can select a puzzle, solve it, and watch the solution in browser

### Phase 3: Puzzle Builder (Days 6-7)
**Prerequisites**: Phase 2 working
**Goal**: Interactive puzzle creation

**Deliverables**:
- [ ] Grid editor with tools
- [ ] Puzzle validation endpoint
- [ ] Builder UI with controls
- [ ] Grid-to-solver conversion
- [ ] Ability to solve custom puzzles

**Success Criteria**: User can create a valid puzzle, validate it, and solve it

---

## Future Enhancements

### Priority 1 (Polish)
- [ ] Better error messages and user feedback
- [ ] Puzzle difficulty ratings
- [ ] Export/import custom puzzles
- [ ] Save/load user creations
- [ ] Solution animation speed control
- [ ] Mobile-responsive design

### Priority 2 (Performance)
- [ ] IDA* solver variant for hard puzzles
- [ ] Parallel state exploration
- [ ] Benchmark suite with standard puzzles
- [ ] Performance profiling and optimization

### Priority 3 (Advanced Features)
- [ ] Pattern database generation
- [ ] Machine learning heuristic
- [ ] Multiplayer puzzle challenges
- [ ] Puzzle rating and sharing
- [ ] Solution optimality verification
- [ ] Alternative solution finder

### Priority 4 (Community)
- [ ] User accounts and puzzle library
- [ ] Leaderboards for solve times
- [ ] Puzzle difficulty voting
- [ ] Community puzzle collections
- [ ] Tutorial mode for beginners

---

## References

### Academic Papers
- "Fast Optimal Sokoban Solving" (Junghanns & Schaeffer)
- "Deadlock Detection in Sokoban" (Taylor & Parberry)

### Online Resources
- Sokoban YASS solver documentation
- XSokoban file format specification
- Festival Sokoban puzzle collections

### Benchmarks
- Original Sokoban levels (50 puzzles)
- Microban collection (155 puzzles)
- Sasquatch collection (advanced puzzles)

---

**Document Status**: Complete  
**Last Updated**: 2026-02-06  
**Version**: 1.0