"""DTOs exposed by the SDK to menu/tests/external Claude CLI self-test (N8)."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class SpendReport:
    """Token + cost rollup. `by_agent` is a {role: {axis: value}} dict."""

    total_input_tokens: int
    total_output_tokens: int
    estimated_cost_usd: Decimal
    pct_of_budget_used: float
    by_agent: dict[str, dict] = field(default_factory=dict)


@dataclass(frozen=True)
class HealthStatus:
    """Watchdog-sourced snapshot of child processes (Phase 10 wires this)."""

    children_alive: dict[str, bool]
    last_heartbeat_ages: dict[str, float]
    pending_messages: dict[str, int]
    restart_count: dict[str, int]


@dataclass(frozen=True)
class MenuResponse:
    """Return value of `DebateSDK.simulate_keystroke()` — the N8 self-test
    surface exercised by the external Claude CLI grader."""

    success: bool
    message: str
    payload: dict | None = None


@dataclass(frozen=True)
class DebateMetadata:
    """Compact summary of a persisted debate (used by `list_debates`)."""

    debate_id: str
    topic: str
    started_at: str
    finished_at: str | None
    outcome: str | None
    n_messages: int
