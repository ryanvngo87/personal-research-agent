import sys
import time
sys.stdout.reconfigure(encoding="utf-8")

from app.planner import decompose
from app.agent import run_agent
from app.synthesizer import synthesize
from app.tracer import save_trace


def main():
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Question: ")
    print(f"\nQuestion: {question}\n")
    start = time.time()

    error = None
    sub_queries, results, output = [], [], {}

    try:
        print("Decomposing into sub-queries...")
        sub_queries = decompose(question)
        for i, q in enumerate(sub_queries, 1):
            print(f"  {i}. {q}")

        print("\nRunning agent loop...\n")
        results = run_agent(sub_queries)

        print("Synthesizing answer...\n")
        output = synthesize(question, results)

        print(output["answer"])

        if output["citations"]:
            print("\n--- Citations ---")
            for i, c in enumerate(output["citations"], 1):
                print(f"[{i}] {c['source_type'].upper()} | {c['title']} | {c['url_or_id'] or 'local'}")
                print(f"    {c['snippet'][:120]}")

    except Exception as e:
        error = str(e)
        print(f"\nError: {error}")

    finally:
        trace_path = save_trace(question, sub_queries, results, output, start, error)
        print(f"\nTrace saved: {trace_path}")


if __name__ == "__main__":
    main()
