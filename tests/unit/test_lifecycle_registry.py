"""Tests for LifecycleRegistry (rubric §A9 + HW1 extensibility fix)."""
from __future__ import annotations

from agent_debate.orchestration.lifecycle_registry import LifecycleRegistry


def test_8_hooks_registered_by_default() -> None:
    names = LifecycleRegistry.hook_names()
    assert len(names) == 8
    assert "before_round" in names
    assert "after_round" in names
    assert "before_verdict" in names
    assert "after_verdict" in names
    assert "before_llm_call" in names
    assert "after_llm_call" in names
    assert "before_search" in names
    assert "after_search" in names


def test_register_and_fire_in_order() -> None:
    reg = LifecycleRegistry()
    calls: list[str] = []

    def hook_a(ctx: dict) -> None:
        calls.append("a")

    def hook_b(ctx: dict) -> None:
        calls.append("b")

    reg.register("before_round", hook_a)
    reg.register("before_round", hook_b)
    reg.fire("before_round", {})

    assert calls == ["a", "b"]


def test_unknown_hook_silently_passes() -> None:
    reg = LifecycleRegistry()
    # Should not raise
    result = reg.fire("nonexistent", {"foo": "bar"})
    assert result == {"foo": "bar"}


def test_hook_exception_doesnt_break_chain() -> None:
    reg = LifecycleRegistry()
    calls: list[str] = []

    def bad_hook(ctx: dict) -> None:
        raise RuntimeError("boom")

    def good_hook(ctx: dict) -> None:
        calls.append("ran")

    reg.register("after_round", bad_hook)
    reg.register("after_round", good_hook)
    reg.fire("after_round", {})

    assert calls == ["ran"]


def test_register_unknown_hook_silently_ignored() -> None:
    reg = LifecycleRegistry()
    calls: list[str] = []

    def fn(ctx: dict) -> None:
        calls.append("x")

    # Should not raise
    reg.register("bad_name", fn)
    # And firing a real hook should not trigger this fn
    reg.fire("before_round", {})
    assert calls == []
