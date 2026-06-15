from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import get_client, observe  # noqa: F401  (re-exported)

    def flush_traces() -> None:
        get_client().flush()

except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):  # type: ignore[misc]
        def decorator(func):
            return func
        return decorator

    def flush_traces() -> None:
        pass


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
