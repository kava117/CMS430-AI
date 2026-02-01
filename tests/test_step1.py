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
