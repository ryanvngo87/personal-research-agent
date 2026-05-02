import json
import os
import time
from datetime import datetime
from app.config import TRACES_DIR


def save_trace(
    question: str,
    sub_queries: list[str],
    agent_results: list[dict],
    output: dict,
    start_time: float,
    error: str | None = None,
) -> str:
    trace = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "latency_seconds": round(time.time() - start_time, 2),
        "question": question,
        "sub_queries": sub_queries,
        "agent_results": agent_results,
        "answer": output.get("answer", ""),
        "citations": output.get("citations", []),
        "error": error,
    }

    os.makedirs(TRACES_DIR, exist_ok=True)
    filename = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ") + ".json"
    filepath = os.path.join(TRACES_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

    return filepath
