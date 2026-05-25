"""Integration test (rubric §A8): when shared_spend crosses 95% of the
hard cap, ApiGatekeeper.execute raises BudgetExhausted before another LLM
call goes through.
"""
from __future__ import annotations

from multiprocessing import Lock, Value

import pytest

from agent_debate.shared.gatekeeper import ApiGatekeeper, BudgetExhausted


def _noop(*args, **kwargs) -> str:
    return "ok"


@pytest.mark.timeout(10)
def test_gatekeeper_aborts_when_spend_near_cap() -> None:
    cap = 100_000
    shared = Value("i", int(cap * 0.96))  # 96% of cap → hard refuse at 95%
    gk = ApiGatekeeper(
        config={
            "tokens_per_debate": cap,
            "warn_percent": 75, "hard_cap_percent": 95,
            "requests_per_minute": 60, "max_retries": 1,
        },
        shared_spend=shared, lock=Lock(),
    )
    with pytest.raises(BudgetExhausted):
        gk.execute(_noop)


@pytest.mark.timeout(10)
def test_gatekeeper_allows_call_under_cap() -> None:
    cap = 100_000
    shared = Value("i", int(cap * 0.50))  # 50% — under both warn + hard cap
    gk = ApiGatekeeper(
        config={
            "tokens_per_debate": cap,
            "warn_percent": 75, "hard_cap_percent": 95,
            "requests_per_minute": 60, "max_retries": 1,
        },
        shared_spend=shared, lock=Lock(),
    )
    assert gk.execute(_noop) == "ok"


@pytest.mark.timeout(10)
def test_spend_update_persists_in_shared_value() -> None:
    shared = Value("i", 0)
    gk = ApiGatekeeper(
        config={
            "tokens_per_debate": 100_000,
            "warn_percent": 75, "hard_cap_percent": 95,
            "requests_per_minute": 60, "max_retries": 1,
        },
        shared_spend=shared, lock=Lock(),
    )
    gk.update_spend(5000)
    gk.update_spend(2500)
    assert gk.get_spend_so_far() == 7500
