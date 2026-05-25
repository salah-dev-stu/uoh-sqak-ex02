"""PartisanAgent — abstract parent for ProAgent + ConAgent.

Shared logic:
  * Loads `<skill_dir>/<SKILL_NAME>/SKILL.md`, strips YAML frontmatter
  * Enforces opponent-reference rule (H7): each turn must reuse ≥2 content words
    from the previous opponent message
  * Extracts URL citations with surrounding text snippet
"""
from __future__ import annotations

import re
from pathlib import Path

from agent_debate.agents.base_agent import BaseAgent
from agent_debate.constants import Stance
from agent_debate.tools.web_search import WebSearchTool

_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n(.*)", re.DOTALL)
_URL_RE = re.compile(r"https?://\S+")
_TRAILING_PUNCT = ".,;:!?\"')"
_SNIPPET_RADIUS = 40
_SNIPPET_MAX = 500
_MIN_WORD_LEN = 4
_MIN_OVERLAP = 2


class PartisanAgent(BaseAgent):
    """Abstract Pro/Con parent. Concrete subclasses set STANCE + SKILL_NAME class vars.

    Input:  msg (dict from in_queue)
    Output: argument/counter dict (subclass-defined)
    Setup:  STANCE (Stance), SKILL_NAME (str) — class-level overrides
            web_search (WebSearchTool | None) — optional injected tool
            temperature (float, default 0.85)
    """

    STANCE: Stance
    SKILL_NAME: str
    temperature: float = 0.85

    def __init__(
        self, *args, web_search: WebSearchTool | None = None, **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.web_search = web_search

    def load_skill_body(self) -> str:
        """Read SKILL.md and strip its YAML frontmatter; raw body returned."""
        path = Path(self.skill_dir) / self.SKILL_NAME / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        match = _FRONTMATTER_RE.match(text)
        return match.group(1) if match else text

    @staticmethod
    def _content_words(text: str) -> set[str]:
        return {
            w.lower()
            for w in re.findall(r"[A-Za-z][A-Za-z'-]*", text)
            if len(w) >= _MIN_WORD_LEN
        }

    @staticmethod
    def enforce_opponent_reference(text: str, prev_opponent_text: str) -> bool:
        """H7: returns True iff the two texts share ≥2 content words (≥4 chars)."""
        if not prev_opponent_text or not text:
            return False
        overlap = PartisanAgent._content_words(text) & PartisanAgent._content_words(
            prev_opponent_text
        )
        return len(overlap) >= _MIN_OVERLAP

    @staticmethod
    def extract_citations(text: str) -> list[dict]:
        """Find every URL in `text`; return list of {url, snippet} dicts.

        Snippet is ≤500 chars of surrounding context with newlines collapsed.
        """
        out: list[dict] = []
        for match in _URL_RE.finditer(text):
            raw_url = match.group(0).rstrip(_TRAILING_PUNCT)
            start = max(0, match.start() - _SNIPPET_RADIUS)
            end = min(len(text), match.end() + _SNIPPET_RADIUS)
            snippet = text[start:end].replace("\n", " ")[:_SNIPPET_MAX]
            out.append({"url": raw_url, "snippet": snippet})
        return out

    def handle_message(self, msg: dict) -> dict | None:
        """Default = no-op; concrete subclasses or integration tests override."""
        return None
