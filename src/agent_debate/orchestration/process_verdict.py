"""Verdict-finalization helpers for the real-process IPC flow (Phase 10).

Kept in its own module so `process_flow.py` and `orchestrator.py` stay
inside the 150-line limit.
"""
from __future__ import annotations

from agent_debate.agents.content_scorer import score_transcript
from agent_debate.agents.judge_agent import JudgeAgent
from agent_debate.agents.scoring_engine import Scorecard
from agent_debate.constants import DebateOutcome


def synth_scorecards(transcript) -> tuple[Scorecard, Scorecard]:
    """Score Pro and Con from the actual transcript content.

    Delegates to agent_debate.agents.content_scorer.score_transcript,
    which derives all 5 axes from text features so different debates
    produce different scores. Kept under this name for back-compat
    with the orchestrator import; new callers should import
    score_transcript directly.
    """
    return score_transcript(transcript)


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
