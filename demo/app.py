"""Run:  streamlit run demo/app.py   (secondary to the benchmark - kept deliberately simple)"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import streamlit as st
from src.router.routing import route_and_run

st.title("Smart Model Router (prototype)")
text = st.text_area("Describe the task (paste the meeting/email/data):", "Summarise this meeting and extract action items.", height=200)
call = st.checkbox("Call the selected model (uses free-tier quota)", value=True)
if st.button("Route"):
    try:
        r = route_and_run(text, call=call)
    except FileNotFoundError:
        st.error("models/router.pkl not found - run the benchmark and `python -m src.main train-router` first."); st.stop()
    c1, c2, c3 = st.columns(3)
    c1.metric("Category", r["category"]); c2.metric("Difficulty (estimated)", r["difficulty_estimate"]); c3.metric("Selected model", r["selected_tier"])
    st.write(f"**Model:** `{r['selected_model']}`  |  **Routing confidence:** {r['confidence']} (threshold {r['threshold']})"
             + ("  |  **escalated one level (low confidence)**" if r["escalated"] else ""))
    if call:
        st.write(f"**Estimated cost:** {r['estimated_cost_usd'] if r['estimated_cost_usd'] is None else f'${r['estimated_cost_usd']:.6f}'}"
                 f"  |  **Latency:** {r['latency_ms'] and round(r['latency_ms'])} ms")
        st.subheader("Response"); st.write(r["response"] or r["error"])
    st.info("Selected because this model was the lowest-cost model predicted to satisfy the benchmark quality requirement.")
