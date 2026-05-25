"""PC/vulgar-language filter (H16). Detects offending text and returns
sanitized output where the violating word is asterisked-out.
"""
from __future__ import annotations

import re


class PCFilter:
    """
    Input:  text (str)
    Output: tuple[bool, str | None] — (is_violation, sanitized_or_None)
    Setup:  pc_keywords (set[str])
    """

    def __init__(self, pc_keywords: set[str]) -> None:
        self.pc_keywords = pc_keywords
        if pc_keywords:
            pattern = r"\b(" + "|".join(re.escape(k) for k in pc_keywords) + r")\b"
            self._regex: re.Pattern | None = re.compile(pattern, re.IGNORECASE)
        else:
            self._regex = None

    def check(self, text: str) -> tuple[bool, str | None]:
        if not self._regex:
            return False, None
        match = self._regex.search(text)
        if not match:
            return False, None
        sanitized = self._regex.sub(lambda m: "*" * len(m.group(0)), text)
        return True, sanitized
