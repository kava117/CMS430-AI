import os
import sys
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingest import (
    strip_gutenberg_boilerplate,
    parse_sections,
    chunk_text,
)

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "art_of_war_giles.txt")


@pytest.fixture(scope="module")
def raw_text():
    return open(DATA_PATH, encoding="utf-8").read()


@pytest.fixture(scope="module")
def stripped_text(raw_text):
    return strip_gutenberg_boilerplate(raw_text)


@pytest.fixture(scope="module")
def sections(stripped_text):
    return parse_sections(stripped_text)


# --- strip_gutenberg_boilerplate ---

def test_strip_removes_gutenberg_from_start(stripped_text):
    assert "Project Gutenberg" not in stripped_text[:200]


def test_strip_preserves_content(stripped_text):
    assert "Sun Tzu" in stripped_text or "Sun Tzŭ" in stripped_text


def test_strip_returns_nonempty(stripped_text):
    assert len(stripped_text) > 5000


# --- parse_sections ---

def test_parse_sections_returns_list(sections):
    assert isinstance(sections, list)
    assert len(sections) > 0


def test_parse_sections_required_keys(sections):
    for s in sections:
        assert "text" in s
        assert "source" in s
        assert "chapter" in s
        assert "chapter_title" in s


def test_parse_sections_valid_source_values(sections):
    valid = {"sun_tzu", "commentary"}
    for s in sections:
        assert s["source"] in valid, f"Invalid source: {s['source']}"


def test_parse_sections_valid_chapter_range(sections):
    for s in sections:
        assert isinstance(s["chapter"], int)
        assert 1 <= s["chapter"] <= 13, f"Chapter out of range: {s['chapter']}"


def test_parse_sections_has_both_source_types(sections):
    sources = {s["source"] for s in sections}
    assert "sun_tzu" in sources
    assert "commentary" in sources


def test_parse_sections_covers_all_13_chapters(sections):
    chapters = {s["chapter"] for s in sections}
    assert chapters == set(range(1, 14)), f"Missing chapters: {set(range(1,14)) - chapters}"


# --- chunk_text ---

def test_chunk_text_word_count_range():
    # Generate a long enough text to produce multiple chunks
    text = "The general who wins a battle makes many calculations. " * 60
    chunks = chunk_text(text, chunk_size=175, overlap=25)
    for chunk in chunks:
        wc = len(chunk.split())
        assert 50 <= wc <= 300, f"Chunk word count out of range: {wc}"


def test_chunk_text_no_mid_sentence_splits():
    text = "All warfare is based on deception. He will win who knows when to fight. " * 40
    chunks = chunk_text(text, chunk_size=100, overlap=15)
    for chunk in chunks:
        stripped = chunk.strip()
        assert stripped[-1] in '.?!', f"Chunk does not end with sentence terminator: ...{stripped[-20:]}"


def test_chunk_text_overlap():
    text = "The supreme art of war is to subdue the enemy without fighting. Water shapes its course according to the nature of the ground. " * 30
    chunks = chunk_text(text, chunk_size=80, overlap=20)
    if len(chunks) >= 2:
        words_a = chunks[0].split()
        words_b = chunks[1].split()
        # Some words from end of chunk A should appear at start of chunk B
        tail_a = set(words_a[-30:])
        head_b = set(words_b[:30])
        assert len(tail_a & head_b) > 0, "No overlap detected between consecutive chunks"


def test_chunk_text_short_input():
    text = "All warfare is based on deception."
    chunks = chunk_text(text)
    assert len(chunks) == 1
    assert "deception" in chunks[0]


def test_chunk_text_empty_input():
    chunks = chunk_text("")
    assert chunks == []


# --- query_rag (requires ingest to have been run) ---

@pytest.fixture(scope="module")
def chroma_available():
    chroma_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
    return os.path.isdir(chroma_path)


def test_query_rag_returns_list(chroma_available):
    if not chroma_available:
        pytest.skip("ChromaDB not yet ingested — run python ingest.py first")
    from rag import query_rag
    results = query_rag("deception", "introduction", "All warfare is based on deception")
    assert isinstance(results, list)


def test_query_rag_returns_five_results(chroma_available):
    if not chroma_available:
        pytest.skip("ChromaDB not yet ingested")
    from rag import query_rag
    results = query_rag("deception", "introduction", "All warfare is based on deception")
    assert len(results) == 5


def test_query_rag_result_keys(chroma_available):
    if not chroma_available:
        pytest.skip("ChromaDB not yet ingested")
    from rag import query_rag
    results = query_rag("self_knowledge", "examination", "know yourself know your enemy")
    for r in results:
        assert "text" in r
        assert "source" in r
        assert "chapter" in r
        assert "chapter_title" in r
        assert isinstance(r["text"], str) and len(r["text"]) > 0


def test_query_rag_different_queries_return_different_results(chroma_available):
    if not chroma_available:
        pytest.skip("ChromaDB not yet ingested")
    from rag import query_rag
    results_a = query_rag("deception", "introduction", "All warfare is based on deception")
    results_b = query_rag("victory", "challenge", "subdue the enemy without fighting")
    texts_a = {r["text"] for r in results_a}
    texts_b = {r["text"] for r in results_b}
    assert texts_a != texts_b, "Different queries returned identical results"
