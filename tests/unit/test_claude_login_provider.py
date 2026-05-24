"""ClaudeLoginProvider — subprocess shell-out to `claude -p`."""
import json
from unittest.mock import patch

import pytest

from agent_debate.tools.claude_login_provider import ClaudeLoginProvider


def test_completes_returns_llm_response():
    provider = ClaudeLoginProvider()
    fake_stdout = json.dumps({
        "result": "hello world",
        "session_id": "abc",
        "total_cost_usd": 0.0,
        "usage": {"input_tokens": 5, "output_tokens": 3},
    })
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = fake_stdout
        mock_run.return_value.stderr = ""
        resp = provider.complete(system="sys", user="hi", temperature=0.7)
    assert resp.text == "hello world"
    assert resp.tokens_in == 5
    assert resp.tokens_out == 3
    assert resp.finish_reason == "stop"


def test_non_zero_exit_raises():
    provider = ClaudeLoginProvider()
    with patch("subprocess.run") as mock_run:
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = ""
        mock_run.return_value.stderr = "rate limit"
        with pytest.raises(RuntimeError, match="claude CLI failed"):
            provider.complete(system="sys", user="hi", temperature=0.7)
