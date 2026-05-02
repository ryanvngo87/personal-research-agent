"""
Run all evaluation cases and print a scored report.
Usage: python -m evals.run_evals
"""
import sys
import os
import json
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.planner import decompose
from app.agent import run_agent
from app.synthesizer import synthesize
from app.tracer import save_trace
from evals.scoring import compute_scores, overall_score

CASES_PATH = os.path.join(os.path.dirname(__file__), "eval_cases.json")


def run_case(case: dict) -> dict:
    question = case["question"]
    start = time.time()
    error = None
    sub_queries, agent_results, output = [], [], {}

    try:
        sub_queries = decompose(question)
        agent_results = run_agent(sub_queries)
        output = synthesize(question, agent_results)
    except Exception as e:
        error = str(e)

    save_trace(question, sub_queries, agent_results, output, start, error)
    scores = compute_scores(case, output, agent_results, sub_queries)

    return {
        "id": case["id"],
        "question": question,
        "scores": scores,
        "overall": overall_score(scores),
        "error": error,
        "latency": round(time.time() - start, 2),
    }


def main():
    with open(CASES_PATH, encoding="utf-8") as f:
        cases = json.load(f)

    print(f"Running {len(cases)} eval cases...\n")
    results = []

    for case in cases:
        print(f"  [{case['id']}] {case['question'][:60]}...")
        result = run_case(case)
        results.append(result)
        status = "ERROR" if result["error"] else f"{result['overall']:.2f}"
        print(f"         Score: {status} | Latency: {result['latency']}s")

    print("\n=== Eval Report ===")
    print(f"{'ID':<12} {'Overall':>8} {'Keywords':>10} {'Tools':>8} {'Citations':>10} {'Complete':>10}")
    print("-" * 62)
    for r in results:
        s = r["scores"]
        print(
            f"{r['id']:<12} {r['overall']:>8.2f} {s['keyword_coverage']:>10.2f} "
            f"{s['tool_usage']:>8.2f} {s['citation_presence']:>10.2f} {s['completeness']:>10.2f}"
        )

    avg = round(sum(r["overall"] for r in results) / len(results), 2)
    print("-" * 62)
    print(f"{'AVERAGE':<12} {avg:>8.2f}")


if __name__ == "__main__":
    main()
