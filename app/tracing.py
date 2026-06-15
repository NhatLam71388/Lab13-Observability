from __future__ import annotations

import os
from typing import Any

try:
    from langfuse import Langfuse
    from langfuse.decorators import langfuse_context, observe

    _langfuse_client = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )

    def flush_traces() -> None:
        _langfuse_client.flush()

except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):  # type: ignore[misc]
        def decorator(func):
            return func
        return decorator

    class _DummyContext:
        def update_current_trace(self, **kwargs: Any) -> None:
            return None

        def update_current_observation(self, **kwargs: Any) -> None:
            return None

    langfuse_context = _DummyContext()

    def flush_traces() -> None:
        pass


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
