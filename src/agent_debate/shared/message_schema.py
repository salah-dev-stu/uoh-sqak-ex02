"""Message dataclass + jsonschema validator for the inter-agent JSON wire protocol."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema

_SCHEMA_PATH = (
    Path(__file__).parent.parent.parent.parent
    / "config" / "schemas" / "message-1.00.json"
)
_SCHEMA = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_message(msg: dict) -> None:
    jsonschema.validate(msg, _SCHEMA)


@dataclass(frozen=True)
class Message:
    """Immutable wire-protocol message. Use `Message.from_dict` for parsing."""

    msg_id: str
    schema_version: str
    from_role: str  # 'from' is a Python keyword; renamed
    to_role: str
    role: str
    ping_index: int
    text: str
    timestamp: str
    references_opponent: bool | None = None
    citations: list[dict] = field(default_factory=list)
    scoring: dict | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None

    @classmethod
    def from_dict(cls, d: dict) -> Message:
        validate_message(d)
        return cls(
            msg_id=d["msg_id"],
            schema_version=d["schema_version"],
            from_role=d["from"],
            to_role=d["to"],
            role=d["role"],
            ping_index=d["ping_index"],
            text=d["text"],
            timestamp=d["timestamp"],
            references_opponent=d.get("references_opponent"),
            citations=d.get("citations", []),
            scoring=d.get("scoring"),
            tokens_in=d.get("tokens_in"),
            tokens_out=d.get("tokens_out"),
        )

    def to_dict(self) -> dict:
        out: dict = {
            "msg_id": self.msg_id,
            "schema_version": self.schema_version,
            "from": self.from_role,
            "to": self.to_role,
            "role": self.role,
            "ping_index": self.ping_index,
            "text": self.text,
            "timestamp": self.timestamp,
        }
        if self.references_opponent is not None:
            out["references_opponent"] = self.references_opponent
        if self.citations:
            out["citations"] = self.citations
        if self.scoring is not None:
            out["scoring"] = self.scoring
        if self.tokens_in is not None:
            out["tokens_in"] = self.tokens_in
        if self.tokens_out is not None:
            out["tokens_out"] = self.tokens_out
        return out
