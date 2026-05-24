"""Claude CLI login-mode provider. Shells out to `claude -p ... --output-format json`.

Uses the user's login bundle (zero per-token cost). Requires Claude CLI on PATH.
"""
from __future__ import annotations

import json
import subprocess

from agent_debate.tools.llm_provider import LLMProvider, LLMResponse


class ClaudeLoginProvider(LLMProvider):
    """
    Input:  system (str), user (str), temperature (float), max_tokens (int)
    Output: LLMResponse
    Setup:  claude CLI must be on PATH and authenticated (`claude --login`)
    """

    def complete(
        self, system: str, user: str, temperature: float, max_tokens: int = 1000
    ) -> LLMResponse:
        cmd = [
            "claude", "-p",
            "--append-system-prompt", system,
            "--output-format", "json",
            "--max-turns", "1",
            user,
        ]
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=90, check=False
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"claude CLI failed (exit {result.returncode}): {result.stderr[:500]}"
            )
        data = json.loads(result.stdout)
        usage = data.get("usage", {})
        return LLMResponse(
            text=data.get("result", ""),
            tokens_in=usage.get("input_tokens", 0),
            tokens_out=usage.get("output_tokens", 0),
            finish_reason="stop",
            raw_json=data,
        )
