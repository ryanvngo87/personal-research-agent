from retrieval.vector_store import search


def chroma_search(query: str, top_k: int = 5) -> list[dict]:
    return search(query, top_k=top_k)


TOOL_SCHEMA = {
    "name": "chroma_search",
    "description": "Search personal notes stored in Chroma using semantic similarity.",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
            "top_k": {"type": "integer", "description": "Number of results to return", "default": 5},
        },
        "required": ["query"],
    },
}
