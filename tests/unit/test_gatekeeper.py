"""ApiGatekeeper — rate limit + token budget + retry + FIFO queue.

Signature matches rubric §A4 verbatim.
"""
from multiprocessing import Lock, Value

import pytest

from agent_debate.shared.gatekeeper import (
    ApiGatekeeper,
    BudgetExhausted,
    QueueStatus,
)


def _config() -> dict:
    return {
        "tokens_per_debate": 1000,
        "warn_at_percent": 75,
        "hard_cap_percent": 95,
        "requests_per_minute": 30,
        "concurrent_max": 3,
        "max_retries": 3,
    }


def _make_gatekeeper() -> ApiGatekeeper:
    spend = Value("i", 0)
    lock = Lock()
    return ApiGatekeeper(config=_config(), shared_spend=spend, lock=lock)


def test_execute_passes_through_simple_call():
    gk = _make_gatekeeper()
    result = gk.execute(lambda: 42)
    assert result == 42


def test_spend_starts_at_zero():
    gk = _make_gatekeeper()
    assert gk.get_spend_so_far() == 0


def test_update_spend_increments():
    gk = _make_gatekeeper()
    gk.update_spend(100)
    gk.update_spend(50)
    assert gk.get_spend_so_far() == 150


def test_budget_below_threshold_succeeds():
    gk = _make_gatekeeper()
    gk.update_spend(800)  # 80% — above 75% warn but below 95% hard cap
    result = gk.execute(lambda: "ok")
    assert result == "ok"


def test_budget_above_hard_cap_raises():
    gk = _make_gatekeeper()
    gk.update_spend(960)  # 96% — above 95% hard cap
    with pytest.raises(BudgetExhausted):
        gk.execute(lambda: "won't run")


def test_retry_on_transient_failure():
    gk = _make_gatekeeper()
    attempts: list[int] = []

    def flaky():
        attempts.append(1)
        if len(attempts) < 3:
            raise ConnectionError("transient")
        return "ok"

    result = gk.execute(flaky)
    assert result == "ok"
    assert len(attempts) == 3


def test_queue_status_reports_initial_state():
    gk = _make_gatekeeper()
    status = gk.get_queue_status()
    assert isinstance(status, QueueStatus)
    assert status.depth == 0


def test_estimate_cost_zero_in_login_mode():
    from decimal import Decimal
    gk = _make_gatekeeper()
    assert gk.estimate_cost(n_debates=5) == Decimal("0.00")
