from unittest.mock import patch

import search


def _mock_exists(valid_titles):
    """Return an article_exists mock that recognises only the given titles."""
    return lambda title: title in valid_titles


class TestFindPath:
    """Tests for search.find_path."""

    @patch("search.article_exists")
    def test_same_start_and_end(self, mock_exists):
        mock_exists.return_value = True
        result = search.find_path("A", "A")
        assert result["success"] is True
        assert result["path"] == ["A"]

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

    @patch("search.get_backward_links", return_value=set())
    @patch("search.get_forward_links", return_value={"B"})
    @patch("search.article_exists", return_value=True)
    def test_direct_link(self, mock_exists, mock_fwd, mock_bwd):
        """A links directly to B — path should be [A, B]."""
        result = search.find_path("A", "B")
        assert result["success"] is True
        assert result["path"] == ["A", "B"]

    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_two_hop(self, mock_exists, mock_fwd, mock_bwd):
        """A→M, M→B  — path should be [A, M, B]."""
        mock_fwd.side_effect = lambda t: {"M"} if t == "A" else set()
        mock_bwd.side_effect = lambda t: {"M"} if t == "B" else set()

        result = search.find_path("A", "B")
        assert result["success"] is True
        assert result["path"] == ["A", "M", "B"]

    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_meeting_via_backward(self, mock_exists, mock_fwd, mock_bwd):
        """Forward finds {X}, backward finds {X} — they meet at X."""
        mock_fwd.side_effect = lambda t: {"X"} if t == "A" else set()
        mock_bwd.side_effect = lambda t: {"X"} if t == "B" else set()

        result = search.find_path("A", "B")
        assert result["success"] is True
        assert "X" in result["path"]

    @patch("search.get_backward_links", return_value=set())
    @patch("search.get_forward_links", return_value=set())
    @patch("search.article_exists", return_value=True)
    def test_no_path(self, mock_exists, mock_fwd, mock_bwd):
        result = search.find_path("A", "B")
        assert result["success"] is False
        assert "No path found" in result["message"]

    @patch("search.get_backward_links", return_value=set())
    @patch("search.get_forward_links", side_effect=RuntimeError("API failure"))
    @patch("search.article_exists", return_value=True)
    def test_api_exception_skipped(self, mock_exists, mock_fwd, mock_bwd):
        """Exception during link expansion should be swallowed, resulting in no path."""
        result = search.find_path("A", "B")
        assert result["success"] is False

    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_shortest_path_chosen(self, mock_exists, mock_fwd, mock_bwd):
        """When multiple meeting points exist, the shortest path wins."""
        # A→M1, A→X→M2; backward B→M1, B→M2
        # M1 gives path len 2, M2 would also give len 2 via different route
        mock_fwd.side_effect = lambda t: {"M1", "M2"} if t == "A" else set()
        mock_bwd.side_effect = lambda t: set()

        # M1 and M2 are both directly linked from A, and B is the end.
        # backward_visited starts with {B}. forward adds {M1, M2}.
        # For them to meet, backward must also contain M1 or M2.
        mock_bwd.side_effect = lambda t: {"M1", "M2"} if t == "B" else set()

        result = search.find_path("A", "B")
        assert result["success"] is True
        assert len(result["path"]) == 3  # A → Mx → B

    @patch("search.get_backward_links")
    @patch("search.get_forward_links")
    @patch("search.article_exists", return_value=True)
    def test_longer_chain(self, mock_exists, mock_fwd, mock_bwd):
        """A→B→C→D via forward search meeting backward at C."""
        mock_fwd.side_effect = lambda t: {"B"} if t == "A" else {"C"} if t == "B" else set()
        mock_bwd.side_effect = lambda t: {"C"} if t == "D" else set()

        result = search.find_path("A", "D")
        assert result["success"] is True
        assert result["path"] == ["A", "B", "C", "D"]
