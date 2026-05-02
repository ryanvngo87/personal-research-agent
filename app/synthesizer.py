import anthropic
from app.config import ANTHROPIC_API_KEY
from tools.citation_tool import citations_from_findings

_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYNTH_PROMPT = """\
You are a research synthesizer. Given a user question and a set of research
findings from multiple sources, produce a final answer with this structure:

**Answer**
<direct response to the question>

**Supporting Detail**
<explanation drawing on the findings>

**Follow-up Questions**
- <optional follow-up 1>
- <optional follow-up 2>

Be concise. Do not fabricate information beyond what the findings support.
"""


def synthesize(question: str, agent_results: list[dict]) -> dict:
    all_findings = []
    for r in agent_results:
        all_findings.extend(r.get("raw_findings", []))

    summaries = "\n\n".join(
        f"Sub-query: {r.get('sub_query', '')}\nSummary: {r.get('summary', '')}"
        for r in agent_results
    )

    response = _client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYNTH_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Question: {question}\n\nResearch findings:\n{summaries}",
            }
        ],
    )

    answer_text = response.content[0].text.strip()
    citations = citations_from_findings(all_findings)

    return {
        "question": question,
        "answer": answer_text,
        "citations": citations,
    }
