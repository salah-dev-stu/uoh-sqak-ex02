# Per-Mechanism PRD — ProAgent

**Component:** `src/agent_debate/agents/pro_agent.py`
**Version:** 1.00
**Parents:** `BaseAgent` → `PartisanAgent` → `ProAgent`
**Skill:** `.claude/skills/pro_skill/SKILL.md`
**Stance:** `AI=ORIGINALITY` — argues AI agents CAN create genuinely original art

---

## Building-block docstring

```python
class ProAgent(PartisanAgent):
    """
    Input:  message (dict, role ∈ {setup_directive, counter, correction_request, intervention})
    Output: argument (Message)  OR  counter (Message)  OR  ack (Message)
    Setup:  STANCE = Stance.ORIGINALITY  (class constant)
            SKILL_NAME = "pro_skill"  (class constant)
            temperature = 0.85  (from agents.json)
            llm_provider (LLMProvider, injected by Orchestrator)
            web_search (WebSearchTool, injected)
            shared_spend (Value), lock (Lock) — for cross-process budget
    """
```

---

## 1. Theoretical background

The Pro agent represents the affirmative position in the debate *"Can AI agents create genuinely original art, or only remix human work?"* — arguing that AI agents **can** create genuinely original art, not merely remix.

Its tactical playbook (laid out in `.claude/skills/pro_skill/SKILL.md`):

1. **Emergence and combinatorial novelty** — neural-net latent spaces reach combinations no human has explored
2. **Auction-house validation** — Christie's sold *Edmond de Belamy* (Obvious, 2018) for $432,500 as art
3. **Practitioner exemplars** — Mario Klingemann's GAN-art, Anna Ridler's curated-data works
4. **Legal framework** — transformative-use doctrine permits derivative works that add meaning
5. **Recursive rebuttal** — *"all human art is also remixing prior work"* — a Levinson-style argument

The Pro is also armed with **web-search dual purpose** (H24): cite its own evidence, AND fact-check Con's claims. When Con cites the Stochastic Parrots paper, Pro can quote a contradicting source from the same literature.

---

## 2. Functional requirements

| H-gate | Behavior | Implementation |
|---|---|---|
| **H1** | All LLM calls are real | `llm_provider.complete()` shells out via Gatekeeper |
| **H2** | All output is JSON | Returns dict that passes `message_schema.validate_message()` |
| **H3** | Emits 10 arguments per debate (1 per ping) | Driven by debate loop in Orchestrator |
| **H7** | Every argument quotes opponent's prior msg | `enforce_opponent_reference(text, prev_con_text)` regex match; sets `references_opponent: bool` |
| **H8** | Distinct Skill from Con (auto-agreement defense) | Different SKILL_NAME + different stance keywords + different system prompt body |
| **H24** | Web search used for citation AND fact-check | `web_search.search(query)` invoked when Skill requires citation backing |
| **N5/H25** | Outcomes deliberately vary across runs | temperature=0.85 introduces variation; no determinism enforced |

---

## 3. Performance metrics

| Metric | Target |
|---|---|
| Per-argument generation latency | ≤ 60 s (LLM-bound; Gatekeeper enforces 90s timeout) |
| Citation count per argument | 1–3 (Skill targets 2) |
| Word count per turn | ≤ 250 (config `max_words_per_turn`) |
| Drift-correction rate | ≤ 5% of turns (i.e., Pro stays in-stance ≥95% of the time) |

---

## 4. Alternatives considered

| Alternative | Rejected because |
|---|---|
| Use a Gemini provider for stronger contradiction (H23) | User chose Claude-only (Prompt #3). H8 risk mitigated via Skill diff + temperature spread (ADR-005). |
| Hardcode arguments instead of LLM call | H1 explicit — real LLM calls only. |
| Skip opponent-reference enforcement | H7 explicit — *"each agent must address opponent's arguments, no parallel monologues."* |
| Single-skill design (let LLM figure out stance from prompt) | H8 — *"agents tend to please; make sure they don't auto-agree."* Skill content is the contradiction guarantee. |

---

## 5. Test scenarios

| # | Test | File | Verifies |
|---|---|---|---|
| 1 | Stance regex matches AI=ORIGINALITY | `test_pro_agent.py` | H8 |
| 2 | `enforce_opponent_reference` passes when text quotes opponent | `test_partisan_agent.py` | H7 |
| 3 | `enforce_opponent_reference` fails on parallel-monologue text | `test_partisan_agent.py` | H7 |
| 4 | `extract_citations` returns URL+snippet pairs | `test_partisan_agent.py` | H6 |
| 5 | LLM call goes through Gatekeeper (mocked) | `test_pro_agent.py` | R3 |
| 6 | Full ProAgent debate ping uses 1-3 citations | `test_full_debate_mocked.py` | H6 + H24 |

---

## 6. Cross-references

- **Skill:** `.claude/skills/pro_skill/SKILL.md` + `references/citations.md`
- **Spec:** §2 (Skills design)
- **PLAN:** §4 class diagram
- **Mirror sibling:** `docs/PRD_con_agent.md`
