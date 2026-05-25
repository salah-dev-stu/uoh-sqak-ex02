"""LifecycleRegistry — 8 named hooks (rubric §A9 + HW1 extensibility fix).

Hooks: before_round, after_round, before_verdict, after_verdict,
       before_llm_call, after_llm_call, before_search, after_search.

Each hook takes a context dict. Hooks fire in registration order.
Exceptions in one hook do not break the chain.
"""
from __future__ import annotations

from collections.abc import Callable

_HOOK_NAMES = (
    "before_round", "after_round",
    "before_verdict", "after_verdict",
    "before_llm_call", "after_llm_call",
    "before_search", "after_search",
)


class LifecycleRegistry:
    """
    Input:  name (str), fn (Callable[[dict], None | dict])
    Output: (mutates) hook list, or fires registered hooks with context
    Setup:  none — empty dict initialized
    """

    def __init__(self) -> None:
        self._hooks: dict[str, list[Callable]] = {name: [] for name in _HOOK_NAMES}

    def register(self, name: str, fn: Callable) -> None:
        if name not in self._hooks:
            return  # silently ignore unknown hook names
        self._hooks[name].append(fn)

    def fire(self, name: str, context: dict) -> dict:
        """Run all hooks registered for `name`. Exceptions are swallowed
        (logged elsewhere via StructuredLogger if needed)."""
        if name not in self._hooks:
            return context
        for fn in self._hooks[name]:
            try:
                fn(context)
            except Exception:  # noqa: BLE001 — hook isolation is the contract
                continue
        return context

    @classmethod
    def hook_names(cls) -> tuple[str, ...]:
        return _HOOK_NAMES
