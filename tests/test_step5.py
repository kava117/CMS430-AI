"""Step 5 tests — IDDFS solver."""
import lightsout


def test_iddfs_1x1():
    """1x1 grid: pressing the single button solves it."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(1)
    assert solution is not None
    assert len(solution) == 1
    assert solution[0] == (0, 0)


def test_iddfs_2x2():
    """2x2 grid should be solvable."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(2)
    assert solution is not None
    assert isinstance(solution, tuple)
    assert len(solution) > 0


def test_iddfs_2x2_solution_is_valid():
    """Applying the IDDFS solution to a 2x2 grid should produce the goal state."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(2)
    state = lightsout.make_initial_state(2)
    for row, col in solution:
        state = lightsout.press_button(state, row, col, 2)
    assert lightsout.is_goal(state)


def test_iddfs_3x3_solution_is_valid():
    """Applying the IDDFS solution to a 3x3 grid should produce the goal state."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(3)
    assert solution is not None
    state = lightsout.make_initial_state(3)
    for row, col in solution:
        state = lightsout.press_button(state, row, col, 3)
    assert lightsout.is_goal(state)


def test_iddfs_returns_expanded_and_created():
    """IDDFS should return positive counts for both expanded and created."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(2)
    assert isinstance(expanded, int)
    assert isinstance(created, int)
    assert expanded > 0
    assert created > 0


def test_iddfs_created_gte_expanded():
    """Nodes created should be >= nodes expanded."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(2)
    assert created >= expanded


def test_iddfs_solution_has_no_duplicates():
    """Each button should be pressed at most once in the solution."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(2)
    assert len(solution) == len(set(solution))


def test_iddfs_max_depth_zero_no_solution():
    """max_depth=0 should only find solutions if the initial state is already the goal."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(2, max_depth=0)
    # 2x2 all-ON is not the goal, so no solution at depth 0
    assert solution is None


def test_iddfs_solution_is_tuple():
    """Solution should be a tuple of (row, col) tuples."""
    solution, expanded, created = lightsout.solve_lights_out_iddfs(2)
    assert isinstance(solution, tuple)
    for button in solution:
        assert isinstance(button, tuple)
        assert len(button) == 2


def test_bfs_and_iddfs_same_length():
    """BFS and IDDFS should find solutions of the same length (both optimal)."""
    bfs_sol, _, _ = lightsout.solve_lights_out_bfs(2)
    iddfs_sol, _, _ = lightsout.solve_lights_out_iddfs(2)
    assert len(bfs_sol) == len(iddfs_sol)


def test_dfs_limited_at_goal():
    """dfs_limited should immediately return when given the goal state."""
    goal = ((False, False), (False, False))
    solution, expanded, created = lightsout.dfs_limited(goal, frozenset(), [], 5, 0, 2)
    assert solution is not None
    assert len(solution) == 0  # no presses needed
