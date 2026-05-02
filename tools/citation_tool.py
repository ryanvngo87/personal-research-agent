from datetime import datetime


def format_citation(source_type: str, title: str, url_or_id: str, snippet: str) -> dict:
    return {
        "source_type": source_type,
        "title": title,
        "url_or_id": url_or_id,
        "snippet": snippet[:300],
        "retrieved_at": datetime.utcnow().isoformat() + "Z",
    }


def _extract_citation(f: dict) -> dict:
    source_type = f.get("source_type", "note")

    if source_type == "github":
        title = f.get("repo") or f.get("name") or "GitHub"
        url_or_id = f.get("url", "")
        snippet = (
            f.get("payload_summary")
            or f.get("message")
            or f.get("description")
            or ""
        )
    elif source_type == "web":
        title = f.get("title", "Web")
        url_or_id = f.get("url", "")
        snippet = f.get("snippet", "")
    else:
        meta = f.get("metadata", {})
        title = meta.get("source", "Note")
        url_or_id = meta.get("source", "")
        snippet = f.get("content", "")

    return format_citation(source_type, title, url_or_id, snippet)


def citations_from_findings(findings: list[dict]) -> list[dict]:
    seen = set()
    citations = []
    for f in findings:
        c = _extract_citation(f)
        key = (c["source_type"], c["title"], c["url_or_id"])
        if key not in seen:
            seen.add(key)
            citations.append(c)
    return citations


TOOL_SCHEMA = {
    "name": "format_citations",
    "description": "Format a list of findings into structured citations for the final answer.",
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {"type": "object"},
                "description": "List of findings with content and metadata",
            }
        },
        "required": ["findings"],
    },
}
