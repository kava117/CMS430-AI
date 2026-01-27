import pytest
from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture
def single_page_forward_response():
    """Canned Wikipedia API response for get_forward_links (single page, no continue)."""
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
def paginated_forward_response_page1():
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
def paginated_forward_response_page2():
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
    """Canned Wikipedia API response for get_backward_links (single page)."""
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
    return {"query": {"pages": {"123": {"pageid": 123, "title": "Python (programming language)"}}}}


@pytest.fixture
def article_missing_response():
    return {"query": {"pages": {"-1": {"title": "Nonexistent", "missing": ""}}}}
