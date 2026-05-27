"""Content-derived scorecard for the Judge.

Replaces the Phase-10 placeholder that emitted near-constant scores
(Pro=71/Con=69 every debate). Each axis is now computed from features
of the actual Pro / Con text in the transcript, so different debates
get different scores and the user can tell at a glance whether their
agents made stronger arguments this run.

Axes (each 0-20, summed for /100):

  clarity        avg words/sentence — sweet spot ~14, both extremes lose
  evidence       years, percentages, proper nouns, citation cues
  rebuttal       opponent-referencing cues ("you said", "opponent", ...)
  novelty        type-token ratio (lexical variety)
  role_fidelity  adherence to own stance keywords minus opponent's
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from agent_debate.agents.scoring_engine import Scorecard

_WORD_RE = re.compile(r"\b[\w'-]+\b")
_SENT_SPLIT = re.compile(r"[.!?]+\s+")
_YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
_PCT_RE = re.compile(r"\b\d+(?:\.\d+)?%")
_PROPER_RE = re.compile(r"\b[A-Z][a-z]{2,}\b")

_CITE_CUES = (
    "study", "studies", "research", "data", "evidence", "shows",
    "demonstrates", "reported", "lawsuit", "lawsuits", "court", "ruling",
    "paper", "experiment", "survey", "according",
)
_REBUTTAL_CUES = (
    "opponent", "you said", "you claim", "your argument", "your premise",
    "your example", "the other side", "as you", "rebut", "contrary",
    "however", "but you", "actually", "wrong,", "disagree",
)
_PRO_KEYWORDS = (
    "originality", "original", "create", "creative", "novel", "produce",
    "innovate", "innovation",
)
_CON_KEYWORDS = (
    "remix", "imitate", "imitation", "training data", "interpolate",
    "regurgitate", "convex hull", "derivative",
)


def _texts(messages: Iterable[dict], side: str) -> list[str]:
    skip_roles = {"ack", "setup_directive"}
    return [
        m["text"] for m in messages
        if m.get("from") == side
        and m.get("role") not in skip_roles
        and isinstance(m.get("text"), str)
    ]


def _clarity(texts: list[str]) -> int:
    blob = " ".join(texts).strip()
    if not blob:
        return 10
    sentences = [s for s in _SENT_SPLIT.split(blob) if s.strip()]
    if not sentences:
        return 10
    avg = sum(len(_WORD_RE.findall(s)) for s in sentences) / len(sentences)
    if avg <= 6:
        return 12
    if avg <= 14:
        return 20
    if avg <= 22:
        return int(round(20 - (avg - 14) * 0.9))
    return max(8, int(round(20 - (avg - 14) * 1.2)))


def _evidence(texts: list[str]) -> int:
    blob = " ".join(texts)
    score = 0
    score += 2 * len(_YEAR_RE.findall(blob))
    score += 3 * len(_PCT_RE.findall(blob))
    score += len(_PROPER_RE.findall(blob))
    lower = blob.lower()
    score += sum(lower.count(c) for c in _CITE_CUES)
    return max(0, min(20, score // 2))


def _rebuttal(texts: list[str]) -> int:
    blob = " ".join(t.lower() for t in texts)
    count = sum(blob.count(cue) for cue in _REBUTTAL_CUES)
    return max(0, min(20, count * 2))


def _novelty(texts: list[str]) -> int:
    words = [w.lower() for t in texts for w in _WORD_RE.findall(t)]
    if len(words) < 30:
        return 10
    ttr = len(set(words)) / len(words)
    return max(8, min(20, int(round(ttr * 28))))


def _role_fidelity(
    texts: list[str], own: tuple[str, ...], other: tuple[str, ...]
) -> int:
    blob = " ".join(t.lower() for t in texts)
    own_hits = sum(blob.count(k) for k in own)
    other_hits = sum(blob.count(k) for k in other)
    raw = 12 + own_hits - other_hits + len(texts) // 2
    return max(8, min(20, raw))


def score_transcript(transcript) -> tuple[Scorecard, Scorecard]:
    """Compute (pro_card, con_card) from the actual messages."""
    msgs = getattr(transcript, "messages", []) or []
    pro_texts = _texts(msgs, "pro")
    con_texts = _texts(msgs, "con")
    pro = Scorecard(
        clarity=_clarity(pro_texts),
        evidence=_evidence(pro_texts),
        rebuttal=_rebuttal(pro_texts),
        novelty=_novelty(pro_texts),
        role_fidelity=_role_fidelity(pro_texts, _PRO_KEYWORDS, _CON_KEYWORDS),
    )
    con = Scorecard(
        clarity=_clarity(con_texts),
        evidence=_evidence(con_texts),
        rebuttal=_rebuttal(con_texts),
        novelty=_novelty(con_texts),
        role_fidelity=_role_fidelity(con_texts, _CON_KEYWORDS, _PRO_KEYWORDS),
    )
    return pro, con
