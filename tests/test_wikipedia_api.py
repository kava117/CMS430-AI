from unittest.mock import patch, MagicMock

import pytest
import requests

import wikipedia_api


class TestGet:
    """Tests for wikipedia_api._get."""

    @patch("wikipedia_api.requests.get")
    def test_returns_parsed_json(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"query": {}}
        mock_get.return_value = mock_resp

        result = wikipedia_api._get({"action": "query", "format": "json"})
        assert result == {"query": {}}

    @patch("wikipedia_api.requests.get", side_effect=requests.ConnectionError)
    def test_raises_on_connection_error(self, mock_get):
        with pytest.raises(RuntimeError, match="Could not connect"):
            wikipedia_api._get({"action": "query"})

    @patch("wikipedia_api.requests.get", side_effect=requests.Timeout)
    def test_raises_on_timeout(self, mock_get):
        with pytest.raises(RuntimeError, match="timed out"):
            wikipedia_api._get({"action": "query"})

    @patch("wikipedia_api.requests.get")
    def test_raises_on_http_error(self, mock_get):
        mock_resp = MagicMock()
        http_err = requests.HTTPError(response=MagicMock(status_code=500))
        mock_resp.raise_for_status.side_effect = http_err
        mock_get.return_value = mock_resp

        with pytest.raises(RuntimeError, match="HTTP 500"):
            wikipedia_api._get({"action": "query"})

    @patch("wikipedia_api.requests.get")
    def test_raises_on_invalid_json(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.side_effect = ValueError("No JSON")
        mock_get.return_value = mock_resp

        with pytest.raises(RuntimeError, match="invalid JSON"):
            wikipedia_api._get({"action": "query"})

    @patch("wikipedia_api.requests.get")
    def test_raises_on_api_error(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"error": {"info": "badtitle"}}
        mock_get.return_value = mock_resp

        with pytest.raises(RuntimeError, match="badtitle"):
            wikipedia_api._get({"action": "query"})


class TestGetForwardLinks:
    """Tests for wikipedia_api.get_forward_links."""

    @patch("wikipedia_api.requests.get")
    def test_single_page(self, mock_get, single_page_forward_response):
        mock_resp = MagicMock()
        mock_resp.json.return_value = single_page_forward_response
        mock_get.return_value = mock_resp

        result = wikipedia_api.get_forward_links("Python (programming language)")
        assert result == {"Guido van Rossum", "CPython"}

    @patch("wikipedia_api.requests.get")
    def test_pagination(
        self, mock_get, paginated_forward_response_page1, paginated_forward_response_page2
    ):
        resp1 = MagicMock()
        resp1.json.return_value = paginated_forward_response_page1
        resp2 = MagicMock()
        resp2.json.return_value = paginated_forward_response_page2
        mock_get.side_effect = [resp1, resp2]

        result = wikipedia_api.get_forward_links("Python (programming language)")
        assert result == {"Guido van Rossum", "CPython"}
        assert mock_get.call_count == 2


class TestGetBackwardLinks:
    """Tests for wikipedia_api.get_backward_links."""

    @patch("wikipedia_api.requests.get")
    def test_single_page(self, mock_get, single_page_backward_response):
        mock_resp = MagicMock()
        mock_resp.json.return_value = single_page_backward_response
        mock_get.return_value = mock_resp

        result = wikipedia_api.get_backward_links("Python (programming language)")
        assert result == {"Programming language", "Scripting language"}


class TestArticleExists:
    """Tests for wikipedia_api.article_exists."""

    @patch("wikipedia_api.requests.get")
    def test_returns_true_for_valid(self, mock_get, article_exists_response):
        mock_resp = MagicMock()
        mock_resp.json.return_value = article_exists_response
        mock_get.return_value = mock_resp

        assert wikipedia_api.article_exists("Python (programming language)") is True

    @patch("wikipedia_api.requests.get")
    def test_returns_false_for_missing(self, mock_get, article_missing_response):
        mock_resp = MagicMock()
        mock_resp.json.return_value = article_missing_response
        mock_get.return_value = mock_resp

        assert wikipedia_api.article_exists("Nonexistent") is False
