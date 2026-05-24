# ADR-003: LLM access via `claude -p` shell-out (not the Anthropic SDK)

**Status:** Accepted — 2026-05-25 (locked at Prompt #3)

## Context

Three options for invoking Claude:

1. **Claude CLI in login mode** — `claude -p ...` shells out; user is already authenticated via `claude --login`; costs ZERO per-token because the login bundle covers it.
2. **Anthropic Python SDK with API key** — pure Python; pay per token; needs `ANTHROPIC_API_KEY` in `.env`.
3. **GLM via Z.AI** — OpenAI-compatible API; cheap-but-comparable LLM; needs another key.

The user explicitly chose option 1 at Prompt #3 — zero API spend matters for the HW2 budget. The trade-off is grader-friction: the grading machine must have Claude CLI installed and authenticated.

## Decision

Use **option 1** — `claude -p` shell-out via `subprocess.run()` with:

```
claude -p \
  --append-system-prompt "$(cat .claude/skills/<role>_skill/SKILL.md)" \
  --output-format json \
  --max-turns 1 \
  "<user prompt>"
```

`--output-format json` makes the response structured; `--max-turns 1` prevents Claude from running multi-turn agentic loops inside a single LLM call.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| Anthropic SDK with API key (option 2) | Pay-per-token. Not chosen, but kept as a future-work seam — `LLMProvider` ABC means swapping in `AnthropicAPIProvider` is one new file + one config-key change. |
| GLM via Z.AI (option 3) | Cheaper than Claude API but not free; less proven for nuanced legal/philosophical argument; grader unfamiliar. |
| Mixed providers (Pro=Claude, Con=Gemini — H23 bonus) | Strongest H8 contradiction guarantee, but user chose zero-cost. **Mitigation:** ADR-005 (Skill differentiation + temperature spread) covers the same-provider risk. |

## Consequences

### Positive

- Zero API spend (login bundle covers all calls).
- No `ANTHROPIC_API_KEY` in `.env` — one less secret to manage.
- Reuses user's existing Claude authentication.

### Negative

- Grader's machine must have Claude CLI installed + authenticated. **Mitigation:** README install section explicit about this; grader feedback report should confirm Claude CLI is part of the standard course toolchain.
- Subprocess shell-out adds ~50 ms overhead per call. Negligible at our call rate.

## Verification

- `tests/unit/test_claude_login_provider.py` — mocks subprocess.run, validates JSON parsing
- `tests/e2e/test_real_debate_5_pings.py` — exercises the live `claude -p` path
