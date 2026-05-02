import sys
import os
import json
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from app.planner import decompose
from app.agent import run_agent
from app.synthesizer import synthesize
from app.tracer import save_trace
from app.config import TRACES_DIR

st.set_page_config(page_title="Personal Research Agent", layout="wide")


@st.cache_resource(show_spinner="Loading embedding model...")
def preload_model():
    from retrieval.embeddings import get_model
    return get_model()


preload_model()

st.title("Personal Research Agent")
st.caption("Ask a question — I'll search your notes, the web, and GitHub to answer it.")


def load_recent_traces(n: int = 10) -> list[dict]:
    if not os.path.exists(TRACES_DIR):
        return []
    files = sorted(
        [f for f in os.listdir(TRACES_DIR) if f.endswith(".json")],
        reverse=True,
    )[:n]
    traces = []
    for fname in files:
        with open(os.path.join(TRACES_DIR, fname), encoding="utf-8") as f:
            traces.append(json.load(f))
    return traces


# Sidebar — recent runs
with st.sidebar:
    st.header("Recent Runs")
    traces = load_recent_traces()
    if not traces:
        st.caption("No runs yet.")
    for t in traces:
        with st.expander(f"{t['timestamp'][:16].replace('T', ' ')}"):
            st.markdown(f"**Q:** {t['question']}")
            st.markdown(f"**Latency:** {t['latency_seconds']}s")
            if t.get("error"):
                st.error(t["error"])

# Main area
question = st.text_input("Your question", placeholder="e.g. What is MCP and how does it work?")
run_btn = st.button("Run", type="primary", disabled=not question.strip())

if run_btn and question.strip():
    start = time.time()
    error = None
    sub_queries, results, output = [], [], {}

    try:
        # Step 1 — Decompose
        with st.status("Decomposing question into sub-queries...", expanded=True) as status:
            sub_queries = decompose(question)
            for i, q in enumerate(sub_queries, 1):
                st.write(f"{i}. {q}")
            status.update(label=f"Decomposed into {len(sub_queries)} sub-queries", state="complete")

        # Step 2 — Agent loop
        with st.status("Running agent loop...", expanded=True) as status:
            results = []
            for i, q in enumerate(sub_queries, 1):
                st.write(f"Researching: _{q}_")
                result = run_agent([q])[0]
                results.append(result)
                tools = ", ".join(set(result.get("tools_called", []))) or "none"
                st.write(f"  Tools used: `{tools}`")
            status.update(label="Agent loop complete", state="complete")

        # Step 3 — Synthesize
        with st.spinner("Synthesizing answer..."):
            output = synthesize(question, results)

    except Exception as e:
        error = str(e)
        st.error(f"Error: {error}")

    finally:
        save_trace(question, sub_queries, results, output, start, error)

    # Display answer
    if output.get("answer"):
        st.divider()
        st.markdown(output["answer"])

        # Citations
        citations = output.get("citations", [])
        if citations:
            st.divider()
            with st.expander(f"Citations ({len(citations)})"):
                for i, c in enumerate(citations, 1):
                    st.markdown(
                        f"**[{i}] {c['source_type'].upper()}** — {c['title']}  \n"
                        f"`{c['url_or_id'] or 'local'}`  \n"
                        f"_{c['snippet'][:200]}_"
                    )
                    st.divider()

        elapsed = round(time.time() - start, 1)
        st.caption(f"Completed in {elapsed}s")
