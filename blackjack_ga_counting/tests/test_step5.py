import os
import subprocess
import time
import pytest

BASE = os.path.join(os.path.dirname(__file__), '..')


@pytest.fixture(scope="session")
def main_result():
    """Run main.py once per test session and return (result, elapsed_seconds)."""
    start = time.time()
    result = subprocess.run(
        ['python', 'main.py'],
        capture_output=True, text=True, timeout=600,
        cwd=BASE
    )
    elapsed = time.time() - start
    return result, elapsed


def test_main_runs_without_error(main_result):
    result, _ = main_result
    assert result.returncode == 0, f"main.py exited with error:\n{result.stderr}"

def test_main_completes_within_time_limit(main_result):
    _, elapsed = main_result
    assert elapsed < 600, f"main.py took {elapsed:.1f}s — exceeds 10-minute limit"

def test_fitness_png_exists(main_result):
    assert os.path.exists(os.path.join(BASE, 'fitness_over_generations.png'))

def test_strategy_heatmap_png_exists(main_result):
    assert os.path.exists(os.path.join(BASE, 'strategy_heatmap.png'))

def test_count_values_png_exists(main_result):
    assert os.path.exists(os.path.join(BASE, 'count_values.png'))

def test_bankroll_over_time_png_exists(main_result):
    assert os.path.exists(os.path.join(BASE, 'bankroll_over_time.png'))

def test_all_pngs_are_nonempty(main_result):
    for fname in ['fitness_over_generations.png', 'strategy_heatmap.png',
                  'count_values.png', 'bankroll_over_time.png']:
        path = os.path.join(BASE, fname)
        size = os.path.getsize(path)
        assert size > 1000, f"{fname} appears empty ({size} bytes)"

def test_stdout_contains_generation_lines(main_result):
    result, _ = main_result
    lines = result.stdout.strip().split('\n')
    gen_lines = [l for l in lines if l.startswith('Gen ')]
    assert len(gen_lines) == 75, f"Expected 75 generation lines, got {len(gen_lines)}"
    assert 'Max:' in gen_lines[0] and 'Mean:' in gen_lines[0]

def test_stdout_generation_lines_use_dollar_amounts(main_result):
    result, _ = main_result
    lines = result.stdout.strip().split('\n')
    gen_lines = [l for l in lines if l.startswith('Gen ')]
    assert '$' in gen_lines[0], f"Generation line missing '$': {gen_lines[0]}"
