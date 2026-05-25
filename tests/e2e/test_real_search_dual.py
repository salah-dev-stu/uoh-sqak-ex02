"""E2E (H24): real Claude + real DDG, 3-ping debate; assert both Pro
and Con messages contain ≥1 citation. Dual-search-usage verification.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.orchestration.orchestrator import DebateOrchestrator
from agent_debate.tools.claude_login_provider import ClaudeLoginProvider


def _real_factory() -> ClaudeLoginProvider:
    return ClaudeLoginProvider()


@pytest.mark.e2e
@pytest.mark.timeout(600)
def test_both_sides_use_web_search_at_least_once(tmp_path: Path) -> None:
    orch = DebateOrchestrator(
        llm_provider_factory=_real_factory,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="Is AI-generated art genuinely original?",
        n_pings=3, skill_dir="./.claude/skills", dry_run=False,
    )
    pro_citations = [
        m for m in transcript.messages
        if m.get("from") == "pro" and m.get("citations")
    ]
    con_citations = [
        m for m in transcript.messages
        if m.get("from") == "con" and m.get("citations")
    ]
    assert pro_citations, "no Pro messages carried citations"
    assert con_citations, "no Con messages carried citations"
