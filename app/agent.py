import json
import anthropic
from app.config import ANTHROPIC_API_KEY
from tools.chroma_search import chroma_search, TOOL_SCHEMA as CHROMA_SCHEMA
from tools.web_search import web_search, TOOL_SCHEMA as WEB_SCHEMA

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

TOOLS = [CHROMA_SCHEMA, WEB_SCHEMA]

TOOL_HANDLERS = {
    "chroma_search": lambda inp: chroma_search(inp["query"], inp.get("top_k", 5)),
    "web_search": lambda inp: web_search(inp["query"], inp.get("count", 5)),
}

SYSTEM_PROMPT = """\
You are a research assistant. For each sub-query you receive, use the available
tools to gather relevant information. Use chroma_search for personal notes and
web_search for current or general information. Call tools as needed, then return
a JSON object with keys:
  "sub_query": the original sub-query
  "findings": a list of {content, source} objects from tool results
  "summary": a brief synthesis of what you found
"""


def run_sub_query(sub_query: str) -> dict:
    messages = [{"role": "user", "content": sub_query}]
    tools_called = []
    raw_findings = []

    while True:
        response = _client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = TOOL_HANDLERS[block.name](block.input)
                tools_called.append(block.name)
                # Attach source_type to each raw result for citations/scoring
                if isinstance(result, list):
                    for item in result:
                        if isinstance(item, dict):
                            item.setdefault("source_type", "web" if block.name == "web_search" else "note")
                            raw_findings.append(item)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })

        if tool_results:
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            continue

        final_text = next(
            (b.text for b in response.content if hasattr(b, "text")), "{}"
        )
        try:
            parsed = json.loads(final_text)
        except json.JSONDecodeError:
            parsed = {"sub_query": sub_query, "findings": [], "summary": final_text}

        parsed["tools_called"] = tools_called
        parsed["raw_findings"] = raw_findings
        return parsed


def run_agent(sub_queries: list[str]) -> list[dict]:
    return [run_sub_query(q) for q in sub_queries]
