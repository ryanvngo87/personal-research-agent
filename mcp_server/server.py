import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mcp.server.fastmcp import FastMCP
from mcp_server.notes_tools import notes_search, notes_get

mcp = FastMCP("personal-notes")


@mcp.tool()
def search_notes(query: str) -> list[dict]:
    """Search personal notes by keyword."""
    return notes_search(query)


@mcp.tool()
def get_note(note_id: str) -> dict:
    """Retrieve the full content of a note by its filename."""
    return notes_get(note_id)


if __name__ == "__main__":
    mcp.run()
