from datetime import datetime


def format_citation(source_type: str, title: str, url_or_id: str, snippet: str) -> dict:
    return {
        "source_type": source_type,
        "title": title,
        "url_or_id": url_or_id,
        "snippet": snippet[:300],
        "retrieved_at": datetime.utcnow().isoformat() + "Z",
    }


def citations_from_findings(findings: list[dict]) -> list[dict]:
    citations = []
    for f in findings:
        meta = f.get("metadata", {})
        source_type = meta.get("source_type", "note")
        title = meta.get("source", f.get("url_or_id", "unknown"))
        url_or_id = f.get("url", meta.get("source", ""))
        snippet = f.get("content", f.get("snippet", ""))
        citations.append(format_citation(source_type, title, url_or_id, snippet))
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
