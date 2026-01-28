"""Step 3 tests — Flask API stub with validation and CORS."""
import json


class TestStatus:
    def test_status_returns_ok(self, client):
        resp = client.get("/api/status")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "ok"


class TestFindPathValidation:
    def test_missing_json_body(self, client):
        """Sending non-JSON body should return 400."""
        resp = client.post("/api/find-path", content_type="text/plain", data="hello")
        assert resp.status_code == 400
        body = resp.get_json()
        assert body["success"] is False

    def test_empty_start(self, client):
        """Empty start field should return 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "", "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_empty_end_whitespace(self, client):
        """Whitespace-only end field should return 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "   "}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_missing_start_key(self, client):
        """Missing 'start' key entirely should return 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_missing_end_key(self, client):
        """Missing 'end' key entirely should return 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A"}),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_title_too_long(self, client):
        """Title exceeding 256 characters should return 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A" * 257, "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 400
        assert "256" in resp.get_json()["message"]


class TestFindPathStub:
    def test_valid_request_returns_200(self, client):
        """Valid request should return 200 with hardcoded response."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["success"] is True
        assert isinstance(body["path"], list)
        assert len(body["path"]) >= 2

    def test_response_has_required_keys(self, client):
        """Response must contain success, path, and message keys."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B"}),
            content_type="application/json",
        )
        body = resp.get_json()
        assert "success" in body
        assert "path" in body
        assert "message" in body

    def test_whitespace_is_trimmed(self, client):
        """Leading/trailing whitespace in titles should not cause a 400."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "  A  ", "end": "  B  "}),
            content_type="application/json",
        )
        assert resp.status_code == 200


class TestCORS:
    def test_cors_headers_on_success(self, client):
        """Successful responses must include CORS headers."""
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B"}),
            content_type="application/json",
        )
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"

    def test_cors_headers_on_error(self, client):
        """Error responses must also include CORS headers."""
        resp = client.post("/api/find-path", content_type="text/plain", data="bad")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"

    def test_cors_allow_methods(self, client):
        """CORS should allow GET, POST, OPTIONS."""
        resp = client.get("/api/status")
        methods = resp.headers.get("Access-Control-Allow-Methods", "")
        assert "GET" in methods
        assert "POST" in methods

    def test_cors_allow_headers(self, client):
        """CORS should allow Content-Type header."""
        resp = client.get("/api/status")
        assert "Content-Type" in resp.headers.get("Access-Control-Allow-Headers", "")
