"""DriftDetector — deterministic stance-keyword regex drift detector (ADR-005)."""
from __future__ import annotations

from agent_debate.agents.drift_detector import DriftDetector


def _make_detector() -> DriftDetector:
    return DriftDetector(
        {"i concede", "you're right", "fair point", "i agree with you"}
    )


def test_detects_concession_phrase():
    detector = _make_detector()
    assert detector.is_drift("Well, I concede on that point.") is True


def test_passes_normal_argument():
    detector = _make_detector()
    assert (
        detector.is_drift(
            "The originality of latent space combinations refutes that view."
        )
        is False
    )


def test_case_insensitive_match():
    detector = _make_detector()
    assert detector.is_drift("Fine, FAIR POINT — but still wrong overall.") is True


def test_empty_keywords_returns_false():
    detector = DriftDetector(set())
    assert detector.is_drift("I concede everything you said.") is False
