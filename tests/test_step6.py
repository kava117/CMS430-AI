"""Step 6 tests — visualization functions."""
import lightsout


def test_print_grid_runs(capsys):
    """print_grid should produce output without errors."""
    state = lightsout.make_initial_state(3)
    lightsout.print_grid(state)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_print_grid_on_symbol(capsys):
    """print_grid should use a filled square for ON cells."""
    state = lightsout.make_initial_state(2)
    lightsout.print_grid(state)
    captured = capsys.readouterr()
    assert "\u25a0" in captured.out


def test_print_grid_off_symbol(capsys):
    """print_grid should use an empty square for OFF cells."""
    state = ((False, False), (False, False))
    lightsout.print_grid(state)
    captured = capsys.readouterr()
    assert "\u25a1" in captured.out


def test_print_grid_row_count(capsys):
    """print_grid for 3x3 should print 3 lines of grid content."""
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
    assert "\u25a0" in captured.out
    assert "\u25a1" in captured.out


def test_print_solution_runs(capsys):
    """print_solution should produce output without errors."""
    solution, _, _ = lightsout.solve_lights_out_bfs(2)
    lightsout.print_solution(solution, 2)
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_print_solution_shows_initial_state(capsys):
    """print_solution should show the initial state."""
    solution, _, _ = lightsout.solve_lights_out_bfs(2)
    lightsout.print_solution(solution, 2)
    captured = capsys.readouterr()
    output_lower = captured.out.lower()
    assert "initial" in output_lower or "\u25a0" in captured.out


def test_print_solution_shows_button_presses(capsys):
    """print_solution should mention each button press."""
    solution, _, _ = lightsout.solve_lights_out_bfs(2)
    lightsout.print_solution(solution, 2)
    captured = capsys.readouterr()
    for row, col in solution:
        assert f"({row}, {col})" in captured.out or f"{row}" in captured.out
