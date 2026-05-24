"""Message dataclass + jsonschema validator for inter-agent JSON wire protocol."""
import uuid
from datetime import UTC, datetime

import jsonschema
import pytest

from agent_debate.shared.message_schema import Message, validate_message


def _valid(**overrides) -> dict:
    base = {
        "msg_id": str(uuid.uuid4()),
        "schema_version": "1.00",
        "from": "pro",
        "to": "judge",
        "role": "argument",
        "ping_index": 1,
        "text": "Hello.",
        "timestamp": datetime.now(tz=UTC).isoformat(),
    }
    base.update(overrides)
    return base


def test_valid_argument_passes():
    validate_message(_valid())  # should not raise


def test_invalid_role_fails():
    with pytest.raises(jsonschema.ValidationError):
        validate_message(_valid(role="nonsense"))


def test_missing_from_fails():
    msg = _valid()
    del msg["from"]
    with pytest.raises(jsonschema.ValidationError):
        validate_message(msg)


def test_message_dataclass_roundtrip():
    raw = _valid()
    msg = Message.from_dict(raw)
    assert msg.from_role == "pro"
    assert msg.to_role == "judge"
    assert msg.to_dict() == raw


def test_message_with_optional_fields():
    raw = _valid(references_opponent=True, citations=[
        {"url": "https://x.test/a", "snippet": "snippet"}
    ], tokens_in=100, tokens_out=50)
    msg = Message.from_dict(raw)
    assert msg.references_opponent is True
    assert msg.citations == [{"url": "https://x.test/a", "snippet": "snippet"}]
    assert msg.tokens_in == 100
