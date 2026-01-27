import json
from unittest.mock import patch


class TestIndex:
    def test_serves_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"html" in resp.data.lower()


class TestStatus:
    def test_returns_ok(self, client):
        resp = client.get("/api/status")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"


class TestFindPathValidation:
    def test_missing_json_body(self, client):
        resp = client.post("/api/find-path", content_type="text/plain", data="hello")
        assert resp.status_code == 400

    def test_empty_start(self, client):
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "", "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_empty_end_whitespace(self, client):
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "   "}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_title_too_long(self, client):
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A" * 257, "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "256" in resp.get_json()["message"]


class TestFindPathBehavior:
    @patch("app.search_find_path")
    def test_successful_search(self, mock_search, client):
        mock_search.return_value = {
            "success": True,
            "path": ["A", "B"],
            "message": "Found path of length 2",
        }
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert body["path"] == ["A", "B"]

    @patch("app.search_find_path")
    def test_article_not_found(self, mock_search, client):
        mock_search.return_value = {
            "success": False,
            "path": None,
            "message": "Article not found: Z",
        }
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "Z", "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 404

    @patch("app.search_find_path", side_effect=Exception("boom"))
    def test_search_exception(self, mock_search, client):
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 500
        assert resp.get_json()["message"] == "Internal server error"


class TestCORS:
    @patch("app.search_find_path")
    def test_cors_on_success(self, mock_search, client):
        mock_search.return_value = {
            "success": True,
            "path": ["A", "B"],
            "message": "Found path of length 2",
        }
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B"}),
            content_type="application/json",
        )
        assert resp.headers["Access-Control-Allow-Origin"] == "*"

    def test_cors_on_error(self, client):
        resp = client.post("/api/find-path", content_type="text/plain", data="bad")
        assert resp.headers["Access-Control-Allow-Origin"] == "*"


class TestWhitespaceTrimming:
    @patch("app.search_find_path")
    def test_trimmed_values_passed(self, mock_search, client):
        mock_search.return_value = {
            "success": True,
            "path": ["A", "B"],
            "message": "Found path of length 2",
        }
        client.post(
            "/api/find-path",
            data=json.dumps({"start": "  A  ", "end": "  B  "}),
            content_type="application/json",
        )
        mock_search.assert_called_once_with("A", "B")
