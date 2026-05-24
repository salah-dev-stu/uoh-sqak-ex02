# ADR-007: Judge scoring criteria sourced via web-search pre-flight (N7)

**Status:** Accepted — 2026-05-25

## Context

Lec05 L1519-1528 verbatim:

> *"מה המומחיות של האבא? מומחה לדיבייטים. תגיד לג'מנאי: תגדיר לי, תחפש בעולם מי המומחה מספר אחת לדיבייטים, ומה הקריטריונים, ואז תיקח את הקריטריונים האלה ותיתני את זה כסיספרומפט לאבא."*
>
> *"The Father's expertise = debate expert. Tell Gemini: 'search the world for who's the #1 debate expert and what criteria he sets,' then take those criteria and give them as system prompt to the Father."*

This is the **N7 originality bonus signal** — the lecturer specifically asked for the Judge's scoring rubric to be **sourced from real-world authority** via web search, not invented from training data.

## Decision

Implement a pre-flight script `scripts/build_judge_criteria.py` that:

1. Web-searches DDG for: `"parliamentary debate scoring criteria"`, `"Lincoln-Douglas debate format judging criteria"`, `"Robert's Rules of Order debate procedure"`, `"World Schools Debate Championship judging axes"`.
2. Synthesizes the results into `.claude/skills/judge_skill/references/debate_criteria.md`.
3. The Judge's `SKILL.md` body references this file: *"For your full scoring rubric, see `references/debate_criteria.md`."*
4. The script is **idempotent** — checks cache; skips if `debate_criteria.md` already exists.
5. Runs once at project setup OR auto-runs from `main.py` if cache miss.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| Hardcoded scoring rubric in SKILL.md | Loses N7 originality bonus signal |
| Live-search criteria at every debate start | Wasteful — criteria don't change between runs |
| Use Anthropic's own scoring guidance | Lecturer explicitly asked for *real-world* debate-authority criteria, not LLM-internal |
| Skip the references file; bake into Judge's system prompt directly | Larger system prompt = higher token cost per LLM call; references file is loaded by the Judge on demand |

## Consequences

### Positive

- Earns N7 originality bonus.
- Judge's scoring rubric is **traceable** — every axis is grounded in a real-world citation, visible in the audit trail.
- Document is reusable (final-project Judge can reload same file).

### Negative

- Requires DDG access on first run. **Mitigation:** cache hit after first run; the script also has a curated fallback embedded.
- Synthesizing search results into a usable rubric requires some prompt engineering. **Mitigation:** the script does light templating, not heavy LLM-call processing.

## Verification

- `scripts/build_judge_criteria.py` runs successfully once on a fresh machine
- `.claude/skills/judge_skill/references/debate_criteria.md` exists and is non-empty
- `tests/unit/test_judge_agent.py::test_loads_criteria_from_reference_file` — verifies the wiring
- README `docs/PROMPTS.md` Prompt #N (during execution) documents the queries used and the synthesis approach
