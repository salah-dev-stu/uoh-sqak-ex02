"""Tests for the content-derived scorer that replaced the Phase-10 stub."""
from __future__ import annotations

from dataclasses import dataclass, field

from agent_debate.agents.content_scorer import score_transcript


@dataclass
class _FakeTranscript:
    messages: list[dict] = field(default_factory=list)


def _msg(side: str, text: str, role: str = "argument") -> dict:
    return {"from": side, "to": "judge", "role": role, "text": text, "ping_index": 1}


def test_empty_transcript_gives_baseline_scores() -> None:
    pro, con = score_transcript(_FakeTranscript())
    # No content → every axis falls back to its empty-input baseline.
    # 10 (clarity) + 0 (evidence) + 0 (rebuttal) + 10 (novelty) + 12 (role_fidelity floor)
    assert pro.total == con.total == 32


def test_different_transcripts_produce_different_totals() -> None:
    weak = _FakeTranscript(messages=[
        _msg("pro", "Yes. Good. AI makes art."),
        _msg("con", "No. Bad. AI copies."),
    ])
    strong = _FakeTranscript(messages=[
        _msg("pro",
             "Originality has never meant ex nihilo. Picasso absorbed African "
             "masks, Bach studied Vivaldi. AlphaGo's Move 37 in 2016 was "
             "statistically improbable yet professionals called it creative. "
             "Generative models produce protein folds absent from any training "
             "corpus — that demonstrates novel composition."),
        _msg("con",
             "Your argument smuggles its conclusion. The Getty lawsuit and "
             "the NYT lawsuit in 2023 document near-verbatim regurgitation. "
             "AlphaGo searched a closed rule-space — category error. New "
             "joint distributions are interpolation inside the convex hull "
             "of training data, not transcendence. The opponent conflates "
             "recombination with creativity."),
    ])
    w_pro, w_con = score_transcript(weak)
    s_pro, s_con = score_transcript(strong)
    assert s_pro.total > w_pro.total
    assert s_con.total > w_con.total


def test_evidence_axis_rewards_years_and_proper_nouns() -> None:
    bare = _FakeTranscript(messages=[_msg("pro", "we win because we said so")])
    rich = _FakeTranscript(messages=[_msg(
        "pro",
        "The 2016 Brysbaert study, Getty lawsuit data, and 67% of researchers "
        "show that Picasso, Bach, and AlphaGo demonstrate originality.",
    )])
    bare_pro, _ = score_transcript(bare)
    rich_pro, _ = score_transcript(rich)
    assert rich_pro.evidence > bare_pro.evidence + 4


def test_rebuttal_axis_rewards_opponent_references() -> None:
    no_ref = _FakeTranscript(messages=[
        _msg("pro", "Originality is real. Models create novel outputs."),
    ])
    refs = _FakeTranscript(messages=[
        _msg("pro", "You said models only remix. Your argument ignores "
                    "Move 37; the opponent is wrong. However the data shows..."),
    ])
    pro_a, _ = score_transcript(no_ref)
    pro_b, _ = score_transcript(refs)
    assert pro_b.rebuttal > pro_a.rebuttal


def test_role_fidelity_rewards_own_stance_keywords() -> None:
    on = _FakeTranscript(messages=[_msg(
        "pro", "Originality and creativity prove AI can produce novel art. "
               "It creates, innovates, and shows real originality.",
    )])
    off = _FakeTranscript(messages=[_msg(
        "pro", "The remix interpretation has merit. Training data and "
               "interpolation matter. The convex hull is the real story.",
    )])
    on_pro, _ = score_transcript(on)
    off_pro, _ = score_transcript(off)
    assert on_pro.role_fidelity > off_pro.role_fidelity


def test_setup_directive_and_ack_messages_are_ignored() -> None:
    t = _FakeTranscript(messages=[
        _msg("pro", "AI=ORIGINALITY ready.", role="ack"),
        _msg("pro", "Originality is real.", role="setup_directive"),
        _msg("pro",
             "The 2016 AlphaGo Move 37 demonstrates original creative output.",
             role="argument"),
    ])
    pro, _ = score_transcript(t)
    bare = _FakeTranscript(messages=[_msg(
        "pro",
        "The 2016 AlphaGo Move 37 demonstrates original creative output.",
    )])
    bare_pro, _ = score_transcript(bare)
    assert pro.total == bare_pro.total  # ack/setup didn't leak into the score
