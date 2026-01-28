"""Step 4 tests — verify script.js has the required fetch and display logic."""
import os

import pytest


@pytest.fixture
def js():
    with open("static/script.js") as f:
        return f.read()


def test_js_uses_fetch_or_xhr(js):
    """script.js must call the API using fetch() or XMLHttpRequest."""
    assert "fetch(" in js or "XMLHttpRequest" in js


def test_js_targets_api_endpoint(js):
    """script.js must reference the /api/find-path endpoint."""
    assert "/api/find-path" in js


def test_js_sends_post(js):
    """script.js must use the POST method."""
    assert "POST" in js


def test_js_sends_json_content_type(js):
    """script.js must set Content-Type to application/json."""
    assert "application/json" in js


def test_js_references_loading_indicator(js):
    """script.js must show/hide the loading indicator."""
    assert "loading" in js


def test_js_references_results_area(js):
    """script.js must write results to the results area."""
    assert "results" in js


def test_js_creates_wikipedia_links(js):
    """script.js must create links to Wikipedia articles."""
    assert "en.wikipedia.org/wiki/" in js


def test_js_disables_button(js):
    """script.js should disable the button during requests."""
    assert "disabled" in js


def test_js_handles_errors(js):
    """script.js should have error-handling logic (catch block or error check)."""
    assert "catch" in js or "onerror" in js or "error" in js.lower()
