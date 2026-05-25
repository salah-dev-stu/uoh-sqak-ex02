"""Stance-keyword regex drift detector (deterministic, no LLM call).

Per ADR-005 + spec §7.5: drift triggers are concession phrases like
"I concede", "you're right", "fair point" — phrases that signal stance
collapse. Compiled to a single case-insensitive alternation regex.
"""
from __future__ import annotations

import re


class DriftDetector:
    """
    Input:  text (str)
    Output: bool (True = drift detected)
    Setup:  drift_keywords (set[str]) — concession phrases
    """

    def __init__(self, drift_keywords: set[str]) -> None:
        if drift_keywords:
            pattern = "|".join(re.escape(k) for k in drift_keywords)
            self._regex: re.Pattern | None = re.compile(pattern, re.IGNORECASE)
        else:
            self._regex = None

    def is_drift(self, text: str) -> bool:
        if not self._regex:
            return False
        return bool(self._regex.search(text))
