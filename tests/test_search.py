"""Step 6 tests — bidirectional search with mocked wikipedia_api calls."""
from unittest.mock import patch

import search


def _mock_exists(valid_titles):
    """Return an article_exists mock that recognises only the given titles."""
    return lambda title: title in valid_titles


class TestSameArticle:
    @patch("search.article_exists", return_value=True)
    def test_same_start_and_end(self, mock_exists):
        result = search.find_path("A", "A")
        assert result["success"] is True
        assert result["path"] == ["A"]


class TestArticleValidation:
    @patch("search.article_exists", side_effect=_mock_exists({"B"}))
    def test_start_not_found(self, mock_exists):
        result = search.find_path("A", "B")
        assert result["success"] is False
        assert "Article not found: A" in result["message"]

    @patch("search.article_exists", side_effect=_mock_exists({"A"}))
    def test_end_not_found(self, mock_exists):
        result = search.find_path("A", "B")
        assert result["success"] is False
        assert "Article not found: B" in result["message"]


class TestDirectLink:
    @patch("search.get_backward_links", return_value=set())
    @patch("search.get_forward_links", return_value={"B"})
    @patch("search.article_exists", return_value=True)
    def test_one_hop_forward(self, mock_exists, mock_fwd, mock_bwd):
        """A links directly to B — path [A, B]."""
        result = search.find_path("A", "B")
        assert result["success"] is True
        assert result["path"] == ["A", "B"]


class TestTwoHop:
    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_two_hop_via_meeting(self, mock_exists, mock_fwd, mock_bwd):
        """A→M, backward B→M — path [A, M, B]."""
        mock_fwd.side_effect = lambda t: {"M"} if t == "A" else set()
        mock_bwd.side_effect = lambda t: {"M"} if t == "B" else set()
        result = search.find_path("A", "B")
        assert result["success"] is True
        assert result["path"] == ["A", "M", "B"]


class TestMeetingViaBackward:
    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_meeting_found_backward(self, mock_exists, mock_fwd, mock_bwd):
        """Forward finds {X}, backward finds {X} — they meet at X."""
        mock_fwd.side_effect = lambda t: {"X"} if t == "A" else set()
        mock_bwd.side_effect = lambda t: {"X"} if t == "B" else set()
        result = search.find_path("A", "B")
        assert result["success"] is True
        assert "X" in result["path"]


class TestNoPath:
    @patch("search.get_backward_links", return_value=set())
    @patch("search.get_forward_links", return_value=set())
    @patch("search.article_exists", return_value=True)
    def test_empty_links_no_path(self, mock_exists, mock_fwd, mock_bwd):
        result = search.find_path("A", "B")
        assert result["success"] is False
        assert "No path found" in result["message"]


class TestExceptionHandling:
    @patch("search.get_backward_links", return_value=set())
    @patch("search.get_forward_links", side_effect=RuntimeError("API failure"))
    @patch("search.article_exists", return_value=True)
    def test_api_exception_is_skipped(self, mock_exists, mock_fwd, mock_bwd):
        """Exception during expansion should be caught — search continues."""
        result = search.find_path("A", "B")
        assert result["success"] is False  # no path, but no crash


class TestShortestPath:
    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_shortest_among_multiple_meeting_points(self, mock_exists, mock_fwd, mock_bwd):
        """Two meeting points exist — the shorter path wins."""
        mock_fwd.side_effect = lambda t: {"M1", "M2"} if t == "A" else set()
        mock_bwd.side_effect = lambda t: {"M1", "M2"} if t == "B" else set()
        result = search.find_path("A", "B")
        assert result["success"] is True
        assert len(result["path"]) == 3  # A → Mx → B


class TestLongerChain:
    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_four_node_path(self, mock_exists, mock_fwd, mock_bwd):
        """A→B→C, backward D→C — path [A, B, C, D]."""
        mock_fwd.side_effect = lambda t: {"B"} if t == "A" else {"C"} if t == "B" else set()
        mock_bwd.side_effect = lambda t: {"C"} if t == "D" else set()
        result = search.find_path("A", "D")
        assert result["success"] is True
        assert result["path"] == ["A", "B", "C", "D"]


class TestReturnFormat:
    @patch("search.get_backward_links", return_value=set())
    @patch("search.get_forward_links", return_value={"B"})
    @patch("search.article_exists", return_value=True)
    def test_result_has_required_keys(self, mock_exists, mock_fwd, mock_bwd):
        """Result dict must always have success, path, and message."""
        result = search.find_path("A", "B")
        assert "success" in result
        assert "path" in result
        assert "message" in result
