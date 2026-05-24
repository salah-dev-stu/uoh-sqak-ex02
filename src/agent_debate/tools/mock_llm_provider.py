"""In-memory mock LLM provider for unit + integration tests. NO network."""
from __future__ import annotations

from agent_debate.tools.llm_provider import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """
    Input:  system, user, temperature, max_tokens
    Output: LLMResponse from canned `responses` dict keyed by (skill_prefix, call_idx)
    Setup:  responses (dict, optional), default_text (str)
    """

    def __init__(
        self, responses: dict | None = None, default_text: str = "(mock)"
    ) -> None:
        self.responses = responses or {}
        self.default_text = default_text
        self._call_counts: dict[str, int] = {}

    def complete(
        self, system: str, user: str, temperature: float, max_tokens: int = 1000
    ) -> LLMResponse:
        key_prefix = system.split()[0] if system else "unknown"
        idx = self._call_counts.get(key_prefix, 0) + 1
        self._call_counts[key_prefix] = idx
        text = self.responses.get((key_prefix, idx), self.default_text)
        return LLMResponse(
            text=text,
            tokens_in=len(user) // 4,
            tokens_out=len(text) // 4,
            finish_reason="stop",
        )
