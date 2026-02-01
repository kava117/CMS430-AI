"""Step 7 tests — performance comparison and plotting."""
import os

import lightsout


def test_compare_returns_dict():
    """compare_algorithms should return a dictionary."""
    results = lightsout.compare_algorithms([2])
    assert isinstance(results, dict)


def test_compare_has_required_keys():
    """Result dict must have grid_sizes, expanded, and created keys for both algorithms."""
    results = lightsout.compare_algorithms([2])
    assert "grid_sizes" in results
    assert "bfs_expanded" in results
    assert "bfs_created" in results
    assert "iddfs_expanded" in results
    assert "iddfs_created" in results


def test_compare_lists_match_length():
    """All lists in the result should have the same length as the input."""
    sizes = [2, 3]
    results = lightsout.compare_algorithms(sizes)
    assert len(results["grid_sizes"]) == len(sizes)
    assert len(results["bfs_expanded"]) == len(sizes)
    assert len(results["bfs_created"]) == len(sizes)
    assert len(results["iddfs_expanded"]) == len(sizes)
    assert len(results["iddfs_created"]) == len(sizes)


def test_compare_grid_sizes_match():
    """grid_sizes in the result should match the input."""
    sizes = [2, 3]
    results = lightsout.compare_algorithms(sizes)
    assert results["grid_sizes"] == sizes


def test_compare_nodes_are_positive():
    """Node counts should be positive integers."""
    results = lightsout.compare_algorithms([2])
    assert results["bfs_expanded"][0] > 0
    assert results["bfs_created"][0] > 0
    assert results["iddfs_expanded"][0] > 0
    assert results["iddfs_created"][0] > 0


def test_compare_created_gte_expanded():
    """Nodes created should be >= nodes expanded for both algorithms."""
    results = lightsout.compare_algorithms([2])
    assert results["bfs_created"][0] >= results["bfs_expanded"][0]
    assert results["iddfs_created"][0] >= results["iddfs_expanded"][0]


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
    assert "expanded" in captured.out.lower()
    assert "created" in captured.out.lower()
