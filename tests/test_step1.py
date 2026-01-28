"""Step 1 tests — verify project scaffolding and minimal Flask app."""
import os


def test_app_module_imports():
    """app.py should be importable without errors."""
    import app
    assert hasattr(app, "app"), "app.py must define a Flask instance named 'app'"


def test_flask_instance():
    """The 'app' object should be a Flask application."""
    from app import app
    from flask import Flask
    assert isinstance(app, Flask)


def test_static_folder_exists():
    """The static/ directory must exist."""
    assert os.path.isdir("static"), "static/ directory is missing"


def test_index_html_exists():
    """static/index.html must exist."""
    assert os.path.isfile("static/index.html"), "static/index.html is missing"


def test_index_html_has_title():
    """static/index.html should contain the project title."""
    with open("static/index.html") as f:
        content = f.read()
    assert "Wikipedia Article Chain Finder" in content


def test_index_route(client):
    """GET / should return 200 and serve HTML content."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"html" in resp.data.lower()


def test_search_module_imports():
    """search.py should be importable."""
    import search  # noqa: F401


def test_wikipedia_api_module_imports():
    """wikipedia_api.py should be importable."""
    import wikipedia_api  # noqa: F401
