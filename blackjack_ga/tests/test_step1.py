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
