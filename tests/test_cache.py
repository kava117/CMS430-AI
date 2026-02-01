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
