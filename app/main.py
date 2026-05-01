import sys
from app.planner import decompose
from app.agent import run_agent


def main():
    question = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Question: ")
    print(f"\nQuestion: {question}\n")

    print("Decomposing into sub-queries...")
    sub_queries = decompose(question)
    for i, q in enumerate(sub_queries, 1):
        print(f"  {i}. {q}")

    print("\nRunning agent loop...\n")
    results = run_agent(sub_queries)

    for r in results:
        print(f"Sub-query: {r.get('sub_query', '')}")
        print(f"Summary:   {r.get('summary', '')}\n")


if __name__ == "__main__":
    main()
