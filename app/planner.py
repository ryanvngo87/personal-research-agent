import json
import anthropic
from app.config import ANTHROPIC_API_KEY

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

PLANNER_PROMPT = """\
You are a research planning assistant. Given a user question, decompose it into
2–5 focused sub-queries that together cover the full answer. Return ONLY a JSON
array of strings, no explanation.

Example:
Question: "How do I build a research agent using MCP and Chroma?"
Response: ["What is MCP and how does it expose tools?", "How does Chroma store and retrieve vectors?", "How does an agent loop call tools?", "How are results from multiple sources synthesized?"]
"""


def decompose(question: str) -> list[str]:
    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=PLANNER_PROMPT,
        messages=[{"role": "user", "content": question}],
    )
    text = response.content[0].text.strip()
    return json.loads(text)
