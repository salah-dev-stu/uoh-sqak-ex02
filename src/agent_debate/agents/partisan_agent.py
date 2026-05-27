"""PartisanAgent — abstract parent for ProAgent + ConAgent.

Shared logic:
  * Loads `<skill_dir>/<SKILL_NAME>/SKILL.md`, strips YAML frontmatter
  * Enforces opponent-reference rule (H7): each turn must reuse ≥2 content words
    from the previous opponent message
  * Extracts URL citations with surrounding text snippet
  * `handle_message` produces ack on setup_directive, argument/counter on cues
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path

from agent_debate.agents.base_agent import BaseAgent
from agent_debate.constants import SCHEMA_VERSION, AgentRole, MessageRole, Stance
from agent_debate.tools.web_search import WebSearchTool

_FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n(.*)", re.DOTALL)
_URL_RE = re.compile(r"https?://\S+")
_TRAILING_PUNCT = ".,;:!?\"')"
_SNIPPET_RADIUS = 40
_SNIPPET_MAX = 500
_MIN_WORD_LEN = 4
_MIN_OVERLAP = 2
_FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def _unwrap_text(raw: str) -> str:
    """Extract `text` field if Claude wrapped its reply in JSON; else return as-is."""
    raw = (raw or "").strip()
    if not raw:
        return raw
    m = _FENCED_JSON_RE.search(raw)
    candidate = m.group(1) if m else (raw if raw.startswith("{") else None)
    if candidate is not None:
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict) and isinstance(obj.get("text"), str):
                return obj["text"].strip()
        except json.JSONDecodeError:
            pass
    return raw


class PartisanAgent(BaseAgent):
    """Abstract Pro/Con parent. Subclasses set STANCE + SKILL_NAME class vars.

    Input:  msg (dict from in_queue)
    Output: argument/counter dict
    Setup:  STANCE, SKILL_NAME, optional web_search, temperature=0.85
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
        """Find every URL in `text`; return list of {url, snippet} dicts (≤500 chars)."""
        out: list[dict] = []
        for match in _URL_RE.finditer(text):
            raw_url = match.group(0).rstrip(_TRAILING_PUNCT)
            start = max(0, match.start() - _SNIPPET_RADIUS)
            end = min(len(text), match.end() + _SNIPPET_RADIUS)
            snippet = text[start:end].replace("\n", " ")[:_SNIPPET_MAX]
            out.append({"url": raw_url, "snippet": snippet})
        return out

    def _envelope(self, to_role: str, role: str, text: str, ping_index: int) -> dict:
        """Build a schema-valid wire message originating from this agent."""
        return {
            "msg_id": str(uuid.uuid4()),
            "schema_version": SCHEMA_VERSION,
            "from": self.role.value if hasattr(self.role, "value") else str(self.role),
            "to": to_role,
            "role": role,
            "ping_index": ping_index,
            "text": text,
            "timestamp": datetime.now(tz=UTC).isoformat(),
        }

    def _llm_text(self, msg: dict) -> str:
        """Drive one LLM call shaped by this agent's stance + the inbound cue."""
        raw = _unwrap_text(msg.get("text", "") or "")
        is_opponent_relay = msg.get("role") == MessageRole.COUNTER.value
        user = (
            f"The OPPONENT just said:\n\n{raw}\n\n"
            f"Now write YOUR OWN counter as the {self.role.value.upper()}"
            " debater. Do NOT repeat their text."
        ) if is_opponent_relay else raw
        response = self.llm_provider.complete(
            system=self._build_system_prompt(), user=user,
            temperature=self.temperature, max_tokens=400,
        )
        return _unwrap_text(response.text)

    def _build_system_prompt(self) -> str:
        """Stance-anchored prompt that forces real arguments (no JSON, no meta)."""
        return (
            f"You are the {self.role.value.upper()} debater. Stance: {self.STANCE.value}.\n"
            "Output ONLY your own argument as plain prose, 150-300 words. NEVER"
            " reproduce or summarize the opponent's text — write a NEW position"
            " of your own. No JSON, no code fences, no markdown (no asterisks,"
            " underscores, hashes, backticks), no meta-commentary about the"
            " wire protocol. If no opponent message is present, open with your"
            " strongest standalone case; otherwise reference ONE short phrase"
            " from them (≤8 words, in quotes) and then make your own case."
        )

    def handle_message(self, msg: dict) -> dict | None:
        """Produce ack on setup_directive; argument/counter for cues from Judge."""
        role_in = msg.get("role")
        ping_index = int(msg.get("ping_index", 0) or 0)
        if role_in == MessageRole.SETUP_DIRECTIVE.value:
            return self._envelope(
                to_role=AgentRole.JUDGE.value,
                role=MessageRole.ACK.value,
                text=f"{self.STANCE.value} ready.",
                ping_index=ping_index,
            )
        if role_in in (MessageRole.ARGUMENT.value, MessageRole.COUNTER.value,
                       MessageRole.CORRECTION_REQUEST.value, MessageRole.INTERVENTION.value):
            text = self._llm_text(msg)
            out_role = (MessageRole.ARGUMENT.value if ping_index <= 1
                        else MessageRole.COUNTER.value)
            return self._envelope(
                to_role=AgentRole.JUDGE.value,
                role=out_role,
                text=text,
                ping_index=ping_index,
            )
        return None
