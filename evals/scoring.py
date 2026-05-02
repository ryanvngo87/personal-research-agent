def score_keyword_coverage(answer: str, expected_keywords: list[str]) -> float:
    """Fraction of expected keywords present in the answer (case-insensitive)."""
    if not expected_keywords:
        return 1.0
    answer_lower = answer.lower()
    hits = sum(1 for kw in expected_keywords if kw.lower() in answer_lower)
    return round(hits / len(expected_keywords), 2)


def score_tool_usage(agent_results: list[dict], expected_tools: list[str]) -> float:
    """Fraction of expected tools that were actually called."""
    if not expected_tools:
        return 1.0
    tools_called = set()
    for result in agent_results:
        tools_called.update(result.get("tools_called", []))
    hits = sum(1 for t in expected_tools if t in tools_called)
    return round(hits / len(expected_tools), 2)


def score_citation_presence(citations: list[dict], expected: bool) -> float:
    """1.0 if citation expectation is met, 0.0 otherwise."""
    has_citations = len(citations) > 0
    return 1.0 if has_citations == expected else 0.0


def score_completeness(answer: str, sub_queries: list[str]) -> float:
    """Rough proxy: did the answer length suggest all sub-queries were addressed."""
    if not sub_queries:
        return 1.0
    min_expected_words = len(sub_queries) * 20
    word_count = len(answer.split())
    return min(1.0, round(word_count / min_expected_words, 2))


def compute_scores(case: dict, output: dict, agent_results: list[dict], sub_queries: list[str]) -> dict:
    answer = output.get("answer", "")
    citations = output.get("citations", [])
    return {
        "keyword_coverage": score_keyword_coverage(answer, case.get("expected_keywords", [])),
        "tool_usage": score_tool_usage(agent_results, case.get("expected_tools", [])),
        "citation_presence": score_citation_presence(citations, case.get("expected_citations", False)),
        "completeness": score_completeness(answer, sub_queries),
    }


def overall_score(scores: dict) -> float:
    values = list(scores.values())
    return round(sum(values) / len(values), 2) if values else 0.0
