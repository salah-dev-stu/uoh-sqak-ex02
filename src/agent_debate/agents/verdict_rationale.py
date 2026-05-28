"""Build a short, human-readable rationale for the Judge's verdict.

Deterministic from the two scorecards — no extra LLM call. The Judge
identifies the largest axis gap in the winner's favour and the axis
the loser held its ground on, and assembles a 2-sentence explanation
so the chyron can show *why* one side won rather than just numbers.
"""
from __future__ import annotations

from agent_debate.agents.scoring_engine import Scorecard

AXIS_LABELS: dict[str, str] = {
    "clarity": "clarity",
    "evidence": "evidence",
    "rebuttal": "engagement with the opponent",
    "novelty": "lexical range",
    "role_fidelity": "adherence to its assigned stance",
}
_AXES = ("clarity", "evidence", "rebuttal", "novelty", "role_fidelity")


def _diffs(winner: Scorecard, loser: Scorecard) -> list[tuple[str, int]]:
    """Sorted list of (axis, winner-loser). Positive = winner's strength."""
    return sorted(
        ((axis, getattr(winner, axis) - getattr(loser, axis)) for axis in _AXES),
        key=lambda kv: kv[1],
        reverse=True,
    )


def build_rationale(pro: Scorecard, con: Scorecard, winner: str) -> str:
    """Return a 1-2 sentence rationale tying the verdict to the scorecards."""
    if winner == "pro":
        w_card, l_card, w_label, l_label = pro, con, "Pro", "Con"
    else:
        w_card, l_card, w_label, l_label = con, pro, "Con", "Pro"

    diffs = _diffs(w_card, l_card)
    top_axis, top_gap = diffs[0]
    bottom_axis, bottom_gap = diffs[-1]

    margin = w_card.total - l_card.total
    head = f"{w_label} took it {w_card.total}-{l_card.total}"
    if margin <= 2:
        head += " by a hair"
    elif margin >= 15:
        head += " in a decisive showing"
    head += "."

    if top_gap <= 0:
        # Winner won on tiebreak chain — no positive-gap axis.
        return head + f" The two sides were close on every axis; {w_label} edged the tiebreak on role_fidelity."

    body = f" {w_label}'s edge was {AXIS_LABELS[top_axis]} (+{top_gap})"
    if bottom_gap < 0:
        body += f", though {l_label} held the lead on {AXIS_LABELS[bottom_axis]} ({bottom_gap:+d})."
    else:
        body += "."
    return head + body
