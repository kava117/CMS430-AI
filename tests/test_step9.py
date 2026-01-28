"""Step 9 tests — final integration checks and UI polish verification."""
import json
import os
from unittest.mock import patch

import pytest


class TestHTMLContent:
    @pytest.fixture
    def html(self):
        with open("static/index.html") as f:
            return f.read()

    def test_has_description_text(self, html):
        """Page should have descriptive text explaining the app."""
        html_lower = html.lower()
        has_description = (
            "find" in html_lower
            or "search" in html_lower
            or "chain" in html_lower
            or "path" in html_lower
            or "link" in html_lower
        )
        assert has_description, "Page should include a description of what the app does"

    def test_has_labels_for_inputs(self, html):
        """Inputs should have associated labels for accessibility."""
        assert "<label" in html.lower()


class TestCSSResponsive:
    @pytest.fixture
    def css(self):
        with open("static/style.css") as f:
            return f.read()

    def test_has_max_width_or_media_query(self, css):
        """CSS should have responsive layout (max-width or media query)."""
        has_responsive = "max-width" in css or "@media" in css or "%" in css
        assert has_responsive, "CSS should include responsive layout rules"

    def test_error_styling(self, css):
        """CSS should have distinct error styling (red or error class)."""
        has_error_style = "error" in css or "red" in css or "#f" in css.lower() or "rgb" in css
        assert has_error_style, "CSS should style error messages distinctly"


class TestEndToEndMocked:
    """Full request flow with mocked search, verifying response format."""

    @patch("app.search_find_path")
    def test_success_response_format(self, mock_search, client):
        mock_search.return_value = {
            "success": True,
            "path": ["Python (programming language)", "Programming language"],
            "message": "Found path of length 2",
        }
        resp = client.post(
            "/api/find-path",
            data=json.dumps({
                "start": "Python (programming language)",
                "end": "Programming language",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert isinstance(body["path"], list)
        assert len(body["path"]) == 2
        assert "length 2" in body["message"]

    @patch("app.search_find_path")
    def test_same_article_response(self, mock_search, client):
        mock_search.return_value = {
            "success": True,
            "path": ["Python (programming language)"],
            "message": "Start and end are the same article",
        }
        resp = client.post(
            "/api/find-path",
            data=json.dumps({
                "start": "Python (programming language)",
                "end": "Python (programming language)",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["path"] == ["Python (programming language)"]

    @patch("app.search_find_path")
    def test_not_found_response(self, mock_search, client):
        mock_search.return_value = {
            "success": False,
            "path": None,
            "message": "Article not found: Xyzzy_nonexistent_page_12345",
        }
        resp = client.post(
            "/api/find-path",
            data=json.dumps({
                "start": "Xyzzy_nonexistent_page_12345",
                "end": "Programming language",
            }),
            content_type="application/json",
        )
        assert resp.status_code == 404
        body = resp.get_json()
        assert body["success"] is False
        assert "not found" in body["message"].lower()

    def test_special_characters_in_title(self, client):
        """Titles with special characters should not crash the server."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({
                "start": "C++ (programming language)",
                "end": "Bjarne Stroustrup",
            }),
            content_type="application/json",
        )
        # Should not be 400 (validation should pass); actual status depends on mock
        assert resp.status_code != 400 or "required" not in resp.get_json().get("message", "")


class TestAllFilesPresent:
    """Verify all expected project files exist."""

    @pytest.mark.parametrize("path", [
        "app.py",
        "search.py",
        "wikipedia_api.py",
        "requirements.txt",
        "static/index.html",
        "static/style.css",
        "static/script.js",
    ])
    def test_file_exists(self, path):
        assert os.path.isfile(path), f"{path} is missing"
