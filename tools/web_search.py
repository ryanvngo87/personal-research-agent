import httpx
from app.config import BRAVE_API_KEY


def web_search(query: str, count: int = 5) -> list[dict]:
    if not BRAVE_API_KEY:
        return [{"error": "BRAVE_API_KEY not set"}]

    response = httpx.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"Accept": "application/json", "X-Subscription-Token": BRAVE_API_KEY},
        params={"q": query, "count": count},
        timeout=10,
    )
    response.raise_for_status()
    results = response.json().get("web", {}).get("results", [])
    return [
        {
            "title": r.get("title"),
            "url": r.get("url"),
            "snippet": r.get("description"),
            "source_type": "web",
        }
        for r in results
    ]


TOOL_SCHEMA = {
    "name": "web_search",
    "description": "Search the web using Brave Search. Use this for current information not found in personal notes.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
            "count": {"type": "integer", "description": "Number of results to return", "default": 5},
        },
        "required": ["query"],
    },
}
