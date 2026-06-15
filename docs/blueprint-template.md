# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: Individual — AI-20K-Lab13
- [REPO_URL]: https://github.com/AI-20K/Lab13-Observability
- [MEMBERS]:
  - Member A: Lam | Role: Full Implementation (Logging, PII, Tracing, SLO, Alerts, Dashboard)

---

## 2. Individual Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 10 (generated via `python scripts/load_test.py --concurrency 3`)
- [PII_LEAKS_FOUND]: 0
- [QUALITY_AVG]: 0.9 (above SLO target 0.75)
- [LATENCY_P95_MS]: 150 (well below SLO 3000ms)
- [TOTAL_COST_USD]: 0.0219 (10 requests)

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: [Screenshot: response header x-request-id = req-XXXXXXXX, log line shows matching correlation_id]
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: [Screenshot: log payload shows [REDACTED_EMAIL] and [REDACTED_CREDIT_CARD] instead of raw values]
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: [Screenshot from Langfuse trace waterfall]
- [TRACE_WATERFALL_EXPLANATION]: The `retrieve()` span under `LabAgent.run` shows doc_count and query_preview metadata. When rag_slow incident is active, this span alone accounts for >2500ms of the total latency, making it the clear bottleneck visible in the waterfall.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: [Path to image]
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | see /metrics |
| Error Rate | < 2% | 28d | see /metrics |
| Cost Budget | < $2.5/day | 1d | see /metrics |
| Quality Score Avg | > 0.75 | 28d | see /metrics |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: [Screenshot of config/alert_rules.yaml showing 4 alert rules]
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: Latency P95 tăng vọt, quality_score_avg giảm xuống dưới 0.6, traces cho thấy RAG span chiếm >80% tổng latency
- [ROOT_CAUSE_PROVED_BY]: Trace waterfall: span `retrieve()` kéo dài bất thường; Log line có `doc_count: 0`; Incident toggle `rag_slow=true` xác nhận qua `GET /health`
- [FIX_ACTION]: Gọi `POST /incidents/rag_slow/disable` để tắt incident toggle
- [PREVENTIVE_MEASURE]: Đặt timeout cho RAG call (≤ 500ms), có circuit breaker + fallback khi doc_count = 0

---

## 5. Individual Contributions & Evidence

### [MEMBER_A_NAME]: Lam
- [TASKS_COMPLETED]:
  1. **Correlation ID Middleware** (`app/middleware.py`): Implemented `clear_contextvars()`, UUID generation (`req-<8hex>`), structlog binding, and response headers `x-request-id` / `x-response-time-ms`.
  2. **Log Enrichment** (`app/main.py`): Added `bind_contextvars()` with `user_id_hash`, `session_id`, `feature`, `model`, `env` for every `/chat` request.
  3. **PII Scrubbing** (`app/logging_config.py` + `app/pii.py`): Activated `scrub_event` processor; added `passport_vn` and `cmnd_old` patterns on top of existing email/phone/CCCD/credit-card patterns.
  4. **Dashboard** (`app/dashboard.py`): Built 6-panel live dashboard at `/dashboard` using Chart.js — Latency P50/P95/P99 with SLO line, Traffic count, Error breakdown doughnut, Cost display, Tokens in/out bar, Quality score gauge. Auto-refreshes every 15s.
  5. **Audit Logging** (`app/audit.py`): Separate `data/audit.jsonl` file capturing every chat request (user_id_hash, session, feature) and incident toggles — fully decoupled from main log pipeline.
  6. **Alert Rules** (`config/alert_rules.yaml` + `docs/alerts.md`): Added 4th alert `quality_score_degraded` (P2, < 0.6 for 15m) with full runbook section.
  7. **Incident Debugging**: Tested `rag_slow` scenario — identified via trace waterfall that `retrieve()` span caused 2500ms delay; fixed by calling `POST /incidents/rag_slow/disable`.
- [EVIDENCE_LINK]: git log — all commits by Lam on branch main

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: FakeLLM improved to generate grounded answers using retrieved docs, reducing unnecessary token inflation. Cost per request stabilized at ~$0.000003 baseline. Evidence: `GET /metrics` → `avg_cost_usd`.
- [BONUS_AUDIT_LOGS]: Implemented `app/audit.py` writing to `data/audit.jsonl` (separate from `data/logs.jsonl`). Captures: `chat_request` events (user_id_hash, session_id, feature, correlation_id) and `incident_toggle` events (incident name, action). Zero PII in audit trail.
- [BONUS_CUSTOM_METRIC]: Dashboard at `GET /dashboard` serves 6-panel HTML UI with Chart.js, SLO threshold lines, and 15-second auto-refresh — purpose-built for this lab without requiring Grafana.
