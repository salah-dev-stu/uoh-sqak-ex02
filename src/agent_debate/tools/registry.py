"""Generic factory registry for plugin patterns (LLM providers, search providers).

This is the extensibility surface HW1 was flagged on. Adding a new provider is
one `Registry.register()` call + one config-key change. Zero core-code edit.
"""
from __future__ import annotations


class Registry[T]:
    """
    Input:  key (str), value (T)
    Output: registered value retrievable by key, or KeyError if missing
    Setup:  (none) — instantiated empty; register() populates
    """

    def __init__(self) -> None:
        self._items: dict[str, T] = {}

    def register(self, key: str, value: T) -> None:
        self._items[key] = value

    def get(self, key: str) -> T:
        if key not in self._items:
            raise KeyError(f"unknown registry key: {key!r}")
        return self._items[key]

    def keys(self) -> list[str]:
        return list(self._items.keys())
