import os

BASE = os.path.join(os.path.dirname(__file__), '..')

def test_step1_files_exist():
    files = ['simulator.py', 'chromosome.py', 'ga.py', 'main.py', 'requirements.txt']
    for f in files:
        assert os.path.exists(os.path.join(BASE, f)), f"Missing file: {f}"

def test_step1_requirements():
    with open(os.path.join(BASE, 'requirements.txt')) as f:
        contents = f.read()
    assert 'numpy' in contents
    assert 'matplotlib' in contents

def test_step1_tests_directory_exists():
    assert os.path.isdir(os.path.join(BASE, 'tests')), "Missing tests/ directory"

def test_step1_conftest_has_sys_path_fix():
    conftest_path = os.path.join(BASE, 'tests', 'conftest.py')
    assert os.path.exists(conftest_path), "Missing tests/conftest.py"
    with open(conftest_path) as f:
        contents = f.read()
    assert 'sys.path' in contents, "conftest.py must add parent dir to sys.path"
