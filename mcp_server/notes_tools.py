import os
from app.config import NOTES_DIR


def notes_search(query: str) -> list[dict]:
    query_lower = query.lower()
    matches = []
    for fname in os.listdir(NOTES_DIR):
        if not fname.endswith((".txt", ".md")):
            continue
        fpath = os.path.join(NOTES_DIR, fname)
        with open(fpath, encoding="utf-8") as f:
            content = f.read()
        if query_lower in content.lower():
            snippet = _extract_snippet(content, query_lower)
            matches.append({"note_id": fname, "snippet": snippet, "source": fname})
    return matches


def notes_get(note_id: str) -> dict:
    fpath = os.path.join(NOTES_DIR, note_id)
    if not os.path.exists(fpath):
        return {"error": f"Note '{note_id}' not found"}
    with open(fpath, encoding="utf-8") as f:
        content = f.read()
    return {"note_id": note_id, "content": content}


def _extract_snippet(text: str, query: str, context: int = 200) -> str:
    idx = text.lower().find(query)
    if idx == -1:
        return text[:context]
    start = max(0, idx - context // 2)
    end = min(len(text), idx + context // 2)
    return text[start:end]
