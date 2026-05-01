"""
Ingest local notes from data/notes/ into Chroma.
Usage: python -m retrieval.ingest
"""
import os
import sys
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import NOTES_DIR
from retrieval.chunking import chunk_text
from retrieval.vector_store import add_chunks


def ingest_file(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        text = f.read()

    filename = os.path.basename(path)
    chunks = chunk_text(text)
    ids = [
        hashlib.md5(f"{filename}:{i}".encode()).hexdigest()
        for i in range(len(chunks))
    ]
    metadatas = [
        {"source": filename, "source_type": "note", "chunk_index": i}
        for i in range(len(chunks))
    ]
    add_chunks(chunks, metadatas, ids)
    return len(chunks)


def ingest_all() -> None:
    total = 0
    for fname in os.listdir(NOTES_DIR):
        if fname.endswith((".txt", ".md")):
            fpath = os.path.join(NOTES_DIR, fname)
            n = ingest_file(fpath)
            print(f"  {fname}: {n} chunks")
            total += n
    print(f"Ingested {total} chunks total.")


if __name__ == "__main__":
    ingest_all()
