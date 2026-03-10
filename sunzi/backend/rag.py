import os
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.path.join(os.path.dirname(__file__), "chroma_db")
EMBED_MODEL = "text-embedding-3-small"

_openai_client = None
_collection = None


def _get_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _openai_client


def get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection("art_of_war")
    return _collection


def query_rag(topic: str, stage: str, user_input: str, n_results: int = 5) -> list:
    """
    Returns list of dicts with keys: text, source, chapter, chapter_title.
    Builds query from topic + stage + user_input for contextually relevant retrieval.
    """
    query_string = f"{topic} {stage} {user_input}"
    client = _get_client()
    response = client.embeddings.create(model=EMBED_MODEL, input=[query_string])
    embedding = response.data[0].embedding

    collection = get_collection()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        where={"source": {"$in": ["sun_tzu", "commentary"]}}
    )

    chunks = []
    for i in range(len(results["documents"][0])):
        meta = results["metadatas"][0][i]
        chunks.append({
            "text": results["documents"][0][i],
            "source": meta["source"],
            "chapter": meta["chapter"],
            "chapter_title": meta["chapter_title"],
        })

    return chunks
