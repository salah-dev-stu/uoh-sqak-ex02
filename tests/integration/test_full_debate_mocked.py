"""Integration test: real Pro+Con multiprocessing.Processes driven by a
mocked LLM provider, full Judge-in-main routing, 5 pings.

Covers H1 (real LLM calls — mocked but through the LLMProvider seam),
H2 (JSON wire protocol), H3 (≥10 pings, here 5*2=10 messages min),
H4 (all traffic through Judge), H5 (no-tie verdict), H7 (Watchdog wiring
implicit via run_setup_phase ack timeout), H18 (setup_directive + ack),
H20 (drift correction path exists — exercised in test_drift_correction).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.constants import AgentRole, DebateOutcome, MessageRole
from agent_debate.orchestration.orchestrator import DebateOrchestrator
from agent_debate.shared.message_schema import validate_message
from tests.integration._helpers import mock_factory_default, skip_if_fork_unavailable


@pytest.mark.timeout(120)
def test_full_debate_runs_to_verdict(temp_skill_dir: Path, tmp_path: Path) -> None:
    skip_if_fork_unavailable()
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="ai-originality", n_pings=5,
        skill_dir=str(temp_skill_dir), dry_run=False,
    )
    assert transcript.outcome in (DebateOutcome.PRO_WINS, DebateOutcome.CON_WINS)
    assert transcript.finished_at is not None


@pytest.mark.timeout(120)
def test_full_debate_minimum_message_count(temp_skill_dir: Path, tmp_path: Path) -> None:
    skip_if_fork_unavailable()
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="topic-msg-count", n_pings=5,
        skill_dir=str(temp_skill_dir), dry_run=False,
    )
    pro_count = sum(1 for m in transcript.messages if m.get("from") == AgentRole.PRO.value)
    con_count = sum(1 for m in transcript.messages if m.get("from") == AgentRole.CON.value)
    # 5 pings each: at least one partisan message per ping per side after acks.
    assert pro_count >= 5, f"pro produced {pro_count} messages (expected ≥5)"
    assert con_count >= 5, f"con produced {con_count} messages (expected ≥5)"


@pytest.mark.timeout(120)
def test_every_message_is_schema_valid(temp_skill_dir: Path, tmp_path: Path) -> None:
    skip_if_fork_unavailable()
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="schema-valid", n_pings=3,
        skill_dir=str(temp_skill_dir), dry_run=False,
    )
    for msg in transcript.messages:
        # Some non-wire dict entries (e.g. boot record from dry-run flow) may
        # appear in mixed-run tests; skip anything without msg_id.
        if "msg_id" not in msg:
            continue
        validate_message(msg)


@pytest.mark.timeout(120)
def test_no_direct_pro_to_con_traffic(temp_skill_dir: Path, tmp_path: Path) -> None:
    """H4: Every Pro→Con message must be paired with an originating Pro→Judge
    message of the same msg_id (i.e. routed by Judge, not sent direct)."""
    skip_if_fork_unavailable()
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="no-direct-traffic", n_pings=3,
        skill_dir=str(temp_skill_dir), dry_run=False,
    )
    pro_to_judge = {m["msg_id"] for m in transcript.messages
                    if m.get("from") == "pro" and m.get("to") == "judge"}
    pro_to_con = [m for m in transcript.messages
                  if m.get("from") == "pro" and m.get("to") == "con"]
    for routed in pro_to_con:
        assert routed["msg_id"] in pro_to_judge, "Pro→Con without preceding Pro→Judge"


@pytest.mark.timeout(120)
def test_verdict_has_differential_scoring(temp_skill_dir: Path, tmp_path: Path) -> None:
    """H5: no tie. Synth scorecards must yield a winner (pro or con)."""
    skip_if_fork_unavailable()
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="no-tie", n_pings=3,
        skill_dir=str(temp_skill_dir), dry_run=False,
    )
    assert transcript.verdict is not None
    assert transcript.verdict.get("winner") in ("pro", "con")


@pytest.mark.timeout(120)
def test_setup_directive_acks_present(temp_skill_dir: Path, tmp_path: Path) -> None:
    """H18: transcript contains at least 2 setup_directive + 2 ack records."""
    skip_if_fork_unavailable()
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="setup-ack", n_pings=3,
        skill_dir=str(temp_skill_dir), dry_run=False,
    )
    directives = sum(
        1 for m in transcript.messages
        if m.get("role") == MessageRole.SETUP_DIRECTIVE.value
    )
    acks = sum(
        1 for m in transcript.messages if m.get("role") == MessageRole.ACK.value
    )
    assert directives >= 2, f"expected ≥2 setup_directives, got {directives}"
    assert acks >= 2, f"expected ≥2 acks, got {acks}"
