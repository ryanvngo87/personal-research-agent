from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL

_model: SentenceTransformer | None = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed(texts: list[str]) -> list[list[float]]:
    return get_model().encode(texts, show_progress_bar=False).tolist()
