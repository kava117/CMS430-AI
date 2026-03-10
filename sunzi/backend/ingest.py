"""
One-time ingest script: chunk, embed, and load Art of War into ChromaDB.
Run once before starting the Flask server: python ingest.py
"""

import os
import re
import time
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "art_of_war_giles.txt")
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")

CHAPTER_TITLES = {
    1: "Laying Plans",
    2: "Waging War",
    3: "Attack by Stratagem",
    4: "Tactical Dispositions",
    5: "Energy",
    6: "Weak Points and Strong",
    7: "Maneuvering",
    8: "Variation of Tactics",
    9: "The Army on the March",
    10: "Terrain",
    11: "The Nine Situations",
    12: "The Attack by Fire",
    13: "The Use of Spies",
}


def strip_gutenberg_boilerplate(text: str) -> str:
    """Remove Project Gutenberg header boilerplate up to the start marker."""
    start_marker = "*** START OF THE PROJECT GUTENBERG EBOOK"
    idx = text.find(start_marker)
    if idx != -1:
        # Skip to end of that line
        idx = text.index("\n", idx) + 1
        text = text[idx:]
    return text.strip()


def parse_sections(text: str) -> list:
    """
    Split text into sections tagged with source, chapter, chapter_title.
    Chapters are found by the pattern 'Chapter N. TITLE' (all caps).
    Within each chapter, numbered passages are sun_tzu, bracketed content is commentary.
    Returns list of dicts: {text, source, chapter, chapter_title}
    """
    # Match chapter headings like "Chapter I. LAYING PLANS" or "Chapter XIII. THE USE OF SPIES"
    chapter_pattern = re.compile(
        r'^Chapter\s+(XIII|XII|XI|IX|VIII|VII|VI|IV|III|II|X|V|I)\.\s+([A-Z][A-Z\s,]+)',
        re.MULTILINE
    )

    # Convert Roman numerals to int
    roman_map = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13
    }

    matches = list(chapter_pattern.finditer(text))
    sections = []

    for i, match in enumerate(matches):
        roman = match.group(1).strip()
        chapter_num = roman_map.get(roman)
        if chapter_num is None:
            continue

        chapter_title = CHAPTER_TITLES.get(chapter_num, match.group(2).strip().title())
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chapter_text = text[start:end].strip()

        # Split chapter into sun_tzu passages and commentary blocks
        # Sun Tzu passages: lines starting with a number (e.g., "1. Sun Tzŭ said:")
        # Commentary: text in [brackets] or paragraph blocks between numbered passages
        _extract_chapter_sections(chapter_text, chapter_num, chapter_title, sections)

    return sections


def _extract_chapter_sections(chapter_text: str, chapter_num: int, chapter_title: str, sections: list):
    """
    Within a chapter, identify sun_tzu numbered passages vs commentary blocks.
    Appends dicts to sections list.
    """
    # Split on numbered passage markers: lines like "1." "12." "5, 6."
    passage_pattern = re.compile(r'\n\s*(\d+(?:,\s*\d+)*)\.\s+')
    parts = passage_pattern.split(chapter_text)

    # parts alternates: [pre-first, num, text, num, text, ...]
    # First element is any intro text before the first numbered passage
    if parts[0].strip():
        _add_section(parts[0].strip(), "commentary", chapter_num, chapter_title, sections)

    i = 1
    while i < len(parts) - 1:
        passage_text = parts[i + 1].strip()
        if passage_text:
            # Separate inline commentary [in brackets] from sun_tzu text
            sun_tzu_text, commentary_text = _split_passage_and_commentary(passage_text)
            if sun_tzu_text:
                _add_section(sun_tzu_text, "sun_tzu", chapter_num, chapter_title, sections)
            if commentary_text:
                _add_section(commentary_text, "commentary", chapter_num, chapter_title, sections)
        i += 2


def _split_passage_and_commentary(text: str) -> tuple:
    """
    Split a passage block into (sun_tzu_text, commentary_text).
    Commentary is text inside [...] brackets or paragraph blocks that follow
    the main passage and consist entirely of bracket content.
    """
    # Extract all [...] blocks
    bracket_pattern = re.compile(r'\[([^\[\]]+)\]', re.DOTALL)
    commentary_parts = []

    def replace_bracket(m):
        commentary_parts.append(m.group(1).strip())
        return ''

    sun_tzu_text = bracket_pattern.sub(replace_bracket, text).strip()
    commentary_text = '\n\n'.join(commentary_parts).strip()

    return sun_tzu_text, commentary_text


def _add_section(text: str, source: str, chapter: int, chapter_title: str, sections: list):
    text = text.strip()
    if len(text) > 20:  # ignore trivially short fragments
        sections.append({
            "text": text,
            "source": source,
            "chapter": chapter,
            "chapter_title": chapter_title,
        })


def chunk_text(text: str, chunk_size: int = 175, overlap: int = 25) -> list:
    """
    Sliding window chunker. Splits text into sentences, then accumulates
    sentences into chunks of ~chunk_size words. Adjacent chunks share
    ~overlap words. Returns list of chunk strings.
    """
    # Split into sentences on . ? ! followed by whitespace or end
    sentence_pattern = re.compile(r'(?<=[.?!])\s+')
    sentences = sentence_pattern.split(text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    chunks = []
    current_sentences = []
    current_word_count = 0

    for sentence in sentences:
        word_count = len(sentence.split())
        current_sentences.append(sentence)
        current_word_count += word_count

        if current_word_count >= chunk_size:
            chunk = ' '.join(current_sentences)
            chunks.append(chunk)

            # Keep last `overlap` words worth of sentences for next chunk
            overlap_sentences = []
            overlap_count = 0
            for s in reversed(current_sentences):
                wc = len(s.split())
                if overlap_count + wc <= overlap:
                    overlap_sentences.insert(0, s)
                    overlap_count += wc
                else:
                    break
            current_sentences = overlap_sentences
            current_word_count = overlap_count

    # Add remaining text as final chunk
    if current_sentences:
        chunk = ' '.join(current_sentences)
        if chunk not in chunks:
            chunks.append(chunk)

    return chunks


EMBED_MODEL = "text-embedding-3-small"
EMBED_BATCH = 100  # OpenAI allows up to 2048 per call; 100 is safe


def _embed_texts_openai(texts: list) -> list:
    """Embed a list of texts using OpenAI's embedding API. Returns list of float lists."""
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    all_embeddings = []
    for i in range(0, len(texts), EMBED_BATCH):
        batch = texts[i:i + EMBED_BATCH]
        print(f"  Embedding batch {i // EMBED_BATCH + 1}/{(len(texts) + EMBED_BATCH - 1) // EMBED_BATCH} ({len(batch)} chunks)...")
        response = openai_client.embeddings.create(model=EMBED_MODEL, input=batch)
        for item in response.data:
            all_embeddings.append(item.embedding)
        time.sleep(0.2)  # stay well within rate limits
    return all_embeddings


def run_ingest():
    print("Loading source text...")
    raw = open(DATA_PATH, encoding='utf-8').read()
    text = strip_gutenberg_boilerplate(raw)
    print(f"  Text length after stripping: {len(text):,} chars")

    print("Parsing sections...")
    sections = parse_sections(text)
    print(f"  Sections found: {len(sections)}")

    print("Chunking sections...")
    all_chunks = []
    for section in sections:
        chunks = chunk_text(section["text"])
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "source": section["source"],
                "chapter": section["chapter"],
                "chapter_title": section["chapter_title"],
            })

    sun_tzu_count = sum(1 for c in all_chunks if c["source"] == "sun_tzu")
    commentary_count = sum(1 for c in all_chunks if c["source"] == "commentary")
    print(f"  Total chunks: {len(all_chunks)} ({sun_tzu_count} sun_tzu, {commentary_count} commentary)")

    texts = [c["text"] for c in all_chunks]

    print(f"Embedding {len(texts)} chunks via OpenAI text-embedding-3-small...")
    embeddings = _embed_texts_openai(texts)

    print("Connecting to ChromaDB...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    # Delete existing collection if present to allow re-ingest
    try:
        client.delete_collection("art_of_war")
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name="art_of_war",
        metadata={"hnsw:space": "cosine"}
    )

    print("Inserting into ChromaDB...")
    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=[{"source": c["source"], "chapter": c["chapter"], "chapter_title": c["chapter_title"]} for c in all_chunks],
        ids=[f"chunk_{i:04d}" for i in range(len(all_chunks))]
    )

    print(f"\nIngest complete.")
    print(f"  Total chunks ingested: {len(all_chunks)}")
    print(f"  Sun Tzu passages:      {sun_tzu_count}")
    print(f"  Commentary chunks:     {commentary_count}")


if __name__ == "__main__":
    run_ingest()
