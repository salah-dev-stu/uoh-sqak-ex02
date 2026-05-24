"""Smoke test — ensures pytest collection works and hooks pass before Phase 1 tests land."""
from __future__ import annotations

from agent_debate import __version__


def test_version_present() -> None:
    """Package exposes __version__ per R6 versioning rule."""
    assert __version__ == "1.00"
