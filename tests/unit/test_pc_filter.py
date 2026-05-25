"""PCFilter — H16 vulgar/PC content filter."""
from __future__ import annotations

from agent_debate.agents.pc_filter import PCFilter


def _make_filter() -> PCFilter:
    return PCFilter({"stupid", "idiot", "moron", "shut up"})


def test_detects_vulgar_word():
    pc_filter = _make_filter()
    is_violation, _sanitized = pc_filter.check("That is a stupid argument.")
    assert is_violation is True


def test_returns_sanitized_with_asterisks():
    pc_filter = _make_filter()
    is_violation, sanitized = pc_filter.check("You are an idiot to think that.")
    assert is_violation is True
    assert sanitized == "You are an ***** to think that."


def test_passes_clean_text():
    pc_filter = _make_filter()
    is_violation, sanitized = pc_filter.check(
        "Latent-space combinations refute the remix claim."
    )
    assert is_violation is False
    assert sanitized is None


def test_case_insensitive_match():
    pc_filter = _make_filter()
    is_violation, sanitized = pc_filter.check("Frankly, you are a MORON.")
    assert is_violation is True
    assert sanitized is not None
    assert "*****" in sanitized
