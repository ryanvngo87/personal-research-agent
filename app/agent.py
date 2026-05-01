import json
import anthropic
from app.config import ANTHROPIC_API_KEY
from tools.chroma_search import chroma_search, TOOL_SCHEMA as CHROMA_SCHEMA

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TOOLS = [CHROMA_SCHEMA]

TOOL_HANDLERS = {
    "chroma_search": lambda inp: chroma_search(inp["query"], inp.get("top_k", 5)),
}

SYSTEM_PROMPT = """\
You are a research assistant. For each sub-query you receive, use the available
tools to gather relevant information from the user's personal notes. Call tools
as needed, then return a JSON object with keys:
  "sub_query": the original sub-query
  "findings": a list of {content, source} objects from tool results
  "summary": a brief synthesis of what you found
"""


def run_sub_query(sub_query: str) -> dict:
    messages = [{"role": "user", "content": sub_query}]

    while True:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Collect any tool calls and execute them
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = TOOL_HANDLERS[block.name](block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        if tool_results:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            continue

        # No more tool calls — extract final text
        final_text = next(
            (b.text for b in response.content if hasattr(b, "text")), "{}"
        )
        try:
            return json.loads(final_text)
        except json.JSONDecodeError:
            return {"sub_query": sub_query, "findings": [], "summary": final_text}


def run_agent(sub_queries: list[str]) -> list[dict]:
    return [run_sub_query(q) for q in sub_queries]
