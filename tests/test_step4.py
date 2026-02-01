"""Step 4 tests — BFS solver."""
import lightsout


def test_bfs_1x1():
    """1x1 grid: pressing the single button solves it."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(1)
    assert solution is not None
    assert len(solution) == 1
    assert solution[0] == (0, 0)


def test_bfs_2x2():
    """2x2 grid should be solvable."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(2)
    assert solution is not None
    assert isinstance(solution, tuple)
    assert len(solution) > 0


def test_bfs_2x2_solution_is_valid():
    """Applying the BFS solution to a 2x2 grid should produce the goal state."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(2)
    state = lightsout.make_initial_state(2)
    for row, col in solution:
        state = lightsout.press_button(state, row, col, 2)
    assert lightsout.is_goal(state)


def test_bfs_3x3_solution_is_valid():
    """Applying the BFS solution to a 3x3 grid should produce the goal state."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(3)
    assert solution is not None
    state = lightsout.make_initial_state(3)
    for row, col in solution:
        state = lightsout.press_button(state, row, col, 3)
    assert lightsout.is_goal(state)


def test_bfs_returns_expanded_and_created():
    """BFS should return positive counts for both expanded and created."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(2)
    assert isinstance(expanded, int)
    assert isinstance(created, int)
    assert expanded > 0
    assert created > 0


def test_bfs_created_gte_expanded():
    """Nodes created should be >= nodes expanded."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(2)
    assert created >= expanded


def test_bfs_solution_has_no_duplicates():
    """Each button should be pressed at most once in the solution."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(2)
    assert len(solution) == len(set(solution))


def test_bfs_1x1_expanded():
    """1x1 should require very few expanded nodes."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(1)
    assert expanded <= 5


def test_bfs_solution_is_tuple():
    """Solution should be a tuple of (row, col) tuples."""
    solution, expanded, created = lightsout.solve_lights_out_bfs(2)
    assert isinstance(solution, tuple)
    for button in solution:
        assert isinstance(button, tuple)
        assert len(button) == 2
