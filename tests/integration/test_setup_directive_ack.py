"""Integration test for H18: two-phase boot — Pro/Con each receive a
setup_directive and reply with an ack BEFORE the first argument.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.constants import MessageRole
from agent_debate.orchestration.orchestrator import DebateOrchestrator
from tests.integration._helpers import mock_factory_default, skip_if_fork_unavailable


@pytest.mark.timeout(120)
def test_setup_phase_precedes_first_argument(
    temp_skill_dir: Path, tmp_path: Path
) -> None:
    skip_if_fork_unavailable()
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default,
        transcript_dir=tmp_path / "transcripts",
    )
    transcript = orch.run_debate(
        topic="phase-a", n_pings=2, skill_dir=str(temp_skill_dir), dry_run=False,
    )
    indices: list[tuple[int, str]] = []
    for i, m in enumerate(transcript.messages):
        role = m.get("role")
        if role in (
            MessageRole.SETUP_DIRECTIVE.value,
            MessageRole.ACK.value,
            MessageRole.ARGUMENT.value,
            MessageRole.COUNTER.value,
        ):
            indices.append((i, role))
    first_argument = next(
        (i for i, r in indices if r == MessageRole.ARGUMENT.value), None
    )
    assert first_argument is not None, "no argument observed at all"
    boot_records = [r for i, r in indices if i < first_argument]
    n_setup = sum(1 for r in boot_records if r == MessageRole.SETUP_DIRECTIVE.value)
    n_ack = sum(1 for r in boot_records if r == MessageRole.ACK.value)
    assert n_setup >= 2, f"need ≥2 setup_directives before first argument; got {n_setup}"
    assert n_ack >= 2, f"need ≥2 acks before first argument; got {n_ack}"
