import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from mcp_server.notes_tools import notes_search, notes_get
from mcp_server.github_tools import get_recent_activity, search_commits, search_repos

mcp = FastMCP("personal-research")


@mcp.tool()
def search_notes(query: str) -> list[dict]:
    """Search personal notes by keyword."""
    return notes_search(query)


@mcp.tool()
def get_note(note_id: str) -> dict:
    """Retrieve the full content of a note by its filename."""
    return notes_get(note_id)


@mcp.tool()
def github_recent_activity(username: str = "") -> list[dict]:
    """Get recent public GitHub activity for a user."""
    return get_recent_activity(username)


@mcp.tool()
def github_search_commits(query: str, username: str = "") -> list[dict]:
    """Search GitHub commits by keyword, optionally filtered to a user."""
    return search_commits(query, username)


@mcp.tool()
def github_search_repos(query: str, username: str = "") -> list[dict]:
    """Search GitHub repositories by keyword, optionally filtered to a user."""
    return search_repos(query, username)


if __name__ == "__main__":
    mcp.run()
