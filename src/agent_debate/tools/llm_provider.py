"""Abstract LLM provider. Concrete adapters: ClaudeLoginProvider, MockLLMProvider."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class LLMResponse:
    text: str
    tokens_in: int
    tokens_out: int
    finish_reason: Literal["stop", "length", "timeout", "error"]
    raw_json: dict = field(default_factory=dict)


class LLMProvider(ABC):
    """
    Input:  system (str), user (str), temperature (float), max_tokens (int)
    Output: LLMResponse (text + token counts + finish_reason)
    Setup:  (subclass-specific)
    """

    @abstractmethod
    def complete(
        self, system: str, user: str, temperature: float, max_tokens: int = 1000
    ) -> LLMResponse:
        ...
