def test_imports():
    import core
    import solver
    import visualization
    assert True


def test_python_version():
    import sys
    assert sys.version_info >= (3, 8)
