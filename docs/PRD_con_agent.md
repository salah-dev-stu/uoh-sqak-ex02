# Per-Mechanism PRD — ConAgent

**Component:** `src/agent_debate/agents/con_agent.py`
**Version:** 1.00
**Parents:** `BaseAgent` → `PartisanAgent` → `ConAgent`
**Skill:** `.claude/skills/con_skill/SKILL.md`
**Stance:** `AI=REMIX_ONLY` — argues AI agents fundamentally remix; nothing is novel

---

## Building-block docstring

```python
class ConAgent(PartisanAgent):
    """
    Input:  message (dict, role ∈ {setup_directive, argument, correction_request, intervention})
    Output: counter (Message)  OR  ack (Message)
    Setup:  STANCE = Stance.REMIX_ONLY  (class constant)
            SKILL_NAME = "con_skill"  (class constant)
            temperature = 0.85
            llm_provider (LLMProvider, injected)
            web_search (WebSearchTool, injected)
            shared_spend (Value), lock (Lock)
    """
```

---

## 1. Theoretical background

The Con agent represents the negative position — arguing AI agents fundamentally **remix** human work; there is no novel creative act, only stochastic recombination of training data.

Tactical playbook from `.claude/skills/con_skill/SKILL.md`:

1. **Stochastic Parrots framing** — Bender, Gebru, McMillan-Major, Mitchell (FAccT 2021): LLMs are sophisticated pattern-completers, not creative minds
2. **Legal evidence** — *NYT v OpenAI* (Dec 2023), *Getty v Stability AI* (Jan 2023) — both allege training-data infringement → AI outputs are derivative
3. **Philosophical** — Searle's Chinese Room; intentionality and "aboutness" are absent in statistical models
4. **Empirical failures** — Gary Marcus's combinatorial-generalization critique; AI fails on out-of-distribution prompts
5. **Recursive rebuttal** — *"calling permutation 'creation' empties the word of meaning"*

Con uses web search for both **own citation** (NYT lawsuit URL, FAccT proceedings) and **opponent fact-check** (verifying Pro's Klingemann auction-price claim, etc.) — the dual purpose mandated by H24.

---

## 2. Functional requirements

Same as `PRD_pro_agent.md` §2 — Con is structurally a mirror of Pro:

| H-gate | Behavior |
|---|---|
| **H1** | Real LLM calls via Gatekeeper |
| **H2** | JSON output via message_schema |
| **H3** | 10 counters per debate (1 per ping) |
| **H7** | Every counter quotes Pro's prior argument |
| **H8** | Distinct Skill (REMIX vs ORIGINALITY) — auto-agreement defense |
| **H24** | Web-search dual purpose: cite own + fact-check Pro |

The opposite-stance pairing (ORIGINALITY vs REMIX_ONLY) is the explicit H8 contradiction guarantee that compensates for ADR-005's same-provider risk.

---

## 3. Performance metrics

Same targets as Pro:

| Metric | Target |
|---|---|
| Per-counter generation latency | ≤ 60 s |
| Citation count per counter | 1–3 |
| Word count per turn | ≤ 250 |
| Drift-correction rate | ≤ 5% |

---

## 4. Alternatives considered

| Alternative | Rejected because |
|---|---|
| Combine Pro + Con into a single "Debater" class with stance parameter | Class diagram readability suffers; rubric §A13 prefers explicit roles |
| Generate counter without requiring opponent-reference | H7 explicit — *"each agent must address opponent's arguments"* |
| Use a lower temperature for Con (more focused criticism) | Symmetric configuration via `agents.json`; the differentiation is in the Skill body, not the temperature |

---

## 5. Test scenarios

Mirror of Pro:

| # | Test | File | Verifies |
|---|---|---|---|
| 1 | Stance regex matches AI=REMIX_ONLY | `test_con_agent.py` | H8 |
| 2 | `enforce_opponent_reference` passes when text quotes Pro | `test_partisan_agent.py` | H7 |
| 3 | LLM call goes through Gatekeeper | `test_con_agent.py` | R3 |
| 4 | Full ConAgent debate ping uses 1-3 citations | `test_full_debate_mocked.py` | H6 + H24 |
| 5 | Con's fact-check query mentions opponent's claim | `test_real_search_dual.py` (E2E) | H24 |

---

## 6. Cross-references

- **Skill:** `.claude/skills/con_skill/SKILL.md` + `references/citations.md`
- **Mirror sibling:** `docs/PRD_pro_agent.md`
- **Shared parent PRD:** none, but `PartisanAgent` shared logic documented in `docs/PLAN.md` §4 class diagram
