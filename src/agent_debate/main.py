"""CLI entry point — `uv run agent-debate` launches the terminal menu.

Composition root: load config → build orchestrator → wrap in DebateSDK →
hand to TerminalMenu. No business logic here (rubric R1).
"""
from __future__ import annotations

import sys
from pathlib import Path

from agent_debate.menu.tui import TerminalMenu
from agent_debate.orchestration.lifecycle_registry import LifecycleRegistry
from agent_debate.orchestration.orchestrator import DebateOrchestrator
from agent_debate.sdk.debate_sdk import DebateSDK
from agent_debate.shared.config import load_config
from agent_debate.tools.claude_login_provider import ClaudeLoginProvider


def make_llm_provider() -> ClaudeLoginProvider:
    return ClaudeLoginProvider()


def main() -> int:
    try:
        config = load_config(Path("config"))
    except FileNotFoundError as exc:
        print(f"Config not found: {exc}", file=sys.stderr)
        return 2
    orchestrator = DebateOrchestrator(
        llm_provider_factory=make_llm_provider,
        lifecycle=LifecycleRegistry(),
        transcript_dir=Path(config.setup["transcript_dir"]),
        gatekeeper_config=config.rate_limits["services"]["claude_login"],
    )
    sdk = DebateSDK(
        orchestrator=orchestrator,
        transcript_dir=Path(config.setup["transcript_dir"]),
        budget_cap=config.rate_limits["services"]["claude_login"]["tokens_per_debate"],
    )
    menu = TerminalMenu(sdk=sdk, default_topic=config.setup["debate_topic"])
    return menu.run()


if __name__ == "__main__":
    sys.exit(main())
