"""SQLite cache for Wikipedia link data."""
import sqlite3
from pathlib import Path

DB_PATH = "links_cache.db"


def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS links (
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            direction TEXT NOT NULL,
            cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (source, target, direction)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_source_direction ON links(source, direction)
    """)
    conn.commit()
    conn.close()


def get_cached_links(title: str, direction: str) -> set[str] | None:
    """
    Retrieve cached links for an article.

    Args:
        title: The Wikipedia article title.
        direction: Either 'forward' or 'backward'.

    Returns:
        A set of linked article titles if cached, or None if not cached.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT target FROM links WHERE source = ? AND direction = ?",
        (title, direction),
    )
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    # Filter out the empty marker used for empty sets
    links = {row[0] for row in rows if row[0]}
    return links


def cache_links(title: str, links: set[str], direction: str):
    """
    Store links in the cache.

    Args:
        title: The Wikipedia article title (source).
        links: Set of linked article titles.
        direction: Either 'forward' or 'backward'.
    """
    conn = sqlite3.connect(DB_PATH)

    # Delete any existing entries for this source+direction
    conn.execute(
        "DELETE FROM links WHERE source = ? AND direction = ?",
        (title, direction),
    )

    if links:
        # Insert all new links
        conn.executemany(
            "INSERT INTO links (source, target, direction) VALUES (?, ?, ?)",
            [(title, target, direction) for target in links],
        )
    else:
        # For empty sets, insert a marker row with empty target
        conn.execute(
            "INSERT INTO links (source, target, direction) VALUES (?, ?, ?)",
            (title, "", direction),
        )

    conn.commit()
    conn.close()


def clear_cache():
    """Delete all cached data."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM links")
    conn.commit()
    conn.close()
