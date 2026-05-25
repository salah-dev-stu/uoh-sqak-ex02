"""Letter-keyed terminal menu (A/B/C/D/E/X) — keyboard-only operation
per H11 + N8. All actions delegate to DebateSDK.
"""
from __future__ import annotations

from agent_debate.sdk.debate_sdk import DebateSDK


class TerminalMenu:
    """
    Input:  user keystrokes via input()
    Output: int exit code (0 = normal exit, non-zero = error)
    Setup:  sdk (DebateSDK), default_topic (str)
    """

    LEGEND = (
        "=== HW2 Multi-Agent Debate System ===\n"
        "  [A] Start new debate\n"
        "  [B] View last transcript\n"
        "  [C] View spend report\n"
        "  [D] Show health status\n"
        "  [E] Manual Phase-1 mode (see README)\n"
        "  [X] Exit\n"
    )

    def __init__(self, sdk: DebateSDK, default_topic: str = "") -> None:
        self.sdk = sdk
        self.default_topic = default_topic

    def render(self) -> str:
        return self.LEGEND

    def dispatch(self, key: str) -> dict:
        """Map a single letter to an action. Returns {action, result}."""
        key = (key or "").upper().strip()
        if key == "A":
            topic = self.default_topic or "Can AI agents create genuinely original art?"
            transcript = self.sdk.run_debate(topic=topic, n_pings=10)
            return {"action": "start_debate", "result": transcript.debate_id}
        if key == "B":
            t = self.sdk._last_transcript
            return {"action": "view_last", "result": t.to_dict() if t else None}
        if key == "C":
            return {"action": "spend", "result": self.sdk.get_spend_report().__dict__}
        if key == "D":
            return {"action": "health", "result": self.sdk.get_health_status().__dict__}
        if key == "E":
            return {"action": "manual_mode", "result": "See README §Manual exploration"}
        if key == "X":
            return {"action": "exit", "result": 0}
        return {"action": "unknown", "result": None}

    def run(self) -> int:
        print(self.render())
        while True:
            try:
                key = input("Press a letter: ").strip()
            except (EOFError, KeyboardInterrupt):
                return 0
            result = self.dispatch(key)
            print(f"[{result['action']}]")
            if result["action"] == "exit":
                return 0
