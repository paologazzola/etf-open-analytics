"""
Index selected repo docs/notes into the vector store (Chroma by default).

Run:
    python -m modules.ingest
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Iterable
from .embed_store import index_docs

SUPPORTED_EXT = (".md", ".txt", ".pdf")


def _rel(doc: Path, root: Path) -> str:
    """Return a stable forward-slash relative path (cross-OS)."""
    return str(doc.relative_to(root)).replace("\\", "/")


def load_text_files(base_dir: Path) -> List[Dict]:
    """Load Markdown, text, and PDF files recursively from base_dir.

    Returns list of {"id": str, "text": str, "meta": {"path": str}}.
    """
    items: List[Dict] = []
    for path in base_dir.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED_EXT:
            continue

        rel = _rel(path, base_dir)
        try:
            if path.suffix.lower() == ".pdf":
                reader = PdfReader(str(path))
                text = "\n".join([page.extract_text() or "" for page in reader.pages])
            else:
                text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            print(f"[WARN] Skipping {path}: {e}")
            continue

        if not text.strip():
            continue

        items.append({"id": rel, "text": text, "meta": {"path": rel}})

    return items



def chunk(text: str, size: int = 1600, overlap: int = 200) -> Iterable[str]:
    """Naive char-based chunking suitable for CPU-only pipelines."""
    if not text:
        return []
    i, n = 0, len(text)
    while i < n:
        yield text[i : i + size]
        i += max(1, size - overlap)


def main() -> None:
    # repo_root: modules/ -> chatbot/ -> repo_root
    repo_root = Path(__file__).resolve().parents[2]
    docs_to_index: List[Dict] = []

    # 1) Explicit candidates (root README, evaluator README, chatbot README)
    candidates = [
        repo_root / "README.md",
        repo_root / "portfolio_evaluator" / "README.md",
        repo_root / "chatbot" / "README.md",
    ]

    for c in candidates:
        if not c.exists():
            continue
        try:
            text = c.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rel_path = _rel(c, repo_root)  # e.g. "README.md" or "chatbot/README.md"
        for j, part in enumerate(chunk(text)):
            docs_to_index.append({
                "id": f"{rel_path}:{j}",   # <-- includes relative path + chunk idx
                "text": part,
                "meta": {"path": rel_path},
            })

    # 2) Optional docs folder
    docs_dir = repo_root / "docs"
    if docs_dir.exists():
        for f in load_text_files(docs_dir):
            rel_path = f["meta"]["path"]  # already relative to docs_dir; make it relative to repo
            # Rebuild full relative path under docs/
            rel_full = f"docs/{rel_path}".replace("\\", "/")
            for j, part in enumerate(chunk(f["text"])):
                docs_to_index.append({
                    "id": f"{rel_full}:{j}",
                    "text": part,
                    "meta": {"path": rel_full},
                })

    # --- client-side de-dup for safety (skip duplicates in the same batch)
    seen = set()
    deduped: List[Dict] = []
    for d in docs_to_index:
        if d["id"] in seen:
            continue
        seen.add(d["id"])
        deduped.append(d)

    # (Optional) Debug: print the first 20 IDs to verify uniqueness
    print("Sample IDs:", [d["id"] for d in deduped[:20]])

    # Index
    index_docs(deduped)
    print(f"Indexed {len(deduped)} chunks from {repo_root}.")


if __name__ == "__main__":
    main()
