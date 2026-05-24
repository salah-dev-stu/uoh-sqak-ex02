"""Generic factory registry for plugin patterns."""
import pytest

from agent_debate.tools.registry import Registry


def test_register_and_retrieve():
    reg: Registry[str] = Registry()
    reg.register("foo", "bar")
    assert reg.get("foo") == "bar"


def test_unknown_key_raises():
    reg: Registry[str] = Registry()
    with pytest.raises(KeyError, match="unknown"):
        reg.get("missing")


def test_duplicate_registration_replaces():
    reg: Registry[str] = Registry()
    reg.register("foo", "v1")
    reg.register("foo", "v2")
    assert reg.get("foo") == "v2"


def test_keys_lists_registered():
    reg: Registry[int] = Registry()
    reg.register("a", 1)
    reg.register("b", 2)
    assert set(reg.keys()) == {"a", "b"}
