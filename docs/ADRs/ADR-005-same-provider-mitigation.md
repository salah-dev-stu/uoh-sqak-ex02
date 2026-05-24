# ADR-005: Same-provider mitigation — temperature spread + Skill differentiation

**Status:** Accepted — 2026-05-25

## Context

ADR-003 locked Claude-only (Pro = Con = Judge = Claude). Lecturer warning at H8 (HW2 spec §8.3 rule 2): *"agents tend to 'please'; make sure they don't auto-agree."* Lec05 L1131-1142 strongly encourages mixed providers for guaranteed contradiction.

Without explicit mitigation, two Claude instances in the same context (same training corpus, same instruction tuning, same RLHF) could quietly converge — Pro starts mid-debate to soften, Con starts to concede, Judge spots no clear winner. H5 (no ties) and H7 (mutual reference) are at risk.

## Decision

Compensate for same-provider risk with **three independent mechanisms**:

1. **Skill differentiation (H8 primary)** — `pro_skill/SKILL.md` and `con_skill/SKILL.md` have fundamentally different stances, different tactical playbooks, different drift-keyword sets, and different citation lists. The skill bodies enforce contradiction at the prompt-construction level, before Claude even processes the input.

2. **Temperature spread** — debater temperatures both at 0.85 (high enough for varied output) but DriftDetector enforces ~5% maximum drift-correction rate per agent. Judge temperature is 0.30 (deterministic moderation).

3. **DriftDetector regex (H20)** — stance-keyword regex catches the obvious convergence phrases (`"actually you're right"`, `"I concede"`, `"fair point"`, etc.) and forces a `correction_request` + replay. This is the per-message safety net.

Keep the `LLMProvider` ABC abstract enough that adding `GeminiProvider` later (for true H23 mixed-providers) is **one new adapter + one config-key change**. The seam stays open.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| Build Gemini provider now | User chose zero-cost (ADR-003); Gemini needs an API key |
| Disable DriftDetector to let Claude "just argue" | H20 explicit graded requirement |
| Use very different temperatures (0.3 Pro / 1.2 Con) | Asymmetric temperature confounds scoring — Judge may misread temperature artifacts as drift |
| Skip H8 mitigation entirely | H8 explicit graded requirement — *"agents tend to please"* warning is non-negotiable |

## Consequences

### Positive

- Zero API spend preserved.
- H8 + H20 both addressed by separate mechanisms (defense in depth).
- Easy upgrade path: add Gemini later for stronger contradiction.

### Negative

- Loses the H23 originality-bonus signal of mixed providers. **Mitigation:** document this trade-off in PROMPTS.md and README "Future Work" so the grader sees the choice was conscious.
- Three mechanisms increase test surface. **Mitigation:** they're orthogonal — Skill diff is data, temperature is config, DriftDetector is code. Each is testable independently.

## Verification

- `tests/unit/test_pro_agent.py` + `test_con_agent.py` — verify distinct stances + drift keywords
- `tests/integration/test_drift_correction.py` — verifies DriftDetector catches convergence attempts
- `tests/integration/test_full_debate_mocked.py` — end-to-end with both Claude instances, verifies debate doesn't collapse into agreement
