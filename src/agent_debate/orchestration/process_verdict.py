"""Verdict-finalization helpers for the real-process IPC flow (Phase 10).

Kept in its own module so `process_flow.py` and `orchestrator.py` stay
inside the 150-line limit.
"""
from __future__ import annotations

from agent_debate.agents.judge_agent import JudgeAgent
from agent_debate.agents.scoring_engine import Scorecard
from agent_debate.constants import DebateOutcome


def synth_scorecards(transcript) -> tuple[Scorecard, Scorecard]:
    """Phase-10 placeholder scorecards keyed on per-side message counts.

    Real scoring will be wired in Phase 11; for Phase 10 the integration
    tests need *some* differential signal to verify the no-tie path.
    """
    pro = sum(1 for m in transcript.messages if m.get("from") == "pro")
    con = sum(1 for m in transcript.messages if m.get("from") == "con")
    return (
        Scorecard(clarity=15, evidence=14, rebuttal=13, novelty=14,
                  role_fidelity=min(20, 10 + pro // 2)),
        Scorecard(clarity=15, evidence=14, rebuttal=12, novelty=13,
                  role_fidelity=min(20, 10 + con // 2)),
    )


def finalize_verdict(judge: JudgeAgent, transcript) -> DebateOutcome:
    """Score + declare winner; mutate transcript.verdict/outcome."""
    pro_card, con_card = synth_scorecards(transcript)
    outcome = judge.declare_winner(pro_card, con_card)
    transcript.outcome = outcome
    transcript.verdict = {
        "winner": "pro" if outcome == DebateOutcome.PRO_WINS else "con",
        "pro_total": pro_card.total,
        "con_total": con_card.total,
    }
    return outcome
