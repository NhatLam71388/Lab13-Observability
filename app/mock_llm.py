from __future__ import annotations

import random
import time
from dataclasses import dataclass

from .incidents import STATE


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    def generate(self, prompt: str) -> FakeResponse:
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        output_tokens = random.randint(80, 180)
        if STATE["cost_spike"]:
            output_tokens *= 4

        # Extract docs section from prompt to build a grounded answer
        docs_section = ""
        if "Docs=" in prompt:
            docs_section = prompt.split("Docs=", 1)[1].split("\nQuestion=")[0].strip()
        question_section = ""
        if "Question=" in prompt:
            question_section = prompt.split("Question=", 1)[1].strip()

        if docs_section and docs_section != "['No domain document matched. Use general fallback answer.']":
            answer = (
                f"Based on the retrieved documentation: {docs_section} "
                f"To answer your question about '{question_section[:60]}': "
                "the system uses structured logging, correlation IDs, and distributed tracing "
                "to provide full observability across the request lifecycle."
            )
        else:
            answer = (
                f"Regarding '{question_section[:80]}': "
                "observability best practices recommend combining metrics (detect), "
                "traces (localize), and logs (explain) for effective incident response. "
                "Ensure PII is never exposed in logs and all requests carry a correlation ID."
            )
        return FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)
