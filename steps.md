# Wikipedia Article Chain Finder - Implementation Steps

Each step below builds on the previous ones. Complete them in order. Every step that adds Python code includes a **Tests** section with `pytest` test cases. Run the tests after implementing the step — all tests must pass before moving to the next step.

---

## Step 1: Project Scaffolding

Create the project directory structure and install dependencies.

**Tasks:**
1. Create the following file structure:
   ```
   project/
   ├── app.py
   ├── search.py
   ├── wikipedia_api.py
   ├── static/
   │   ├── index.html
   │   ├── style.css
   │   └── script.js
   ├── tests/
   │   └── __init__.py
   └── requirements.txt
   ```
2. Write `requirements.txt` with:
   ```
   Flask
   requests
   pytest
   ```
3. Install dependencies with `pip install -r requirements.txt`.
4. In `app.py`, create a minimal Flask app that serves `static/index.html` at the root route (`/`) and returns a simple page.
5. In `static/index.html`, add a basic HTML5 page with the title "Wikipedia Article Chain Finder".
6. Leave `search.py` and `wikipedia_api.py` as empty files (or with placeholder comments).

**Tests:**

Create `tests/test_step1.py`:

```python
"""Step 1 tests — verify project scaffolding and minimal Flask app."""
import importlib
import os

import pytest


def test_app_module_imports():
    """app.py should be importable without errors."""
    import app
    assert hasattr(app, "app"), "app.py must define a Flask instance named 'app'"


def test_flask_instance():
    """The 'app' object should be a Flask application."""
    from app import app
    from flask import Flask
    assert isinstance(app, Flask)


def test_static_folder_exists():
    """The static/ directory must exist."""
    assert os.path.isdir("static"), "static/ directory is missing"


def test_index_html_exists():
    """static/index.html must exist."""
    assert os.path.isfile("static/index.html"), "static/index.html is missing"


def test_index_html_has_title():
    """static/index.html should contain the project title."""
    with open("static/index.html") as f:
        content = f.read()
    assert "Wikipedia Article Chain Finder" in content


def test_index_route(client):
    """GET / should return 200 and serve HTML content."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"html" in resp.data.lower()


def test_search_module_imports():
    """search.py should be importable."""
    import search  # noqa: F401


def test_wikipedia_api_module_imports():
    """wikipedia_api.py should be importable."""
    import wikipedia_api  # noqa: F401


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c
```

Run: `pytest tests/test_step1.py -v`

All 8 tests must pass.

**Acceptance criteria:**
- Running `python app.py` starts a Flask dev server.
- Visiting `http://localhost:5000/` in a browser shows the HTML page.
- `pytest tests/test_step1.py -v` passes all 8 tests.

---

## Step 2: Frontend UI Layout

Build the complete user interface (no functionality yet).

**Tasks:**
1. In `static/index.html`:
   - Add two labeled text input fields: "Start Article" (`id="start"`) and "End Article" (`id="end"`).
   - Add a "Find Path" submit button (`id="find-btn"`).
   - Add a results container `<div>` (`id="results"`), empty for now.
   - Add a loading indicator element (`id="loading"`), hidden by default.
   - Link `style.css` and `script.js`.
2. In `static/style.css`:
   - Style the page with a clean, centered layout.
   - Style the input fields, button, results area, and loading indicator.
   - The loading indicator should be hidden by default (`display: none`).
3. In `static/script.js`:
   - Add an event listener on the submit button.
   - On click, read the values of both inputs, trim whitespace, and log them to the console.
   - Validate that neither input is empty; if either is, display an inline error message in the results area.

**Tests:**

Create `tests/test_step2.py`:

```python
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
```

Run: `pytest tests/test_step2.py -v`

All 10 tests must pass.

**Acceptance criteria:**
- The page renders two inputs, a button, and a results area.
- Clicking the button with empty inputs shows an error message.
- Clicking the button with filled inputs logs the values to the console.
- `pytest tests/test_step2.py -v` passes all 10 tests.

---

## Step 3: Flask API Endpoint (Stub)

Create the `/api/find-path` endpoint that accepts input and returns a hardcoded response.

**Tasks:**
1. In `app.py`:
   - Add a `POST /api/find-path` route that accepts JSON with `start` and `end` fields.
   - Validate that both fields are present and non-empty (after stripping whitespace). Return a 400 error with a JSON error message if not.
   - Reject titles longer than 256 characters with a 400 error.
   - For now, return a hardcoded success response:
     ```json
     {
       "success": true,
       "path": ["Start", "End"],
       "message": "Found path of length 2"
     }
     ```
   - Add a `GET /api/status` health-check route returning `{"status": "ok"}`.
   - Add CORS headers to all responses (set `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Headers: Content-Type`, `Access-Control-Allow-Methods: GET, POST, OPTIONS`).

**Tests:**

Create `tests/conftest.py` (shared fixtures for all future test files):

```python
"""Shared pytest fixtures."""
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c
```

Create `tests/test_step3.py`:

```python
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
```

Run: `pytest tests/test_step3.py -v`

All 13 tests must pass.

**Acceptance criteria:**
- `POST /api/find-path` with valid JSON returns the hardcoded success response (200).
- `POST /api/find-path` with missing/empty fields returns 400.
- `GET /api/status` returns `{"status": "ok"}` (200).
- CORS headers are present on all responses.
- `pytest tests/test_step3.py -v` passes all 13 tests.

---

## Step 4: Connect Frontend to Backend

Wire the frontend to call the API and display results.

**Tasks:**
1. In `static/script.js`:
   - On button click, show the loading indicator and hide the results area.
   - Send a `POST` request to `/api/find-path` with the JSON body `{"start": "...", "end": "..."}`.
   - On success, hide the loading indicator and display the returned path in the results area. Render each article title as a clickable link to `https://en.wikipedia.org/wiki/ARTICLE_TITLE` (URL-encode the title). Separate articles with arrows (`→`).
   - On failure (non-2xx response or `success: false`), display the error message in the results area.
   - On network error, display a generic "Something went wrong" message.
   - Disable the submit button while a request is in flight to prevent duplicate submissions.

**Tests:**

Create `tests/test_step4.py`:

```python
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
```

Run: `pytest tests/test_step4.py -v`

All 9 tests must pass.

**Acceptance criteria:**
- Clicking "Find Path" shows the loading indicator, then displays the hardcoded path as clickable Wikipedia links.
- The loading indicator disappears when results appear.
- Error states display user-friendly messages.
- `pytest tests/test_step4.py -v` passes all 9 tests.

---

## Step 5: Wikipedia API Wrapper

Implement functions to fetch links from the Wikipedia API.

**Tasks:**
1. In `wikipedia_api.py`, implement the following:

   **Private helper `_get(params: dict) -> dict`**
   - Make a GET request to `https://en.wikipedia.org/w/api.php` with the given params.
   - Set a `User-Agent` header (e.g., `"WikipediaChainFinder/1.0 (CMS430-AI project)"`).
   - Set a timeout of 15 seconds.
   - Call `resp.raise_for_status()` and convert specific `requests` exceptions to `RuntimeError`:
     - `ConnectionError` → "Could not connect to Wikipedia API"
     - `Timeout` → "Wikipedia API request timed out"
     - `HTTPError` → "Wikipedia API returned HTTP {status_code}"
   - Parse JSON; raise `RuntimeError` on `ValueError`.
   - Check for `"error"` key in response; raise `RuntimeError` with the error info.
   - Return the parsed JSON dict.

   **`get_forward_links(title: str) -> set[str]`**
   - Use `_get` with `action=query`, `prop=links`, `pllimit=max`, `plnamespace=0`.
   - Handle pagination via the `continue` key.
   - Return a set of linked article titles.

   **`get_backward_links(title: str) -> set[str]`**
   - Use `_get` with `action=query`, `prop=linkshere`, `lhlimit=max`, `lhnamespace=0`.
   - Handle pagination via the `continue` key.
   - Return a set of article titles that link to the given article.

   **`article_exists(title: str) -> bool`**
   - Use `_get` to query the title.
   - Return `False` if page ID is `"-1"` or page has `"missing"` key.
   - Return `True` otherwise.

**Tests:**

Create `tests/test_wikipedia_api.py`:

```python
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
```

Run: `pytest tests/test_wikipedia_api.py -v`

All 14 tests must pass.

**Acceptance criteria:**
- All three public functions work correctly with mocked responses.
- Error cases raise `RuntimeError` with descriptive messages.
- Pagination is handled (multiple API calls made until `continue` is absent).
- `pytest tests/test_wikipedia_api.py -v` passes all 14 tests.

---

## Step 6: Bidirectional Search Algorithm

Implement the core search logic.

**Tasks:**
1. In `search.py`, implement:

   **`find_path(start: str, end: str) -> dict`**
   - Return immediately if `start == end` with `{"success": True, "path": [start], "message": "Start and end are the same article"}`.
   - Validate both articles exist using `article_exists()`. Return a failure dict if either is invalid: `{"success": False, "path": None, "message": "Article not found: <title>"}`.
   - Implement bidirectional search:
     - Maintain for each direction: `frontier`, `visited` (set), `parents` (dict mapping article → parent).
     - Initialize forward: `frontier={start}`, `visited={start}`, `parents={start: None}`.
     - Initialize backward: `frontier={end}`, `visited={end}`, `parents={end: None}`.
     - On each iteration (up to `MAX_DEPTH = 3`):
       1. Expand forward frontier using `get_forward_links`. If an API call raises an exception, skip that article and continue.
       2. Check intersection of `forward_visited` and `backward_visited`. If found, reconstruct path and return.
       3. Expand backward frontier using `get_backward_links`. Same exception handling.
       4. Check intersection again.
     - If no intersection after all iterations, return `{"success": False, "path": None, "message": "No path found within depth limit"}`.

   **`_build_result(meeting, forward_parents, backward_parents) -> dict`**
   - For each meeting point, reconstruct the path. Return the shortest one.

   **`_reconstruct(meeting, forward_parents, backward_parents) -> list[str]`**
   - Walk from meeting point back through `forward_parents` to start (reverse it).
   - Walk from meeting point forward through `backward_parents` to end.
   - Return concatenated path.

**Tests:**

Create `tests/test_search.py`:

```python
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
```

Run: `pytest tests/test_search.py -v`

All 11 tests must pass.

**Acceptance criteria:**
- Same-article returns immediately.
- Invalid articles return failure with clear messages.
- Direct links, two-hop, and longer chains are found.
- API exceptions during expansion are caught and skipped.
- The shortest path is chosen among multiple meeting points.
- `pytest tests/test_search.py -v` passes all 11 tests.

---

## Step 7: Integrate Search into the API

Replace the hardcoded API response with the real search.

**Tasks:**
1. In `app.py`:
   - Import `find_path` from `search.py` (e.g., `from search import find_path as search_find_path`).
   - In the `POST /api/find-path` handler, replace the hardcoded response: call `search_find_path(start, end)` and return the result as JSON.
   - Wrap the call in a try/except. Return a 500 response with `{"success": false, "path": null, "message": "Internal server error"}` on unexpected exceptions.
   - If `find_path` returns `success: false`, return HTTP 404.
   - If `find_path` returns `success: true`, return HTTP 200.

**Tests:**

Create `tests/test_app.py`:

```python
"""Step 7 tests — full Flask app with mocked search backend."""
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
        assert resp.get_json()["success"] is False

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
    def test_successful_search_returns_200(self, mock_search, client):
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
    def test_article_not_found_returns_404(self, mock_search, client):
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
    def test_search_exception_returns_500(self, mock_search, client):
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 500
        assert resp.get_json()["message"] == "Internal server error"

    @patch("app.search_find_path")
    def test_no_path_found_returns_404(self, mock_search, client):
        mock_search.return_value = {
            "success": False,
            "path": None,
            "message": "No path found within depth limit",
        }
        resp = client.post(
            "/api/find-path",
            data=json.dumps({"start": "A", "end": "B"}),
            content_type="application/json",
        )
        assert resp.status_code == 404


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
    def test_trimmed_values_passed_to_search(self, mock_search, client):
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
```

Run: `pytest tests/test_app.py -v`

All 14 tests must pass.

**Acceptance criteria:**
- The full flow works end-to-end: enter two article titles in the browser, click "Find Path", and see the real chain of Wikipedia articles displayed as clickable links.
- Invalid article titles show a clear error message (404).
- Server errors are caught and returned as 500 responses.
- `pytest tests/test_app.py -v` passes all 14 tests.

---

## Step 8: Error Handling and Edge Cases

Harden the application against failure modes.

**Tasks:**
1. In `wikipedia_api.py`:
   - Verify the request timeout is set (e.g., 15 seconds).
   - Verify HTTP errors (non-200 status codes) are handled gracefully.
   - Verify JSON decoding errors are handled.
   (These should already be done if Step 5 was implemented correctly. If not, fix them now.)
2. In `search.py`:
   - Verify that a frontier expansion returning zero new articles (dead end) does not crash — the search continues with the other direction.
   - Verify that API call failures during search are caught and the article is skipped.
   (These should already be done if Step 6 was implemented correctly. If not, fix them now.)
3. In `app.py`:
   - Verify input sanitization: trim whitespace, reject empty strings, reject excessively long titles (>256 chars).
   (This should already be done if Step 3 was implemented correctly. If not, fix them now.)
4. In `static/script.js`:
   - Add a timeout for fetch requests (show "The search is taking too long" if the request exceeds 90 seconds).
   - Ensure the submit button re-enables after results or errors are displayed.

**Tests:**

Create `tests/test_step8.py`:

```python
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
```

Run: `pytest tests/test_step8.py -v`

All 9 tests must pass.

**Acceptance criteria:**
- Entering a non-existent article shows "Article not found" (not a server crash).
- Dead-end articles do not crash the search.
- Both-direction API failures are handled gracefully.
- The submit button re-enables after every request.
- `pytest tests/test_step8.py -v` passes all 9 tests.

---

## Step 9: Polish and Final Testing

Clean up the UI and verify the full application.

**Tasks:**
1. In `static/style.css`:
   - Ensure the page is responsive and looks reasonable on mobile screens.
   - Style the path results clearly (arrows with clickable links).
   - Style error messages distinctly (e.g., red text or a colored border).
2. In `static/index.html`:
   - Add a brief description or instructions below the title explaining what the app does.
3. Test the following cases manually in the browser and fix any issues:
   - Same start and end article.
   - Closely related articles (e.g., "Python (programming language)" → "Programming language").
   - Non-existent article title.
   - Empty input fields.
   - Articles with special characters in titles.
4. Verify that the path length shown in the message matches the actual path length displayed.

**Tests:**

Create `tests/test_step9.py`:

```python
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
```

Run: `pytest tests/test_step9.py -v`

All 10 tests must pass.

**Full suite run:** `pytest -v`

All tests across all files should pass. No network access required.

**Acceptance criteria:**
- All test cases produce correct, user-friendly results.
- The page looks clean and is usable.
- No unhandled errors appear in the browser console or server logs during testing.
- `pytest -v` passes all tests across the entire test suite.

---

## Step 10: SQLite Cache for Wikipedia Links

Add a caching layer to avoid redundant Wikipedia API calls for previously fetched links.

**Tasks:**
1. Create `cache.py` with SQLite-based caching:
   - Database stored at `links_cache.db`
   - Table schema:
     ```sql
     CREATE TABLE IF NOT EXISTS links (
         source TEXT NOT NULL,
         target TEXT NOT NULL,
         direction TEXT NOT NULL,
         cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         PRIMARY KEY (source, target, direction)
     );
     CREATE INDEX IF NOT EXISTS idx_source_direction ON links(source, direction);
     ```
   - Implement `init_db()` to initialize the database and create tables.
   - Implement `get_cached_links(title: str, direction: str) -> set[str] | None` to retrieve cached links or return `None` if not cached.
   - Implement `cache_links(title: str, links: set[str], direction: str)` to store links in the cache.
   - Implement `clear_cache()` to delete all cached data.

2. Modify `wikipedia_api.py`:
   - Import cache functions from `cache.py`.
   - Update `get_forward_links()` to check cache first, return cached links if found, otherwise fetch from API, cache the result, then return.
   - Update `get_backward_links()` similarly.

**Tests:**

Create `tests/test_cache.py`:

```python
"""Step 10 tests — SQLite cache for Wikipedia links."""
import os
import sqlite3
import tempfile
from unittest.mock import patch

import pytest

import cache
import wikipedia_api


@pytest.fixture
def temp_db():
    """Use a temporary database file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        temp_path = f.name

    original_db = cache.DB_PATH
    cache.DB_PATH = temp_path
    cache.init_db()

    yield temp_path

    cache.DB_PATH = original_db
    if os.path.exists(temp_path):
        os.remove(temp_path)


class TestCacheInit:
    def test_init_creates_database(self, temp_db):
        """init_db should create the database file."""
        assert os.path.exists(temp_db)

    def test_init_creates_links_table(self, temp_db):
        """init_db should create the links table."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='links'"
        )
        result = cursor.fetchone()
        conn.close()
        assert result is not None

    def test_init_is_idempotent(self, temp_db):
        """Calling init_db multiple times should not raise errors."""
        cache.init_db()
        cache.init_db()
        # If we get here without exception, test passes


class TestCacheOperations:
    def test_cache_and_retrieve_links(self, temp_db):
        """cache_links followed by get_cached_links should return the same links."""
        links = {"Article A", "Article B", "Article C"}
        cache.cache_links("Test Article", links, "forward")

        result = cache.get_cached_links("Test Article", "forward")
        assert result == links

    def test_get_uncached_returns_none(self, temp_db):
        """get_cached_links should return None for uncached articles."""
        result = cache.get_cached_links("Nonexistent", "forward")
        assert result is None

    def test_forward_and_backward_cached_separately(self, temp_db):
        """Forward and backward links should be cached independently."""
        forward_links = {"Forward A", "Forward B"}
        backward_links = {"Backward A", "Backward B"}

        cache.cache_links("Test Article", forward_links, "forward")
        cache.cache_links("Test Article", backward_links, "backward")

        assert cache.get_cached_links("Test Article", "forward") == forward_links
        assert cache.get_cached_links("Test Article", "backward") == backward_links

    def test_clear_cache_removes_all_entries(self, temp_db):
        """clear_cache should remove all cached data."""
        cache.cache_links("Article 1", {"Link A"}, "forward")
        cache.cache_links("Article 2", {"Link B"}, "backward")

        cache.clear_cache()

        assert cache.get_cached_links("Article 1", "forward") is None
        assert cache.get_cached_links("Article 2", "backward") is None

    def test_empty_links_cached_correctly(self, temp_db):
        """Caching an empty set should be distinguishable from not cached."""
        cache.cache_links("Empty Article", set(), "forward")

        result = cache.get_cached_links("Empty Article", "forward")
        assert result == set()
        assert result is not None


class TestWikipediaApiCacheIntegration:
    @patch("wikipedia_api._get")
    def test_forward_links_uses_cache(self, mock_get, temp_db):
        """get_forward_links should use cache on second call."""
        mock_get.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "pageid": 123,
                        "title": "Test",
                        "links": [
                            {"ns": 0, "title": "Link A"},
                            {"ns": 0, "title": "Link B"},
                        ],
                    }
                }
            }
        }

        # First call should hit the API
        result1 = wikipedia_api.get_forward_links("Test")
        assert mock_get.call_count == 1

        # Second call should use cache
        result2 = wikipedia_api.get_forward_links("Test")
        assert mock_get.call_count == 1  # No additional API call

        assert result1 == result2 == {"Link A", "Link B"}

    @patch("wikipedia_api._get")
    def test_backward_links_uses_cache(self, mock_get, temp_db):
        """get_backward_links should use cache on second call."""
        mock_get.return_value = {
            "query": {
                "pages": {
                    "123": {
                        "pageid": 123,
                        "title": "Test",
                        "linkshere": [
                            {"ns": 0, "title": "Backlink A"},
                            {"ns": 0, "title": "Backlink B"},
                        ],
                    }
                }
            }
        }

        # First call should hit the API
        result1 = wikipedia_api.get_backward_links("Test")
        assert mock_get.call_count == 1

        # Second call should use cache
        result2 = wikipedia_api.get_backward_links("Test")
        assert mock_get.call_count == 1  # No additional API call

        assert result1 == result2 == {"Backlink A", "Backlink B"}


class TestCacheTableSchema:
    def test_links_table_has_correct_columns(self, temp_db):
        """The links table should have source, target, direction, and cached_at columns."""
        conn = sqlite3.connect(temp_db)
        cursor = conn.execute("PRAGMA table_info(links)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()

        assert "source" in columns
        assert "target" in columns
        assert "direction" in columns
        assert "cached_at" in columns
```

Run: `pytest tests/test_cache.py -v`

All 13 tests must pass.

**Acceptance criteria:**
- The `links_cache.db` file is created when the application first fetches links.
- Repeated searches for the same article reuse cached links (no additional API calls).
- The cache correctly separates forward and backward links.
- `pytest tests/test_cache.py -v` passes all 13 tests.
- `pytest -v` passes all tests across the entire test suite (previous tests still pass).
