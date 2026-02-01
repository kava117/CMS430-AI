# Lights Out Puzzle Solver - Technical Specifications

## Problem Description

Implement a solver for the classic "Lights Out" puzzle using two different search algorithms: Breadth-First Search (BFS) and Iterative Deepening Depth-First Search (IDDFS).

### Puzzle Rules
- **Grid**: N × N grid of button lights (variable N)
- **Initial State**: All lights are ON
- **Goal State**: All lights are OFF
- **Action**: Pressing a button toggles:
  - The button itself
  - Its four neighbors (up, down, left, right)
  - Edge and corner buttons have fewer neighbors

### Key Optimization
Since pressing a button twice returns it to the original state, **each button needs to be pressed at most once** in an optimal solution. This constraint is critical for preventing infinite search paths.

## Implementation Requirements

### Language
Python 3.x

### Core Components

#### 1. State Representation
- Represent the grid state as an immutable data structure (tuple of tuples recommended)
- Each cell value: `True` (ON) or `False` (OFF)
- Example for 3×3 grid:
  ```python
  state = (
      (True, True, True),
      (True, True, True),
      (True, True, True)
  )
  ```

#### 2. State Manipulation Functions

**`press_button(state: tuple, row: int, col: int, n: int) -> tuple`**
- Takes current state and button coordinates
- Returns new state after toggling the button and its neighbors
- Must handle edge cases (corners, edges)

**`is_goal(state: tuple) -> bool`**
- Returns `True` if all lights are OFF
- Returns `False` otherwise

**`get_successors(state: tuple, n: int, pressed: set) -> list`**
- Generates all valid successor states
- Takes a set of already-pressed buttons to avoid redundant presses
- Returns list of tuples: `[(new_state, button_pressed, updated_pressed_set), ...]`
- Each successor represents pressing one unpressed button

#### 3. Algorithm Implementation

**`solve_lights_out_bfs(n: int) -> tuple`**
- Implements Breadth-First Search
- **Returns**: 
  - Tuple of button coordinates in press order: `((r1, c1), (r2, c2), ...)`
  - `None` if no solution exists
  - Number of nodes processed
- **Tracking**: Maintain visited states to avoid cycles
- **Queue elements**: `(state, pressed_buttons_set, solution_path, nodes_processed)`

**`solve_lights_out_iddfs(n: int, max_depth: int = 20) -> tuple`**
- Implements Iterative Deepening Depth-First Search
- Progressively increases depth limit from 0 to `max_depth`
- **Returns**: 
  - Tuple of button coordinates in press order
  - `None` if no solution found within `max_depth`
  - Total number of nodes processed across all iterations
- **Helper function needed**: `dfs_limited(state, pressed, path, depth_limit, current_depth, nodes_processed)`

#### 4. Performance Tracking

**`compare_algorithms(grid_sizes: list) -> dict`**
- Tests both algorithms on multiple grid sizes
- **Input**: List of N values (e.g., `[2, 3, 4, 5]`)
- **Returns**: Dictionary with results
  ```python
  {
      'grid_sizes': [2, 3, 4, 5],
      'bfs_nodes': [nodes_for_2x2, nodes_for_3x3, ...],
      'iddfs_nodes': [nodes_for_2x2, nodes_for_3x3, ...]
  }
  ```

#### 5. Visualization Functions

**`print_grid(state: tuple) -> None`**
- Prints the current grid state
- Use `■` for ON, `□` for OFF (or similar clear representation)

**`print_solution(solution: tuple, n: int) -> None`**
- Prints which buttons were pressed in order
- Shows the sequence of grid states as each button is pressed

**`plot_performance(results: dict) -> None`**
- Creates line plot comparing BFS vs IDDFS
- **X-axis**: Grid size (N)
- **Y-axis**: Number of nodes processed
- **Two lines**: One for BFS, one for IDDFS
- Save plot as `performance_comparison.png`
- Use matplotlib for plotting

## Code Structure (Following N-Queens Example)

```python
"""
Lights Out puzzle solver using BFS and Iterative Deepening
[Your Name], 2026
"""

# Helper functions
def press_button(state: tuple, row: int, col: int, n: int) -> tuple:
    """Toggle button at (row, col) and its neighbors"""
    pass

def is_goal(state: tuple) -> bool:
    """Check if all lights are OFF"""
    pass

def get_successors(state: tuple, n: int, pressed: set) -> list:
    """Generate valid successor states (unpressed buttons only)"""
    pass

# Algorithm implementations
def solve_lights_out_bfs(n: int) -> tuple:
    """Solve using Breadth-First Search"""
    pass

def solve_lights_out_iddfs(n: int, max_depth: int = 20) -> tuple:
    """Solve using Iterative Deepening DFS"""
    pass

# Helper for IDDFS
def dfs_limited(state: tuple, pressed: set, path: list, 
                depth_limit: int, current_depth: int, n: int) -> tuple:
    """Depth-limited DFS helper"""
    pass

# Performance analysis
def compare_algorithms(grid_sizes: list) -> dict:
    """Compare BFS vs IDDFS performance"""
    pass

# Visualization
def print_grid(state: tuple) -> None:
    """Display grid state"""
    pass

def print_solution(solution: tuple, n: int) -> None:
    """Display solution sequence"""
    pass

def plot_performance(results: dict) -> None:
    """Create performance comparison graph"""
    pass

# Main execution
if __name__ == "__main__":
    # Test both algorithms on various grid sizes
    grid_sizes = [2, 3, 4, 5]
    results = compare_algorithms(grid_sizes)
    
    # Generate performance graph
    plot_performance(results)
    
    # Example: Show solution for 3x3 grid
    solution, nodes = solve_lights_out_bfs(3)
    print_solution(solution, 3)
```

## Expected Output

### Console Output
```
Testing 2×2 grid...
BFS: Solution found with 4 button presses, 15 nodes processed
IDDFS: Solution found with 4 button presses, 23 nodes processed

Testing 3×3 grid...
BFS: Solution found with 6 button presses, 124 nodes processed
IDDFS: Solution found with 6 button presses, 89 nodes processed

...

Solution for 3×3 grid:
Initial state:
■ ■ ■
■ ■ ■
■ ■ ■

Press button at (0, 0):
□ □ ■
□ ■ ■
■ ■ ■

Press button at (0, 2):
...
```

### Graph Output
- File: `performance_comparison.png`
- Line plot with grid size on X-axis, nodes processed on Y-axis
- Two lines clearly labeled "BFS" and "IDDFS"
- Legend, axis labels, title included

## Why Iterative Deepening is Suitable

Document should include a brief explanation (can be in comments or separate section):
- Unlimited depth would cause infinite descent without iterative deepening
- Button presses can be repeated indefinitely without the depth limit
- IDDFS ensures all combinations up to depth D are explored before going deeper
- Combines space efficiency of DFS with completeness of BFS
- Particularly effective when solution depth is unknown

## Dependencies
- Python standard library (`collections.deque` for BFS queue)
- `matplotlib` for plotting
- No other external dependencies required

## Performance Notes
- For N > 5, computation may become intensive
- BFS will typically process more nodes but guarantees shortest solution
- IDDFS may be more memory-efficient for larger grids
- Both algorithms should find solutions for small grids (N ≤ 5) quickly

## Deliverables
1. Python implementation file (`lights_out_solver.py`)
2. Performance comparison graph (`performance_comparison.png`)
3. Console output showing solutions and node counts for tested grid sizes