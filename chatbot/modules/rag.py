"""
RAG (Retrieval-Augmented Generation) module.

This module connects the vector store (Chroma by default) with the local LLM.
It retrieves the most semantically relevant text chunks for a given query and
uses them as context to craft an informed and grounded answer.

Workflow:
1. Embed the user query using the same SentenceTransformer as used for ingestion.
2. Retrieve top-k similar chunks from Chroma.
3. Build a context string with those chunks (sources included).
4. Send a concise prompt to the LLM backend (`modules.llm`).
5. Return the generated answer and the sources metadata.
"""

from __future__ import annotations
from typing import List, Tuple, Dict
from .embed_store import get_vector_store, embed_text
from .llm import chat_completion


def build_prompt(query: str, context_chunks: List[str]) -> str:
    """Compose a minimal prompt with context and question."""
    context = "\n\n".join(context_chunks)
    return (
        "You are a precise assistant specialized in ETF analytics.\n"
        "Answer the user question based only on the context below.\n"
        "If the context does not contain the answer, say 'I don't have this information.'\n\n"
        f"### Context ###\n{context}\n\n"
        f"### Question ###\n{query}\n\n"
        "Answer:"
    )


def answer_with_rag(query: str, top_k: int = 4) -> Tuple[str, List[Dict]]:
    """Run the full retrieval + generation pipeline.

    Args:
        query: user question text.
        top_k: number of top documents to retrieve.

    Returns:
        (answer_text, sources)
    """
    if not query or not query.strip():
        return "Empty query.", []

    # Step 1: embed query and get Chroma collection
    query_emb = embed_text(query)
    vs = get_vector_store()

    # Step 2: perform similarity search
    try:
        results = vs.query(query_embeddings=[query_emb], n_results=top_k)
    except Exception as e:
        return f"Vector store query failed: {e}", []

    # Step 3: extract chunks and metadata
    docs = results.get("documents", [[]])[0] if results.get("documents") else []
    metas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []
    context_chunks = docs[:top_k]
    sources = [{"path": m.get("path", "unknown")} for m in metas[:top_k]]

    # Step 4: build prompt and call LLM
    prompt = build_prompt(query, context_chunks)
    try:
        answer = chat_completion(prompt)
    except Exception as e:
        answer = f"LLM error: {e}"

    return answer, sources


# Optional: test mode
if __name__ == "__main__":
    sample_q = "Explain how the ETF risk model is trained."
    ans, srcs = answer_with_rag(sample_q)
    print("ANSWER:", ans)
    print("SOURCES:", srcs)
