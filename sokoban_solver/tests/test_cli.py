import subprocess


def test_cli_solve_file(tmp_path):
    puzzle_file = tmp_path / "test_puzzle.txt"
    puzzle_file.write_text("""####
#. #
#$ #
#@ #
####""")

    result = subprocess.run(
        ['python', 'main.py', str(puzzle_file)],
        capture_output=True,
        text=True,
        cwd='/workspaces/CMS430-AI/sokoban_solver',
    )

    assert result.returncode == 0
    assert 'solution' in result.stdout.lower()


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
        text=True,
        cwd='/workspaces/CMS430-AI/sokoban_solver',
    )

    assert 'no solution' in result.stdout.lower()


def test_cli_help():
    result = subprocess.run(
        ['python', 'main.py', '--help'],
        capture_output=True,
        text=True,
        cwd='/workspaces/CMS430-AI/sokoban_solver',
    )

    assert result.returncode == 0
    assert 'usage' in result.stdout.lower() or 'help' in result.stdout.lower()
