"""Send 3 requests under rag_slow incident to demonstrate debugging flow."""
import httpx

BASE = "http://127.0.0.1:8000"

payloads = [
    {"user_id": "u_inc_01", "session_id": "s_inc_01", "feature": "qa", "message": "What is the monitoring policy?"},
    {"user_id": "u_inc_02", "session_id": "s_inc_02", "feature": "qa", "message": "Explain refund policy in detail"},
    {"user_id": "u_inc_03", "session_id": "s_inc_03", "feature": "summary", "message": "Summarize observability workflow"},
]

with httpx.Client(timeout=30.0) as c:
    # Enable rag_slow
    r = c.post(f"{BASE}/incidents/rag_slow/enable")
    print("Incident enabled:", r.json())

    print("\n--- Requests under rag_slow incident ---")
    for p in payloads:
        r = c.post(f"{BASE}/chat", json=p)
        d = r.json()
        print(f"[{r.status_code}] {d['correlation_id']} | latency={d['latency_ms']}ms | quality={d['quality_score']}")

    # Disable rag_slow
    r = c.post(f"{BASE}/incidents/rag_slow/disable")
    print("\nIncident disabled:", r.json())
