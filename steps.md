# Lights Out Puzzle Solver - Implementation Steps

Each step below builds on the previous ones. Complete them in order. Every step that adds Python code includes a **Tests** section with `pytest` test cases. Run the tests after implementing the step — all tests must pass before moving to the next step.

---

## Step 1: Project Scaffolding

Create the project file and install dependencies.

**Tasks:**
1. Create the following file structure:
   ```
   project/
   ├── lightsout.py
   ├── tests/
   │   └── __init__.py
   └── requirements.txt
   ```
2. Write `requirements.txt` with:
   ```
   matplotlib
   pytest
   ```
3. Install dependencies with `pip install -r requirements.txt`.
4. In `lightsout.py`, add the module docstring and placeholder functions with `pass` bodies for all functions listed in the spec:
   - `press_button(state, row, col, n)`
   - `is_goal(state)`
   - `get_successors(state, n, pressed)`
   - `solve_lights_out_bfs(n)`
   - `solve_lights_out_iddfs(n, max_depth=20)`
   - `dfs_limited(state, pressed, path, depth_limit, current_depth, n)`
   - `compare_algorithms(grid_sizes)`
   - `print_grid(state)`
   - `print_solution(solution, n)`
   - `plot_performance(results)`

**Tests:**

Create `tests/test_step1.py`:

```python
"""Step 1 tests — verify project scaffolding and module structure."""
import importlib
import inspect
import os


def test_lightsout_module_imports():
    """lightsout.py should be importable without errors."""
    import lightsout  # noqa: F401


def test_has_press_button():
    """lightsout.py must define press_button."""
    import lightsout
    assert hasattr(lightsout, "press_button")
    assert callable(lightsout.press_button)


def test_has_is_goal():
    """lightsout.py must define is_goal."""
    import lightsout
    assert hasattr(lightsout, "is_goal")
    assert callable(lightsout.is_goal)


def test_has_get_successors():
    """lightsout.py must define get_successors."""
    import lightsout
    assert hasattr(lightsout, "get_successors")
    assert callable(lightsout.get_successors)


def test_has_solve_bfs():
    """lightsout.py must define solve_lights_out_bfs."""
    import lightsout
    assert hasattr(lightsout, "solve_lights_out_bfs")
    assert callable(lightsout.solve_lights_out_bfs)


def test_has_solve_iddfs():
    """lightsout.py must define solve_lights_out_iddfs."""
    import lightsout
    assert hasattr(lightsout, "solve_lights_out_iddfs")
    assert callable(lightsout.solve_lights_out_iddfs)


def test_has_dfs_limited():
    """lightsout.py must define dfs_limited."""
    import lightsout
    assert hasattr(lightsout, "dfs_limited")
    assert callable(lightsout.dfs_limited)


def test_has_compare_algorithms():
    """lightsout.py must define compare_algorithms."""
    import lightsout
    assert hasattr(lightsout, "compare_algorithms")
    assert callable(lightsout.compare_algorithms)


def test_has_print_grid():
    """lightsout.py must define print_grid."""
    import lightsout
    assert hasattr(lightsout, "print_grid")
    assert callable(lightsout.print_grid)


def test_has_print_solution():
    """lightsout.py must define print_solution."""
    import lightsout
    assert hasattr(lightsout, "print_solution")
    assert callable(lightsout.print_solution)


def test_has_plot_performance():
    """lightsout.py must define plot_performance."""
    import lightsout
    assert hasattr(lightsout, "plot_performance")
    assert callable(lightsout.plot_performance)


def test_requirements_file_exists():
    """requirements.txt must exist."""
    assert os.path.isfile("requirements.txt")


def test_tests_directory_exists():
    """tests/ directory must exist."""
    assert os.path.isdir("tests")
```

Run: `pytest tests/test_step1.py -v`

All 12 tests must pass.

**Acceptance criteria:**
- `lightsout.py` is importable and defines all required functions.
- `requirements.txt` and `tests/` directory exist.
- `pytest tests/test_step1.py -v` passes all 12 tests.

---

## Step 2: State Representation and `press_button`

Implement the core state manipulation function.

**Tasks:**
1. In `lightsout.py`, implement `press_button(state, row, col, n)`:
   - `state` is a tuple of tuples of booleans (`True` = ON, `False` = OFF).
   - Toggle the button at `(row, col)` and its four neighbors (up, down, left, right).
   - Handle edges and corners — only toggle neighbors that are within bounds.
   - Return a new tuple of tuples (states are immutable).

2. Add a helper to create the initial all-ON state:
   ```python
   def make_initial_state(n: int) -> tuple:
       """Return an n×n grid with all lights ON."""
       return tuple(tuple(True for _ in range(n)) for _ in range(n))
   ```

**Tests:**

Create `tests/test_step2.py`:

```python
"""Step 2 tests — press_button and state representation."""
import lightsout


def test_initial_state_2x2():
    """make_initial_state(2) should return a 2×2 grid of all True."""
    state = lightsout.make_initial_state(2)
    assert state == ((True, True), (True, True))


def test_initial_state_3x3():
    """make_initial_state(3) should return a 3×3 grid of all True."""
    state = lightsout.make_initial_state(3)
    assert len(state) == 3
    assert all(len(row) == 3 for row in state)
    assert all(cell is True for row in state for cell in row)


def test_state_is_immutable():
    """State should be a tuple of tuples."""
    state = lightsout.make_initial_state(3)
    assert isinstance(state, tuple)
    assert all(isinstance(row, tuple) for row in state)


def test_press_center_3x3():
    """Pressing center of 3×3 toggles center and 4 neighbors."""
    state = lightsout.make_initial_state(3)
    new_state = lightsout.press_button(state, 1, 1, 3)
    # Center and 4 neighbors should be False, corners stay True
    assert new_state[1][1] is False  # center
    assert new_state[0][1] is False  # up
    assert new_state[2][1] is False  # down
    assert new_state[1][0] is False  # left
    assert new_state[1][2] is False  # right
    # Corners unchanged
    assert new_state[0][0] is True
    assert new_state[0][2] is True
    assert new_state[2][0] is True
    assert new_state[2][2] is True


def test_press_corner_3x3():
    """Pressing top-left corner of 3×3 toggles 3 cells."""
    state = lightsout.make_initial_state(3)
    new_state = lightsout.press_button(state, 0, 0, 3)
    assert new_state[0][0] is False  # itself
    assert new_state[0][1] is False  # right neighbor
    assert new_state[1][0] is False  # down neighbor
    # Non-neighbors unchanged
    assert new_state[1][1] is True
    assert new_state[2][2] is True


def test_press_edge_3x3():
    """Pressing top-center of 3×3 toggles 4 cells (no up neighbor)."""
    state = lightsout.make_initial_state(3)
    new_state = lightsout.press_button(state, 0, 1, 3)
    assert new_state[0][1] is False  # itself
    assert new_state[0][0] is False  # left
    assert new_state[0][2] is False  # right
    assert new_state[1][1] is False  # down
    # No up neighbor — rest unchanged
    assert new_state[1][0] is True
    assert new_state[2][1] is True


def test_press_bottom_right_corner_2x2():
    """Pressing (1,1) on 2×2 toggles 3 cells."""
    state = lightsout.make_initial_state(2)
    new_state = lightsout.press_button(state, 1, 1, 2)
    assert new_state[1][1] is False  # itself
    assert new_state[0][1] is False  # up
    assert new_state[1][0] is False  # left
    # Top-left unchanged
    assert new_state[0][0] is True


def test_double_press_restores_state():
    """Pressing the same button twice should restore the original state."""
    state = lightsout.make_initial_state(3)
    once = lightsout.press_button(state, 1, 1, 3)
    twice = lightsout.press_button(once, 1, 1, 3)
    assert twice == state


def test_press_does_not_mutate_original():
    """press_button should return a new state, not mutate the original."""
    state = lightsout.make_initial_state(3)
    original = state
    lightsout.press_button(state, 1, 1, 3)
    assert state == original


def test_press_1x1():
    """Pressing the only button on a 1×1 grid toggles just that cell."""
    state = ((True,),)
    new_state = lightsout.press_button(state, 0, 0, 1)
    assert new_state == ((False,),)
```

Run: `pytest tests/test_step2.py -v`

All 10 tests must pass.

**Acceptance criteria:**
- `make_initial_state` returns the correct all-ON grid for any N.
- `press_button` correctly toggles the target and its valid neighbors.
- Edge and corner cases are handled.
- Pressing a button twice restores the original state.
- `pytest tests/test_step2.py -v` passes all 10 tests.

---

## Step 3: Goal Checking and Successor Generation

Implement `is_goal` and `get_successors`.

**Tasks:**
1. In `lightsout.py`, implement `is_goal(state)`:
   - Return `True` if every cell in the grid is `False` (all lights OFF).
   - Return `False` otherwise.

2. In `lightsout.py`, implement `get_successors(state, n, pressed)`:
   - Iterate over all `(row, col)` positions in the grid.
   - Skip positions that are already in the `pressed` set.
   - For each unpressed position, compute the new state via `press_button`.
   - Return a list of tuples: `[(new_state, (row, col), updated_pressed_set), ...]`.
   - The `updated_pressed_set` is a new `frozenset` with the pressed button added.

**Tests:**

Create `tests/test_step3.py`:

```python
"""Step 3 tests — is_goal and get_successors."""
import lightsout


def test_is_goal_all_off():
    """All-OFF grid should be the goal state."""
    state = ((False, False), (False, False))
    assert lightsout.is_goal(state) is True


def test_is_goal_all_on():
    """All-ON grid is not the goal state."""
    state = lightsout.make_initial_state(3)
    assert lightsout.is_goal(state) is False


def test_is_goal_one_on():
    """A grid with even one ON cell is not the goal."""
    state = ((False, False), (True, False))
    assert lightsout.is_goal(state) is False


def test_is_goal_1x1_off():
    """1×1 all-OFF is goal."""
    assert lightsout.is_goal(((False,),)) is True


def test_is_goal_1x1_on():
    """1×1 all-ON is not goal."""
    assert lightsout.is_goal(((True,),)) is False


def test_successors_count_no_pressed():
    """With no buttons pressed, successors should equal n*n."""
    state = lightsout.make_initial_state(2)
    successors = lightsout.get_successors(state, 2, frozenset())
    assert len(successors) == 4  # 2×2 = 4 buttons


def test_successors_count_some_pressed():
    """With some buttons pressed, successors should be fewer."""
    state = lightsout.make_initial_state(2)
    pressed = frozenset({(0, 0), (1, 1)})
    successors = lightsout.get_successors(state, 2, pressed)
    assert len(successors) == 2  # 4 - 2 pressed = 2 remaining


def test_successors_count_3x3():
    """3×3 grid with no pressed buttons should yield 9 successors."""
    state = lightsout.make_initial_state(3)
    successors = lightsout.get_successors(state, 3, frozenset())
    assert len(successors) == 9


def test_successor_tuple_structure():
    """Each successor should be (new_state, button, updated_pressed)."""
    state = lightsout.make_initial_state(2)
    successors = lightsout.get_successors(state, 2, frozenset())
    for new_state, button, new_pressed in successors:
        assert isinstance(new_state, tuple)
        assert isinstance(button, tuple)
        assert len(button) == 2
        assert button in new_pressed


def test_successor_state_differs():
    """Each successor's state should differ from the original."""
    state = lightsout.make_initial_state(2)
    successors = lightsout.get_successors(state, 2, frozenset())
    for new_state, button, new_pressed in successors:
        assert new_state != state


def test_successors_skip_pressed():
    """Buttons in the pressed set should not appear in successors."""
    state = lightsout.make_initial_state(2)
    pressed = frozenset({(0, 0)})
    successors = lightsout.get_successors(state, 2, pressed)
    buttons = [button for _, button, _ in successors]
    assert (0, 0) not in buttons


def test_successor_pressed_set_is_superset():
    """Updated pressed set should contain the original pressed set plus the new button."""
    state = lightsout.make_initial_state(2)
    original_pressed = frozenset({(0, 0)})
    successors = lightsout.get_successors(state, 2, original_pressed)
    for _, button, new_pressed in successors:
        assert original_pressed.issubset(new_pressed)
        assert button in new_pressed
```

Run: `pytest tests/test_step3.py -v`

All 12 tests must pass.

**Acceptance criteria:**
- `is_goal` correctly identifies all-OFF grids.
- `get_successors` generates the correct number of successors.
- Pressed buttons are excluded from successors.
- Each successor contains the new state, the button pressed, and an updated pressed set.
- `pytest tests/test_step3.py -v` passes all 12 tests.

---

## Step 4: Breadth-First Search Solver

Implement the BFS algorithm to solve the puzzle.

**Tasks:**
1. In `lightsout.py`, implement `solve_lights_out_bfs(n)`:
   - Start from the initial all-ON state for an `n×n` grid.
   - Use `collections.deque` as the BFS queue.
   - Queue elements: `(state, pressed_set, solution_path)`.
   - Track visited states with a `set` to avoid revisiting.
   - Track number of nodes processed (incremented each time a state is dequeued).
   - On finding a goal state, return `(solution_path, nodes_processed)`.
   - If the queue is exhausted, return `(None, nodes_processed)`.
   - The `solution_path` is a tuple of `(row, col)` button presses in order.

**Tests:**

Create `tests/test_step4.py`:

```python
"""Step 4 tests — BFS solver."""
import lightsout


def test_bfs_1x1():
    """1×1 grid: pressing the single button solves it."""
    solution, nodes = lightsout.solve_lights_out_bfs(1)
    assert solution is not None
    assert len(solution) == 1
    assert solution[0] == (0, 0)


def test_bfs_2x2():
    """2×2 grid should be solvable."""
    solution, nodes = lightsout.solve_lights_out_bfs(2)
    assert solution is not None
    assert isinstance(solution, tuple)
    assert len(solution) > 0


def test_bfs_2x2_solution_is_valid():
    """Applying the BFS solution to a 2×2 grid should produce the goal state."""
    solution, nodes = lightsout.solve_lights_out_bfs(2)
    state = lightsout.make_initial_state(2)
    for row, col in solution:
        state = lightsout.press_button(state, row, col, 2)
    assert lightsout.is_goal(state)


def test_bfs_3x3_solution_is_valid():
    """Applying the BFS solution to a 3×3 grid should produce the goal state."""
    solution, nodes = lightsout.solve_lights_out_bfs(3)
    assert solution is not None
    state = lightsout.make_initial_state(3)
    for row, col in solution:
        state = lightsout.press_button(state, row, col, 3)
    assert lightsout.is_goal(state)


def test_bfs_returns_nodes_processed():
    """BFS should return a positive node count."""
    solution, nodes = lightsout.solve_lights_out_bfs(2)
    assert isinstance(nodes, int)
    assert nodes > 0


def test_bfs_solution_has_no_duplicates():
    """Each button should be pressed at most once in the solution."""
    solution, nodes = lightsout.solve_lights_out_bfs(2)
    assert len(solution) == len(set(solution))


def test_bfs_1x1_nodes():
    """1×1 should require very few nodes."""
    solution, nodes = lightsout.solve_lights_out_bfs(1)
    assert nodes <= 5


def test_bfs_solution_is_tuple():
    """Solution should be a tuple of (row, col) tuples."""
    solution, nodes = lightsout.solve_lights_out_bfs(2)
    assert isinstance(solution, tuple)
    for button in solution:
        assert isinstance(button, tuple)
        assert len(button) == 2
```

Run: `pytest tests/test_step4.py -v`

All 8 tests must pass.

**Acceptance criteria:**
- BFS finds valid solutions for 1×1, 2×2, and 3×3 grids.
- Applying the returned solution to the initial state produces the goal state.
- No button is pressed more than once.
- Node count is returned as a positive integer.
- `pytest tests/test_step4.py -v` passes all 8 tests.

---

## Step 5: Iterative Deepening DFS Solver

Implement the IDDFS algorithm.

**Tasks:**
1. In `lightsout.py`, implement `dfs_limited(state, pressed, path, depth_limit, current_depth, n)`:
   - If `is_goal(state)`, return `(tuple(path), 1)` (the solution path and 1 node processed).
   - If `current_depth >= depth_limit`, return `(None, 1)`.
   - For each successor, recursively call `dfs_limited` with incremented depth.
   - Accumulate total nodes processed across recursive calls.
   - Return the first solution found, or `(None, total_nodes)` if none found at this depth.

2. In `lightsout.py`, implement `solve_lights_out_iddfs(n, max_depth=20)`:
   - Start from the initial all-ON state.
   - For each depth limit from 0 to `max_depth`:
     - Call `dfs_limited` with the initial state.
     - If a solution is found, return `(solution, total_nodes)`.
   - Accumulate total nodes processed across all depth iterations.
   - If no solution found within `max_depth`, return `(None, total_nodes)`.

**Tests:**

Create `tests/test_step5.py`:

```python
"""Step 5 tests — IDDFS solver."""
import lightsout


def test_iddfs_1x1():
    """1×1 grid: pressing the single button solves it."""
    solution, nodes = lightsout.solve_lights_out_iddfs(1)
    assert solution is not None
    assert len(solution) == 1
    assert solution[0] == (0, 0)


def test_iddfs_2x2():
    """2×2 grid should be solvable."""
    solution, nodes = lightsout.solve_lights_out_iddfs(2)
    assert solution is not None
    assert isinstance(solution, tuple)
    assert len(solution) > 0


def test_iddfs_2x2_solution_is_valid():
    """Applying the IDDFS solution to a 2×2 grid should produce the goal state."""
    solution, nodes = lightsout.solve_lights_out_iddfs(2)
    state = lightsout.make_initial_state(2)
    for row, col in solution:
        state = lightsout.press_button(state, row, col, 2)
    assert lightsout.is_goal(state)


def test_iddfs_3x3_solution_is_valid():
    """Applying the IDDFS solution to a 3×3 grid should produce the goal state."""
    solution, nodes = lightsout.solve_lights_out_iddfs(3)
    assert solution is not None
    state = lightsout.make_initial_state(3)
    for row, col in solution:
        state = lightsout.press_button(state, row, col, 3)
    assert lightsout.is_goal(state)


def test_iddfs_returns_nodes_processed():
    """IDDFS should return a positive node count."""
    solution, nodes = lightsout.solve_lights_out_iddfs(2)
    assert isinstance(nodes, int)
    assert nodes > 0


def test_iddfs_solution_has_no_duplicates():
    """Each button should be pressed at most once in the solution."""
    solution, nodes = lightsout.solve_lights_out_iddfs(2)
    assert len(solution) == len(set(solution))


def test_iddfs_max_depth_zero_no_solution():
    """max_depth=0 should only find solutions if the initial state is already the goal."""
    solution, nodes = lightsout.solve_lights_out_iddfs(2, max_depth=0)
    # 2×2 all-ON is not the goal, so no solution at depth 0
    assert solution is None


def test_iddfs_solution_is_tuple():
    """Solution should be a tuple of (row, col) tuples."""
    solution, nodes = lightsout.solve_lights_out_iddfs(2)
    assert isinstance(solution, tuple)
    for button in solution:
        assert isinstance(button, tuple)
        assert len(button) == 2


def test_bfs_and_iddfs_same_length():
    """BFS and IDDFS should find solutions of the same length (both optimal)."""
    bfs_sol, _ = lightsout.solve_lights_out_bfs(2)
    iddfs_sol, _ = lightsout.solve_lights_out_iddfs(2)
    assert len(bfs_sol) == len(iddfs_sol)


def test_dfs_limited_at_goal():
    """dfs_limited should immediately return when given the goal state."""
    goal = ((False, False), (False, False))
    solution, nodes = lightsout.dfs_limited(goal, frozenset(), [], 5, 0, 2)
    assert solution is not None
    assert len(solution) == 0  # no presses needed
```

Run: `pytest tests/test_step5.py -v`

All 10 tests must pass.

**Acceptance criteria:**
- IDDFS finds valid solutions for 1×1, 2×2, and 3×3 grids.
- Applying the returned solution to the initial state produces the goal state.
- No button is pressed more than once.
- IDDFS with `max_depth=0` correctly returns `None` when the initial state is not the goal.
- BFS and IDDFS find solutions of the same length.
- `pytest tests/test_step5.py -v` passes all 10 tests.

---

## Step 6: Visualization Functions

Implement grid printing and solution display.

**Tasks:**
1. In `lightsout.py`, implement `print_grid(state)`:
   - Print each row of the grid.
   - Use `"■"` for ON (`True`) and `"□"` for OFF (`False`).
   - Separate cells with spaces.

2. In `lightsout.py`, implement `print_solution(solution, n)`:
   - Print the initial all-ON state.
   - For each button press in the solution, print which button was pressed and the resulting grid state.
   - Format: `"Press button at (row, col):"` followed by the grid.

**Tests:**

Create `tests/test_step6.py`:

```python
"""Step 6 tests — visualization functions."""
import lightsout


def test_print_grid_runs(capsys):
    """print_grid should produce output without errors."""
    state = lightsout.make_initial_state(3)
    lightsout.print_grid(state)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_print_grid_on_symbol(capsys):
    """print_grid should use ■ for ON cells."""
    state = lightsout.make_initial_state(2)
    lightsout.print_grid(state)
    captured = capsys.readouterr()
    assert "■" in captured.out


def test_print_grid_off_symbol(capsys):
    """print_grid should use □ for OFF cells."""
    state = ((False, False), (False, False))
    lightsout.print_grid(state)
    captured = capsys.readouterr()
    assert "□" in captured.out


def test_print_grid_row_count(capsys):
    """print_grid for 3×3 should print 3 lines of grid content."""
    state = lightsout.make_initial_state(3)
    lightsout.print_grid(state)
    captured = capsys.readouterr()
    lines = [line for line in captured.out.strip().split("\n") if line.strip()]
    assert len(lines) == 3


def test_print_grid_mixed_state(capsys):
    """print_grid with mixed state should show both symbols."""
    state = ((True, False), (False, True))
    lightsout.print_grid(state)
    captured = capsys.readouterr()
    assert "■" in captured.out
    assert "□" in captured.out


def test_print_solution_runs(capsys):
    """print_solution should produce output without errors."""
    solution, _ = lightsout.solve_lights_out_bfs(2)
    lightsout.print_solution(solution, 2)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_print_solution_shows_initial_state(capsys):
    """print_solution should show the initial state."""
    solution, _ = lightsout.solve_lights_out_bfs(2)
    lightsout.print_solution(solution, 2)
    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "initial" in output_lower or "■" in captured.out


def test_print_solution_shows_button_presses(capsys):
    """print_solution should mention each button press."""
    solution, _ = lightsout.solve_lights_out_bfs(2)
    lightsout.print_solution(solution, 2)
    captured = capsys.readouterr()
    for row, col in solution:
        assert f"({row}, {col})" in captured.out or f"{row}" in captured.out
```

Run: `pytest tests/test_step6.py -v`

All 8 tests must pass.

**Acceptance criteria:**
- `print_grid` displays the grid using `■` and `□` symbols.
- `print_solution` shows the initial state and each step of the solution.
- `pytest tests/test_step6.py -v` passes all 8 tests.

---

## Step 7: Performance Comparison and Plotting

Implement algorithm comparison and graph generation.

**Tasks:**
1. In `lightsout.py`, implement `compare_algorithms(grid_sizes)`:
   - For each grid size in the list, run both `solve_lights_out_bfs` and `solve_lights_out_iddfs`.
   - Print progress to console (e.g., `"Testing 2×2 grid..."`).
   - Print results for each algorithm (solution length and nodes processed).
   - Return a dictionary:
     ```python
     {
         "grid_sizes": [2, 3, ...],
         "bfs_nodes": [nodes_2, nodes_3, ...],
         "iddfs_nodes": [nodes_2, nodes_3, ...]
     }
     ```

2. In `lightsout.py`, implement `plot_performance(results)`:
   - Use `matplotlib` to create a line plot.
   - X-axis: grid size (N). Y-axis: nodes processed.
   - Plot two lines: one for BFS, one for IDDFS.
   - Include a legend, axis labels, and title.
   - Save the plot as `performance_comparison.png`.

3. Fill in the `if __name__ == "__main__"` block:
   - Run `compare_algorithms([2, 3, 4, 5])`.
   - Call `plot_performance` with the results.
   - Show the BFS solution for a 3×3 grid using `print_solution`.

**Tests:**

Create `tests/test_step7.py`:

```python
"""Step 7 tests — performance comparison and plotting."""
import os

import lightsout


def test_compare_returns_dict():
    """compare_algorithms should return a dictionary."""
    results = lightsout.compare_algorithms([2])
    assert isinstance(results, dict)


def test_compare_has_required_keys():
    """Result dict must have grid_sizes, bfs_nodes, and iddfs_nodes."""
    results = lightsout.compare_algorithms([2])
    assert "grid_sizes" in results
    assert "bfs_nodes" in results
    assert "iddfs_nodes" in results


def test_compare_lists_match_length():
    """All lists in the result should have the same length as the input."""
    sizes = [2, 3]
    results = lightsout.compare_algorithms(sizes)
    assert len(results["grid_sizes"]) == len(sizes)
    assert len(results["bfs_nodes"]) == len(sizes)
    assert len(results["iddfs_nodes"]) == len(sizes)


def test_compare_grid_sizes_match():
    """grid_sizes in the result should match the input."""
    sizes = [2, 3]
    results = lightsout.compare_algorithms(sizes)
    assert results["grid_sizes"] == sizes


def test_compare_nodes_are_positive():
    """Node counts should be positive integers."""
    results = lightsout.compare_algorithms([2])
    assert results["bfs_nodes"][0] > 0
    assert results["iddfs_nodes"][0] > 0


def test_plot_creates_file():
    """plot_performance should create performance_comparison.png."""
    if os.path.exists("performance_comparison.png"):
        os.remove("performance_comparison.png")

    results = lightsout.compare_algorithms([2])
    lightsout.plot_performance(results)

    assert os.path.isfile("performance_comparison.png")

    # Cleanup
    os.remove("performance_comparison.png")


def test_plot_file_is_not_empty():
    """The generated plot file should not be empty."""
    results = lightsout.compare_algorithms([2])
    lightsout.plot_performance(results)

    size = os.path.getsize("performance_comparison.png")
    assert size > 0

    os.remove("performance_comparison.png")


def test_compare_console_output(capsys):
    """compare_algorithms should print progress to console."""
    lightsout.compare_algorithms([2])
    captured = capsys.readouterr()
    assert "2" in captured.out
```

Run: `pytest tests/test_step7.py -v`

All 8 tests must pass.

**Acceptance criteria:**
- `compare_algorithms` returns correctly structured results.
- `plot_performance` generates a valid PNG file.
- Console output shows progress during comparison.
- `pytest tests/test_step7.py -v` passes all 8 tests.

---

## Step 8: Integration and Final Testing

Verify the full application works end-to-end.

**Tasks:**
1. Run the full main block: `python lightsout.py`.
2. Verify `performance_comparison.png` is generated.
3. Review console output for correctness.
4. Run the full test suite to confirm everything works together.

**Tests:**

Create `tests/test_step8.py`:

```python
"""Step 8 tests — end-to-end integration and edge cases."""
import lightsout


class TestSolutionCorrectness:
    """Verify solutions are correct by applying them to the initial state."""

    def _verify_solution(self, n):
        """Helper: solve and verify for grid size n."""
        bfs_sol, bfs_nodes = lightsout.solve_lights_out_bfs(n)
        iddfs_sol, iddfs_nodes = lightsout.solve_lights_out_iddfs(n)

        # Both should find a solution
        assert bfs_sol is not None, f"BFS failed for {n}×{n}"
        assert iddfs_sol is not None, f"IDDFS failed for {n}×{n}"

        # Verify BFS solution
        state = lightsout.make_initial_state(n)
        for row, col in bfs_sol:
            state = lightsout.press_button(state, row, col, n)
        assert lightsout.is_goal(state), f"BFS solution invalid for {n}×{n}"

        # Verify IDDFS solution
        state = lightsout.make_initial_state(n)
        for row, col in iddfs_sol:
            state = lightsout.press_button(state, row, col, n)
        assert lightsout.is_goal(state), f"IDDFS solution invalid for {n}×{n}"

    def test_1x1(self):
        self._verify_solution(1)

    def test_2x2(self):
        self._verify_solution(2)

    def test_3x3(self):
        self._verify_solution(3)

    def test_4x4(self):
        self._verify_solution(4)


class TestSolutionOptimality:
    """BFS and IDDFS should find solutions of the same length."""

    def test_2x2_same_length(self):
        bfs_sol, _ = lightsout.solve_lights_out_bfs(2)
        iddfs_sol, _ = lightsout.solve_lights_out_iddfs(2)
        assert len(bfs_sol) == len(iddfs_sol)

    def test_3x3_same_length(self):
        bfs_sol, _ = lightsout.solve_lights_out_bfs(3)
        iddfs_sol, _ = lightsout.solve_lights_out_iddfs(3)
        assert len(bfs_sol) == len(iddfs_sol)


class TestEdgeCases:
    def test_press_button_all_positions_3x3(self):
        """Pressing every button on a 3×3 grid should not crash."""
        state = lightsout.make_initial_state(3)
        for r in range(3):
            for c in range(3):
                state = lightsout.press_button(state, r, c, 3)
        # Just verify we get a valid state back
        assert len(state) == 3
        assert all(len(row) == 3 for row in state)

    def test_goal_state_as_input_to_successors(self):
        """get_successors should work on the goal state."""
        goal = ((False, False), (False, False))
        successors = lightsout.get_successors(goal, 2, frozenset())
        assert len(successors) == 4

    def test_solution_buttons_within_bounds(self):
        """All buttons in a solution should be within grid bounds."""
        for n in [2, 3]:
            solution, _ = lightsout.solve_lights_out_bfs(n)
            for row, col in solution:
                assert 0 <= row < n
                assert 0 <= col < n

    def test_no_repeated_buttons_in_solution(self):
        """Solutions should never press the same button twice."""
        for n in [2, 3]:
            bfs_sol, _ = lightsout.solve_lights_out_bfs(n)
            iddfs_sol, _ = lightsout.solve_lights_out_iddfs(n)
            assert len(bfs_sol) == len(set(bfs_sol))
            assert len(iddfs_sol) == len(set(iddfs_sol))


class TestReturnTypes:
    def test_bfs_return_type(self):
        solution, nodes = lightsout.solve_lights_out_bfs(2)
        assert isinstance(solution, tuple)
        assert isinstance(nodes, int)

    def test_iddfs_return_type(self):
        solution, nodes = lightsout.solve_lights_out_iddfs(2)
        assert isinstance(solution, tuple)
        assert isinstance(nodes, int)

    def test_compare_return_type(self):
        results = lightsout.compare_algorithms([2])
        assert isinstance(results, dict)
        assert isinstance(results["bfs_nodes"], list)
        assert isinstance(results["iddfs_nodes"], list)
```

Run: `pytest tests/test_step8.py -v`

All 14 tests must pass.

**Full suite run:** `pytest -v`

All tests across all files should pass.

**Acceptance criteria:**
- Solutions are correct for grid sizes 1 through 4 using both algorithms.
- BFS and IDDFS find solutions of the same length.
- All button presses are within bounds and never repeated.
- Return types match the spec.
- `pytest -v` passes all tests across the entire test suite.
