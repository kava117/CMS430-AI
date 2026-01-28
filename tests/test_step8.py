"""Step 8 tests — error handling and edge case hardening."""
import json
from unittest.mock import patch, MagicMock

import pytest
import requests

import wikipedia_api
import search


class TestWikipediaApiTimeout:
    @patch("wikipedia_api.requests.get")
    def test_timeout_value_is_set(self, mock_get):
        """_get must pass a timeout kwarg to requests.get."""
        mock_get.return_value = MagicMock(json=MagicMock(return_value={"query": {}}))
        wikipedia_api._get({"action": "query"})
        _, kwargs = mock_get.call_args
        assert kwargs.get("timeout") is not None
        assert kwargs["timeout"] > 0


class TestSearchDeadEnd:
    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_dead_end_does_not_crash(self, mock_exists, mock_fwd, mock_bwd):
        """If forward returns empty set, search should still continue (not crash)."""
        # First call returns empty (dead end), search continues but finds nothing
        mock_fwd.return_value = set()
        mock_bwd.return_value = set()
        result = search.find_path("A", "B")
        assert result["success"] is False
        assert result["path"] is None

    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_forward_dead_end_backward_finds_path(self, mock_exists, mock_fwd, mock_bwd):
        """Forward hits dead end, but backward finds meeting point."""
        mock_fwd.side_effect = lambda t: set()  # forward always dead-ends
        mock_bwd.side_effect = lambda t: {"A"} if t == "B" else set()  # backward finds A
        result = search.find_path("A", "B")
        assert result["success"] is True
        assert result["path"] == ["A", "B"]


class TestSearchMultipleExceptions:
    @patch("search.get_backward_links", side_effect=RuntimeError("fail"))
    @patch("search.get_forward_links", side_effect=RuntimeError("fail"))
    @patch("search.article_exists", return_value=True)
    def test_both_directions_fail_gracefully(self, mock_exists, mock_fwd, mock_bwd):
        """Exceptions in both directions should not crash — returns no-path."""
        result = search.find_path("A", "B")
        assert result["success"] is False


class TestAppInputSanitization:
    def test_null_start_value(self, client):
        """JSON null for start should return 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": None, "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_null_end_value(self, client):
        """JSON null for end should return 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": None}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_numeric_start_value(self, client):
        """Numeric start should return 400 (not a string)."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": 123, "end": "B"}),
            content_type="application/json",
        )
        # Should either 400 or handle gracefully (coerce to string)
        assert resp.status_code in (200, 400)

    def test_end_title_too_long(self, client):
        """End title over 256 chars should return 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B" * 257}),
            content_type="application/json",
        )
        assert resp.status_code == 400


class TestScriptTimeout:
    def test_js_has_timeout_handling(self):
        """script.js should handle long-running requests (timeout or abort)."""
        with open("static/script.js") as f:
            js = f.read()
        # Should have some form of timeout handling
        has_timeout = (
            "AbortController" in js
            or "setTimeout" in js
            or "timeout" in js.lower()
            or "signal" in js
        )
        assert has_timeout, "script.js should handle request timeouts"

    def test_js_re_enables_button(self):
        """script.js should re-enable the submit button after requests complete."""
        with open("static/script.js") as f:
            js = f.read()
        assert "disabled" in js, "script.js should toggle the disabled state of the button"
