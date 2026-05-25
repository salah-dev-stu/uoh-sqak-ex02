"""Module-level helpers for integration tests.

Multiprocessing 'spawn' start method pickles the Process target + kwargs,
so factory callables and helper functions must live at module scope
(not closure-captured fixtures) or pickling fails on macOS.
"""
from __future__ import annotations

import os
import sys

from agent_debate.tools.mock_llm_provider import MockLLMProvider


def mock_factory_default() -> MockLLMProvider:
    """Picklable, multiprocess-safe factory for the mock LLM provider."""
    return MockLLMProvider(default_text="(integration-mock argument)")


def mock_factory_drift() -> MockLLMProvider:
    """Mock that emits a drift keyword on the first Pro turn."""
    return MockLLMProvider(default_text="I concede the point you've raised.")


def mock_factory_pc() -> MockLLMProvider:
    """Mock that emits a PC-filter keyword on the first turn."""
    return MockLLMProvider(default_text="That argument is just stupid.")


def mock_factory_slow() -> MockLLMProvider:
    """Mock that sleeps to simulate a hung LLM call (chaos test)."""
    import time

    class SlowMock(MockLLMProvider):
        def complete(self, system, user, temperature, max_tokens=1000):
            time.sleep(60)
            return super().complete(system, user, temperature, max_tokens)

    return SlowMock(default_text="(slow)")


def skip_if_fork_unavailable() -> None:
    """Some CI runners lack os.fork(); pytest skip-with-reason if so."""
    import pytest

    if sys.platform == "win32" or not hasattr(os, "fork"):
        pytest.skip("multiprocessing fork not available on this platform")
