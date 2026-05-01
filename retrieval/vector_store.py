import chromadb
from app.config import CHROMA_DIR, CHROMA_COLLECTION, TOP_K
from retrieval.embeddings import embed


def _collection():
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    return client.get_or_create_collection(CHROMA_COLLECTION)


def add_chunks(chunks: list[str], metadatas: list[dict], ids: list[str]) -> None:
    col = _collection()
    col.add(
        documents=chunks,
        embeddings=embed(chunks),
        metadatas=metadatas,
        ids=ids,
    )


def search(query: str, top_k: int = TOP_K, where: dict | None = None) -> list[dict]:
    col = _collection()
    kwargs = {"query_embeddings": embed([query]), "n_results": top_k}
    if where:
        kwargs["where"] = where
    results = col.query(**kwargs)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]
    return [
        {"content": doc, "metadata": meta, "score": 1 - dist}
        for doc, meta, dist in zip(docs, metas, distances)
    ]
