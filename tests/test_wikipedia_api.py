"""Step 5 tests — wikipedia_api.py with all requests mocked."""
from unittest.mock import patch, MagicMock

import pytest
import requests

import wikipedia_api


# ---------------------------------------------------------------------------
# Fixtures — canned API responses
# ---------------------------------------------------------------------------

@pytest.fixture
def single_page_forward_response():
    return {
        "query": {
            "pages": {
                "123": {
                    "pageid": 123,
                    "title": "Python (programming language)",
                    "links": [
                        {"ns": 0, "title": "Guido van Rossum"},
                        {"ns": 0, "title": "CPython"},
                    ],
                }
            }
        }
    }


@pytest.fixture
def paginated_forward_page1():
    return {
        "continue": {"plcontinue": "abc|def", "continue": "||"},
        "query": {
            "pages": {
                "123": {
                    "pageid": 123,
                    "title": "Python (programming language)",
                    "links": [{"ns": 0, "title": "Guido van Rossum"}],
                }
            }
        },
    }


@pytest.fixture
def paginated_forward_page2():
    return {
        "query": {
            "pages": {
                "123": {
                    "pageid": 123,
                    "title": "Python (programming language)",
                    "links": [{"ns": 0, "title": "CPython"}],
                }
            }
        }
    }


@pytest.fixture
def single_page_backward_response():
    return {
        "query": {
            "pages": {
                "123": {
                    "pageid": 123,
                    "title": "Python (programming language)",
                    "linkshere": [
                        {"ns": 0, "title": "Programming language"},
                        {"ns": 0, "title": "Scripting language"},
                    ],
                }
            }
        }
    }


@pytest.fixture
def article_exists_response():
    return {
        "query": {
            "pages": {"123": {"pageid": 123, "title": "Python (programming language)"}}
        }
    }


@pytest.fixture
def article_missing_response():
    return {"query": {"pages": {"-1": {"title": "Nonexistent", "missing": ""}}}}


def _mock_response(json_data):
    """Create a mock requests.Response that returns the given JSON."""
    resp = MagicMock()
    resp.json.return_value = json_data
    return resp


# ---------------------------------------------------------------------------
# _get tests
# ---------------------------------------------------------------------------

class TestGet:
    @patch("wikipedia_api.requests.get")
    def test_returns_parsed_json(self, mock_get):
        mock_get.return_value = _mock_response({"query": {}})
        result = wikipedia_api._get({"action": "query", "format": "json"})
        assert result == {"query": {}}

    @patch("wikipedia_api.requests.get")
    def test_passes_headers_and_timeout(self, mock_get):
        mock_get.return_value = _mock_response({"query": {}})
        wikipedia_api._get({"action": "query"})
        _, kwargs = mock_get.call_args
        assert "headers" in kwargs
        assert "User-Agent" in kwargs["headers"] or "user-agent" in str(kwargs["headers"]).lower()
        assert kwargs.get("timeout") is not None

    @patch("wikipedia_api.requests.get", side_effect=requests.ConnectionError)
    def test_raises_on_connection_error(self, mock_get):
        with pytest.raises(RuntimeError, match="[Cc]onnect"):
            wikipedia_api._get({"action": "query"})

    @patch("wikipedia_api.requests.get", side_effect=requests.Timeout)
    def test_raises_on_timeout(self, mock_get):
        with pytest.raises(RuntimeError, match="[Tt]imed? ?out"):
            wikipedia_api._get({"action": "query"})

    @patch("wikipedia_api.requests.get")
    def test_raises_on_http_error(self, mock_get):
        mock_resp = MagicMock()
        http_err = requests.HTTPError(response=MagicMock(status_code=500))
        mock_resp.raise_for_status.side_effect = http_err
        mock_get.return_value = mock_resp
        with pytest.raises(RuntimeError, match="500"):
            wikipedia_api._get({"action": "query"})

    @patch("wikipedia_api.requests.get")
    def test_raises_on_invalid_json(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.side_effect = ValueError("No JSON")
        mock_get.return_value = mock_resp
        with pytest.raises(RuntimeError, match="[Ii]nvalid JSON"):
            wikipedia_api._get({"action": "query"})

    @patch("wikipedia_api.requests.get")
    def test_raises_on_api_error_key(self, mock_get):
        mock_get.return_value = _mock_response({"error": {"info": "badtitle"}})
        with pytest.raises(RuntimeError, match="badtitle"):
            wikipedia_api._get({"action": "query"})


# ---------------------------------------------------------------------------
# get_forward_links tests
# ---------------------------------------------------------------------------

class TestGetForwardLinks:
    @patch("wikipedia_api.requests.get")
    def test_single_page(self, mock_get, single_page_forward_response):
        mock_get.return_value = _mock_response(single_page_forward_response)
        result = wikipedia_api.get_forward_links("Python (programming language)")
        assert result == {"Guido van Rossum", "CPython"}

    @patch("wikipedia_api.requests.get")
    def test_pagination(self, mock_get, paginated_forward_page1, paginated_forward_page2):
        mock_get.side_effect = [
            _mock_response(paginated_forward_page1),
            _mock_response(paginated_forward_page2),
        ]
        result = wikipedia_api.get_forward_links("Python (programming language)")
        assert result == {"Guido van Rossum", "CPython"}
        assert mock_get.call_count == 2

    @patch("wikipedia_api.requests.get")
    def test_no_links_returns_empty_set(self, mock_get):
        mock_get.return_value = _mock_response({
            "query": {"pages": {"123": {"pageid": 123, "title": "Stub"}}}
        })
        result = wikipedia_api.get_forward_links("Stub")
        assert result == set()


# ---------------------------------------------------------------------------
# get_backward_links tests
# ---------------------------------------------------------------------------

class TestGetBackwardLinks:
    @patch("wikipedia_api.requests.get")
    def test_single_page(self, mock_get, single_page_backward_response):
        mock_get.return_value = _mock_response(single_page_backward_response)
        result = wikipedia_api.get_backward_links("Python (programming language)")
        assert result == {"Programming language", "Scripting language"}

    @patch("wikipedia_api.requests.get")
    def test_no_backlinks_returns_empty_set(self, mock_get):
        mock_get.return_value = _mock_response({
            "query": {"pages": {"123": {"pageid": 123, "title": "Obscure"}}}
        })
        result = wikipedia_api.get_backward_links("Obscure")
        assert result == set()


# ---------------------------------------------------------------------------
# article_exists tests
# ---------------------------------------------------------------------------

class TestArticleExists:
    @patch("wikipedia_api.requests.get")
    def test_returns_true_for_valid(self, mock_get, article_exists_response):
        mock_get.return_value = _mock_response(article_exists_response)
        assert wikipedia_api.article_exists("Python (programming language)") is True

    @patch("wikipedia_api.requests.get")
    def test_returns_false_for_missing(self, mock_get, article_missing_response):
        mock_get.return_value = _mock_response(article_missing_response)
        assert wikipedia_api.article_exists("Nonexistent") is False
