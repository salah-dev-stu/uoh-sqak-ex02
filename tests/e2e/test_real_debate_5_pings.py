"""E2E: real Claude CLI + real DuckDuckGo, 5 pings end-to-end.

Gated by `RUN_E2E=1`. Will not run in CI. Real Claude calls take ~30-60s
each × ~10 messages = 5-10 min total — hence the 600s timeout.

Asserts the persisted transcript exists, the verdict is declared, and no
crash escaped the orchestrator.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.constants import DebateOutcome
from agent_debate.orchestration.orchestrator import DebateOrchestrator
from agent_debate.tools.claude_login_provider import ClaudeLoginProvider


def _real_factory() -> ClaudeLoginProvider:
    return ClaudeLoginProvider()


@pytest.mark.e2e
@pytest.mark.timeout(600)
def test_real_5_ping_debate_runs_to_verdict(tmp_path: Path) -> None:
    orch = DebateOrchestrator(
        llm_provider_factory=_real_factory,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="Is AI-generated art genuinely original?",
        n_pings=5, skill_dir="./.claude/skills", dry_run=False,
    )
    assert transcript.outcome in (DebateOutcome.PRO_WINS, DebateOutcome.CON_WINS)
    assert transcript.finished_at is not None
    assert transcript.verdict is not None
    assert transcript.verdict.get("winner") in ("pro", "con")
    files = list((tmp_path / "transcripts").glob("*.json"))
    assert files, "transcript file not persisted"
