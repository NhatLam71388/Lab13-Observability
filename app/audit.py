from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

AUDIT_PATH = Path(os.getenv("AUDIT_LOG_PATH", "data/audit.jsonl"))


def _write(record: dict[str, Any]) -> None:
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


def audit_chat(user_id_hash: str, session_id: str, feature: str, correlation_id: str) -> None:
    _write({
        "ts": datetime.now(timezone.utc).isoformat(),
        "audit_event": "chat_request",
        "user_id_hash": user_id_hash,
        "session_id": session_id,
        "feature": feature,
        "correlation_id": correlation_id,
    })


def audit_incident(name: str, action: str, correlation_id: str) -> None:
    _write({
        "ts": datetime.now(timezone.utc).isoformat(),
        "audit_event": "incident_toggle",
        "incident": name,
        "action": action,
        "correlation_id": correlation_id,
    })
