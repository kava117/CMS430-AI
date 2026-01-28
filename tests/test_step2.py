"""Step 2 tests — verify the HTML page has the required UI elements."""
import os
import re

import pytest


@pytest.fixture
def html():
    with open("static/index.html") as f:
        return f.read()


@pytest.fixture
def css():
    with open("static/style.css") as f:
        return f.read()


@pytest.fixture
def js():
    with open("static/script.js") as f:
        return f.read()


def test_start_input_exists(html):
    """Page must have an input with id='start'."""
    assert 'id="start"' in html or "id='start'" in html


def test_end_input_exists(html):
    """Page must have an input with id='end'."""
    assert 'id="end"' in html or "id='end'" in html


def test_find_button_exists(html):
    """Page must have a button with id='find-btn'."""
    assert "find-btn" in html


def test_results_div_exists(html):
    """Page must have a div with id='results'."""
    assert 'id="results"' in html or "id='results'" in html


def test_loading_indicator_exists(html):
    """Page must have an element with id='loading'."""
    assert 'id="loading"' in html or "id='loading'" in html


def test_css_linked(html):
    """Page must link to style.css."""
    assert "style.css" in html


def test_js_linked(html):
    """Page must link to script.js."""
    assert "script.js" in html


def test_css_hides_loading(css):
    """CSS should hide the loading indicator by default (display: none)."""
    assert "display" in css and "none" in css


def test_js_file_exists():
    """script.js must exist."""
    assert os.path.isfile("static/script.js")


def test_js_has_event_listener(js):
    """script.js should attach a click or submit event listener."""
    assert "addEventListener" in js or "onclick" in js
