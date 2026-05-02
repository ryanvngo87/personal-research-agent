from mcp_server.github_tools import get_recent_activity, search_commits, search_repos
from app.config import GITHUB_USERNAME


def github_search(query: str, search_type: str = "commits") -> list[dict]:
    if search_type == "activity":
        return get_recent_activity(GITHUB_USERNAME)
    if search_type == "repos":
        return search_repos(query, GITHUB_USERNAME)
    return search_commits(query, GITHUB_USERNAME)


TOOL_SCHEMA = {
    "name": "github_search",
    "description": (
        "Search GitHub for commits, repos, or recent activity. "
        "Use this when the question involves code, projects, or development history."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "search_type": {
                "type": "string",
                "enum": ["commits", "repos", "activity"],
                "description": "What to search: commits, repos, or recent activity",
                "default": "commits",
            },
        },
        "required": ["query"],
    },
}
