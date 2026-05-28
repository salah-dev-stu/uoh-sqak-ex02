"""Integration test: graceful shutdown — Pro/Con processes exit cleanly
within 10s of `shutdown_gracefully()` and the transcript persists.
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest

from agent_debate.orchestration.orchestrator import DebateOrchestrator
from tests.integration._helpers import mock_factory_default, skip_if_fork_unavailable


@pytest.mark.timeout(120)
def test_shutdown_kills_started_children(
    temp_skill_dir: Path, tmp_path: Path
) -> None:
    skip_if_fork_unavailable()
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default,
        transcript_dir=tmp_path / "transcripts",
    )
    orch.spawn_children(topic="shutdown", skill_dir=str(temp_skill_dir))
    for role in ("pro", "con"):
        orch._child_map[role].start()
    time.sleep(0.5)
    started = [orch._child_map[r] for r in ("pro", "con")]
    assert all(p.is_alive() for p in started)
    t0 = time.time()
    orch.shutdown_gracefully()
    elapsed = time.time() - t0
    assert elapsed < 15.0, f"shutdown took {elapsed:.1f}s (limit 15s)"
    assert all(not p.is_alive() for p in started)


@pytest.mark.timeout(120)
def test_partial_debate_then_shutdown_persists_transcript(
    temp_skill_dir: Path, tmp_path: Path
) -> None:
    """Run a 2-ping debate; verify the transcript file is written even
    after graceful shutdown."""
    skip_if_fork_unavailable()
    transcript_dir = tmp_path / "transcripts"
    orch = DebateOrchestrator(
        llm_provider_factory=mock_factory_default, transcript_dir=transcript_dir,
    )
    transcript = orch.run_debate(
        topic="partial", n_pings=2, skill_dir=str(temp_skill_dir), dry_run=False,
    )
    files = list(transcript_dir.glob("*.json"))
    assert files, "no transcript persisted after shutdown"
    assert transcript.finished_at is not None
