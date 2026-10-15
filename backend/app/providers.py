import os
from typing import Protocol

from .engine.planner import plan
from .engine.schema import AppSpec


class SpecProvider(Protocol):
    def suggest(self, prompt: str) -> AppSpec | None: ...


class NullProvider:
    def suggest(self, prompt: str) -> AppSpec | None:
        return None


class GroqProvider:
    def suggest(self, prompt: str) -> AppSpec | None:
        from langchain_groq import ChatGroq

        model = ChatGroq(model="llama-3.3-70b-versatile")
        result = model.with_structured_output(AppSpec).invoke(
            "Return a small business website specification for this request. "
            "Use only supplied facts; do not invent contact details or testimonials. " + prompt
        )
        return AppSpec.model_validate(result)


def create_spec(prompt: str, provider: SpecProvider | None = None) -> AppSpec:
    selected = provider
    if selected is None:
        selected = GroqProvider() if os.getenv("SITEFORGE_LLM_PROVIDER") == "groq" and os.getenv("GROQ_API_KEY") else NullProvider()
    try:
        candidate = selected.suggest(prompt)
        if candidate is not None:
            return AppSpec.model_validate(candidate)
    except Exception:
        pass
    return plan(prompt)
