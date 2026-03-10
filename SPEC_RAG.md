# SPEC_RAG.md — Retrieval-Augmented Generation

---

## Overview

The RAG system retrieves relevant passages from Sun Tzu's *Art of War* (Giles translation) to provide the generator LLM with grounded textual context. It uses ChromaDB as the vector store and sentence-transformers for embedding.

---

## Source Text

**Primary source:** *The Art of War* by Sun Tzu, translated by Lionel Giles (1910)
**Acquisition:** Download plain text from Project Gutenberg (https://www.gutenberg.org/ebooks/17405)
**Save to:** `backend/data/art_of_war_giles.txt`

The Giles translation includes both Sun Tzu's original text and Giles's scholarly commentary. Both should be included in the corpus but tagged separately.

---

## Text Preprocessing

Before chunking, preprocess the raw text:

1. Strip Project Gutenberg header and footer boilerplate
2. Identify and separate Sun Tzu's original text from Giles's commentary
   - Sun Tzu's text appears as the main numbered passages
   - Commentary appears as indented or bracketed sections following each passage
3. Tag each section with metadata:
   - `source`: `"sun_tzu"` or `"commentary"`
   - `chapter`: integer 1-13
   - `chapter_title`: string (e.g., "Laying Plans", "Attack by Stratagem")

---

## Chunking Strategy

**Chunk size:** 150-200 words
**Overlap:** 20-30 words between adjacent chunks

Use a sliding window approach. Do not split mid-sentence. If a chunk boundary falls mid-sentence, extend to the end of the sentence even if slightly over the word limit.

**Implementation approach:**

```python
def chunk_text(text, chunk_size=175, overlap=25):
    # Split into sentences first
    # Build chunks by accumulating sentences until chunk_size is reached
    # Store last `overlap` words to prepend to next chunk
    # Return list of (chunk_text, start_index) tuples
```

Each chunk should carry forward the metadata of its source section (source, chapter, chapter_title).

**Why this chunk size:** Sun Tzu's original passages are aphoristic and short. A 150-200 word window captures one to three related aphorisms plus enough surrounding context for meaningful embedding. Giles's commentary paragraphs fit naturally in this range.

---

## Embedding

**Library:** `sentence-transformers`
**Model:** `all-MiniLM-L6-v2` (fast, good quality, 384-dimensional embeddings)

```python
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("your text here")  # returns numpy array of 384 floats
```

Embed all chunks at ingest time. Store embeddings in ChromaDB alongside chunk text and metadata.

---

## ChromaDB Setup

**Library:** `chromadb`
**Mode:** Local persistent storage (no server required)

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="art_of_war",
    metadata={"hnsw:space": "cosine"}  # cosine similarity for text
)
```

**Adding documents:**

```python
collection.add(
    documents=["chunk text here", ...],
    embeddings=[[0.1, 0.2, ...], ...],   # pre-computed embeddings
    metadatas=[{"source": "sun_tzu", "chapter": 1, "chapter_title": "Laying Plans"}, ...],
    ids=["chunk_001", "chunk_002", ...]   # unique string IDs
)
```

---

## Ingest Script

`backend/ingest.py` is a one-time setup script. It should:

1. Load and preprocess `art_of_war_giles.txt`
2. Chunk the text with the strategy above
3. Embed all chunks using sentence-transformers
4. Load all chunks, embeddings, and metadata into ChromaDB
5. Print a summary: total chunks ingested, breakdown by source type

Run once before starting the Flask server:
```bash
python ingest.py
```

The ChromaDB collection persists to disk at `./chroma_db/` and does not need to be rebuilt on each server start.

---

## Query Flow

At generation time, `rag.py` exposes a single query function:

```python
def query_rag(topic: str, stage: str, user_input: str, n_results: int = 5) -> list[dict]:
    """
    Returns list of dicts with keys: text, source, chapter, chapter_title
    """
```

**Query construction:** Combine the current topic label, stage label, and user input into a single query string. This ensures retrieved chunks are relevant to both the conversational context and the user's specific response.

Example:
```python
query_string = f"{topic} {stage} {user_input}"
# e.g. "deception introduction All warfare is based on deception"
```

**Retrieval:**

```python
results = collection.query(
    query_embeddings=[model.encode(query_string).tolist()],
    n_results=n_results,
    where={"source": {"$in": ["sun_tzu", "commentary"]}}  # retrieve both
)
```

**Return format:** Return top 5 results as a list of dicts. Include both sun_tzu and commentary chunks. The generator prompt will handle them differently based on their source tag.

---

## Metadata Filtering

When querying, you may optionally filter by chapter to constrain retrieval to topic-relevant chapters:

**Topic → Chapter mapping:**

| Topic | Relevant Chapters |
|---|---|
| deception | 1 (Laying Plans), 13 (Use of Spies) |
| self_knowledge | 3 (Attack by Stratagem), 7 (Maneuvering) |
| adaptability | 6 (Weak Points and Strong), 8 (Variation of Tactics) |
| victory | 2 (Waging War), 3 (Attack by Stratagem) |

This filtering is optional — unfiltered retrieval is acceptable for early implementation. Add filtering as a refinement if retrieval quality is poor.

---

## Dependencies

```
chromadb
sentence-transformers
torch  # required by sentence-transformers
```

Add to `requirements.txt`.