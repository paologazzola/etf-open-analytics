"""
Embedding + Vector Store utilities (Chroma + Sentence Transformers), CPU-only.

Public API used elsewhere:
- get_vector_store()
- embed_text(text) -> List[float]
- embed_texts(texts) -> List[List[float]]
- index_docs(docs)
- retrieve(query, k)
"""

from __future__ import annotations
import os
from typing import List, Dict, Tuple

import chromadb
from chromadb.config import Settings

# Optional fallback embedding if SentenceTransformer/torch fail
from chromadb.utils import embedding_functions

# Env config
RAG_COLLECTION = os.getenv("RAG_COLLECTION", "etf_docs")
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "intfloat/e5-small-v2")

# Lazy singletons
try:
    from sentence_transformers import SentenceTransformer
    _emb_model: "SentenceTransformer | None" = None
    _st_available = True
except Exception as e:
    print(f"[WARN] sentence-transformers unavailable ({e}); will use fallback embeddings.")
    SentenceTransformer = None  # type: ignore
    _emb_model = None
    _st_available = False

_chroma_client = None
_collection = None
_fallback_ef = None  # Chroma's DefaultEmbeddingFunction


def _get_emb_model():
    """
    Singleton for the embedding model, forced on CPU.
    If SentenceTransformer fails (torch DLL issues etc.), fallback to Chroma EF.
    """
    global _emb_model, _fallback_ef
    if _emb_model is None and _st_available:
        try:
            # Force CPU device to avoid CUDA/DLL issues on Windows
            _emb_model = SentenceTransformer(EMBEDDING_MODEL_NAME, device="cpu")  # type: ignore
            print(f"[INFO] Loaded SentenceTransformer on CPU: {EMBEDDING_MODEL_NAME}")
        except Exception as e:
            print(f"[ERROR] Failed to load SentenceTransformer on CPU: {e}")
            _emb_model = None

    if _emb_model is None:
        if _fallback_ef is None:
            _fallback_ef = embedding_functions.DefaultEmbeddingFunction()
            print("[WARN] Using Chroma DefaultEmbeddingFunction as fallback.")
    return _emb_model or _fallback_ef


def _get_chroma_client():
    """Singleton for the Chroma client with persistence enabled."""
    global _chroma_client
    if _chroma_client is None:
        try:
            from chromadb import PersistentClient  # type: ignore
            _chroma_client = PersistentClient(path=CHROMA_PERSIST_DIR)
        except Exception:
            _chroma_client = chromadb.Client(
                Settings(is_persistent=True, persist_directory=CHROMA_PERSIST_DIR)
            )
    return _chroma_client


def get_vector_store():
    """Return the Chroma collection used by RAG (creating it if missing)."""
    global _collection
    if _collection is not None:
        return _collection

    client = _get_chroma_client()
    try:
        _collection = client.get_collection(RAG_COLLECTION)
    except Exception:
        _collection = client.get_or_create_collection(RAG_COLLECTION)
    return _collection


# ----------------------------
# Public helpers (embeddings)
# ----------------------------
def embed_text(text: str) -> List[float]:
    """Return a single embedding vector for the given text."""
    model = _get_emb_model()
    if hasattr(model, "encode"):
        vec = model.encode([text], normalize_embeddings=True)  # SentenceTransformer
        return vec[0].tolist()
    # Fallback EF returns python list already
    return model(text)  # type: ignore


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Return embedding vectors for a list of texts."""
    model = _get_emb_model()
    if hasattr(model, "encode"):
        vecs = model.encode(texts, normalize_embeddings=True)  # SentenceTransformer
        return vecs.tolist()
    return [model(x) for x in texts]  # type: ignore


# ----------------------------
# Indexing & Retrieval
# ----------------------------
def index_docs(docs: List[Dict]):
    """
    Index documents into Chroma with safe re-ingest:
    - delete existing IDs if present
    - then add with fresh embeddings

    Each doc must be a dict:
      {
        "id": str,   # unique id for the chunk
        "text": str, # chunk text
        "meta": dict # e.g., {"path": "README.md"}
      }
    """
    if not docs:
        return

    coll = get_vector_store()
    ids = [d["id"] for d in docs]
    texts = [d["text"] for d in docs]
    metas = [d.get("meta", {}) for d in docs]

    # Best-effort delete (ignore if not present)
    try:
        coll.delete(ids=ids)
    except Exception:
        pass

    embeddings = embed_texts(texts)
    coll.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metas)


def retrieve(query: str, k: int = 5) -> List[Tuple[str, Dict]]:
    """
    Convenience function: return [(document_text, metadata), ...] for a query.
    (rag.py typically uses get_vector_store() + embed_text()).
    """
    coll = get_vector_store()
    qv = embed_text(query)
    res = coll.query(query_embeddings=[qv], n_results=k)
    docs = res.get("documents", [[]])[0] if res.get("documents") else []
    metas = res.get("metadatas", [[]])[0] if res.get("metadatas") else []
    return list(zip(docs, metas))
