# Per-Mechanism PRD — JudgeAgent

**Component:** `src/agent_debate/agents/judge_agent.py`
**Version:** 1.00 (per R6)
**Parents:** `BaseAgent` → `JudgeAgent` (no `PartisanAgent` intermediate — Judge has no stance)
**Composed sub-components:** `DriftDetector`, `PCFilter`, `ScoringEngine`
**Authored:** 2026-05-25

---

## Building-block docstring (rubric §A13)

```python
class JudgeAgent(BaseAgent):
    """
    Input:  message (dict, jsonschema-valid Message),
            debate_state (DebateState — internal ping counter + scorecard)
    Output: routed message (Message)  OR
            correction_request (Message)  OR
            intervention (Message)  OR
            verdict (Message)
    Setup:  drift_keywords (set[str]),
            pc_keywords (set[str]),
            scoring_weights (dict[str, float], default: uniform 0.2 per axis),
            llm_provider (LLMProvider),
            topic_blind (bool, default: True),
            no_tie (bool, default: True),
            max_turns_before_verdict (int, default: 20 for 10 pings/side)
    """
```

---

## 1. Theoretical background

The Judge is modeled after a **parliamentary debate moderator** — a role lifted from real-world authority via the N7 pre-flight (`scripts/build_judge_criteria.py`, which web-searches "parliamentary debate scoring", "Lincoln-Douglas format", "Robert's Rules" and persists synthesized criteria to `.claude/skills/judge_skill/references/debate_criteria.md`). The Judge does NOT know the debate topic (H19) — by design — so its evaluation is purely about *form*, not *content*. Lec05 L1449-1469: *"He doesn't need to know football, doesn't need to know diet science… it's actually better he doesn't know — so he's not biased."*

The 5-axis scoring rubric (clarity, evidence, rebuttal, novelty, role_fidelity × 20 each = 100 max) is the Judge's only evaluation surface. Per HW2 spec §8.3 rule 6 + lec05 L1471: persuasiveness wins, not factual correctness. The Judge does not fact-check claims; opponents do that (H17 + H24).

---

## 2. Functional requirements

| H-gate | Behavior | Implementation detail |
|---|---|---|
| **H4** | All Pro↔Con traffic routes through Judge | `route(msg)` puts msg on opponent's `in_queue`; Pro and Con never share queues |
| **H5** | Judge MUST declare a winner; no ties | `declare_winner()` compares totals; on equality, tiebreak by role_fidelity, then evidence, then random |
| **H16** | Judge enforces PC/vulgar-language gate before re-broadcast | `PCFilter.check(text)` runs on every inbound msg; on violation → `intervention` |
| **H18** | Judge issues `setup_directive` to each child at debate start; waits for both `ack` | `issue_setup_directives()` blocks Phase B opening until both acks land |
| **H19** | Judge's system prompt is topic-agnostic | Topic never appears in `judge_skill/SKILL.md`; assertion in `test_judge_agent.py` |
| **H20** | Per-message drift check; on drift → `correction_request` + replay | `DriftDetector.is_drift(text)` runs on every inbound msg; on hit → emit correction_request |
| **H22** | (Indirect) Judge's behavior is reproducible enough to debug but verdicts vary by run (H25) | LLM-based scoring with temperature=0.3 — deterministic enough to test, varied enough to surprise |
| **H24** | (Indirect) Judge does NOT fact-check; web-search is exclusively the debaters' tool | No `WebSearchTool` injected into Judge; only LLM + 3 sub-components |

---

## 3. Performance metrics

| Metric | Target | Measurement |
|---|---|---|
| Per-message validation latency | ≤ 100 ms | DriftDetector regex + PCFilter regex + jsonschema |
| Setup-directive turnaround | ≤ 2 s | From Phase A start to both acks received |
| Per-ping scoring latency (LLM-based) | ≤ 5 s | Gatekeeper-wrapped Claude call |
| Verdict assembly | ≤ 1 s | Aggregation across 20 turns + tiebreak |
| Drift-correction overhead | ≤ 10 s per incident | Send correction_request + await replay |
| Memory footprint | ≤ 100 MB | Bounded by structured logger FIFO |

---

## 4. Alternatives considered

| Alternative | Rejected because |
|---|---|
| LLM-based drift detection (call Claude to evaluate "is this drift?") | Adds 1 extra LLM call per message × 20 turns = significant cost + latency. Stance-keyword regex is deterministic, cheap, debuggable. |
| Judge knows the topic; scores correctness | Lec05 L1449-1469 explicitly forbids — biases the Judge. |
| Judge allows ties when score gap < 2 | H5 explicit — *"no ties allowed, differential 70/80 OK"*. Tiebreak chain handles equal-score edge case. |
| Drift detected only on ≥3 consecutive misses | Lec05 L1182-1184: per-message check is what the lecturer specified. Single-message drift fires immediately. |
| Judge writes the scoring rubric from training-data only | Lec05 L1519-1528: lecturer specifically asked for web-search-derived criteria. N7 originality bonus. |

---

## 5. Test scenarios

| # | Test | File | Verifies |
|---|---|---|---|
| 1 | Setup directives sent + acks received before debate loop | `test_setup_directive_ack.py` | H18 |
| 2 | All Pro/Con messages route via Judge (never direct) | `test_full_debate_mocked.py` | H4 |
| 3 | Drift-triggering text → `correction_request` emitted | `test_drift_correction.py` | H20 |
| 4 | PC-violating text → `intervention` emitted | `test_pc_intervention.py` | H16 |
| 5 | Equal Pro/Con scores → tiebreak resolves; never returns "tie" | `test_no_tie_enforcer.py` | H5 |
| 6 | System prompt assembled without topic words | `test_judge_agent.py::test_topic_blind` | H19 |
| 7 | Topic-blind verdict still produces meaningful differential | `test_full_debate_mocked.py` | H19 + H5 |
| 8 | Lying/factually-wrong claims pass through unchallenged | `test_full_debate_mocked.py::test_lies_not_filtered` | H17 (Judge does not fact-check) |

---

## 6. Cross-references

- **Spec:** `docs/superpowers/specs/2026-05-24-hw2-debate-design.md` §3 (class hierarchy), §4 (data flow), §6 (testing)
- **PLAN:** §4 (class diagram showing JudgeAgent composition), §11 ADR-007 (N7 preflight)
- **Sub-component PRDs:** none — DriftDetector / PCFilter / ScoringEngine are inline classes (≤150 lines each)
- **Skill:** `.claude/skills/judge_skill/SKILL.md` + `references/debate_criteria.md` (generated)
