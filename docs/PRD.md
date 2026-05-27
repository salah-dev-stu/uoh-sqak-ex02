# Product Requirements Document — HW2 Multi-Agent Debate System

> **Authored using Dr. Segal's canonical Vibe Coding prompt** (lec01 L1230-1236):
> *"Your mission is to create the following PRD document based on the following description"*
> — followed by the bullets from `docs/superpowers/specs/2026-05-24-hw2-debate-design.md` §0.

**Project:** HW2 — Multi-Agent Debate System
**Course:** 203.3763 — *Orchestration of AI Agents* (אורקסטרציה של סוכני AI), Spring 2026
**Pair:** Salah Qadah (323039974) + Andalus Kalash (211435797). Group code: `uoh-sqak`.
**Lecturer:** Dr. Yoram Reuven Segal — `rmisegal@gmail.com`
**Authored:** 2026-05-25 via Claude Opus 4.7 (audit trail: `docs/PROMPTS.md`)
**Version:** 1.00 (rubric R6 — starts at 1.00, +0.01 per change)
**Status:** AWAITING APPROVAL — rubric §2.5 step 1 gate

---

## 1. Background

### 1.1 Course thesis (cite verbatim — rubric §A2 + §A24)

> "מתכנת העובד עם סוכני AI ומשתמש בשיטת קידוד בהנחיה יכול לייצר בפרק זמן נתון פי 16 יותר שורות קוד איכותיות בהשוואה לכתיבה ידנית ללא AI."
>
> *"A developer working with AI agents using Vibe Coding can produce 16× more quality code lines per time unit vs hand-writing without AI."*
>
> "הכלל הראשון והחשוב ביותר: כדי לנצל את מלוא הפוטנציאל של סוכני AI, חובה להגדיר דרישות ברורות ומפורטות."
>
> *"The first and most important rule: to unlock AI agents' full potential, you MUST define clear and detailed requirements."*

And the central thesis of HW2 specifically (HW2 spec §10):

> "המעבר מ-Prompt Engineering ל-Context Engineering הוא המעבר שהופך אתכם ממשתמשי ChatGPT למהנדסי סוכנים. אורקסטרציה של סוכנים, ניהול מודע של חלון ההקשר, ועיצוב היררכיה ברורה של Command, Skill, Agent, Subagent — אלו הכלים שיבדילו את התוצר שלכם מתוצר חובבני."
>
> *"The transition from Prompt Engineering to Context Engineering is what turns you from ChatGPT users into agent engineers. Agent orchestration, conscious context-window management, and clear hierarchy design of Command, Skill, Agent, Subagent — these are the tools that distinguish your product from an amateur one."*

This PRD answers Dr. Segal's first-and-most-important-rule for THIS project.

### 1.2 HW1 calibration (what to recover)

HW1 final grade: **85.54** (75.54 pre-bonus + 10 automatic compensation). Below the user's course target of 92. The HW1 feedback report (`../hw1/feedback/Detailed_Feedback_Report.pdf`) identifies four transferable weak spots:

| HW1 weak spot | HW2 remediation |
|---|---|
| Project Planning | Rigorous `docs/PRD.md` (this file) + `docs/PLAN.md` (C4 + UML + class diagram + 7 ADRs + ISO/IEC 25010) + 9 per-mechanism PRDs |
| Configuration & Security | Five versioned JSON configs + `.env-example` only + Gatekeeper as the spend/rate enforcement layer + grader can `git clone && uv sync && uv run agent-debate` on a fresh machine |
| Extensibility | Named `LLMProvider`/`SearchProvider` ABCs + factory `Registry` + 8 explicitly-named `LifecycleRegistry` hooks (rubric §A9) |
| Quality Standards | `.pre-commit-config.yaml` (ruff + 150-line enforcer + unit tests) + `.github/workflows/ci.yml` (ruff + coverage ≥85% + line enforcer) — HW1 had none of these |

### 1.3 Brainstorming provenance

This PRD is **derived from** the brainstorming spec `docs/superpowers/specs/2026-05-24-hw2-debate-design.md` (locked decisions §0, architecture §1, skills §2, components §3, data flow §4, error handling §5, testing strategy §6, self-review §7). 36 locked decisions are logged in `docs/PROMPTS.md`. This PRD is not a re-design — it is the **requirements distillation** of an already-approved design.

---

## 2. Goals & Key Performance Indicators

### 2.1 Primary goal

Build a **three-process Python debate system** where Pro and Con agents argue *"Can AI agents create genuinely original art, or only remix human work?"* through a JSON-IPC bus moderated by a topic-blind Judge, using real Claude calls and real DuckDuckGo web-search, with watchdog supervision and a letter-keyed terminal UI — meeting all 25 HW2 audit gates (H1–H25) and the 13 cross-cutting rubric gates (R1–R13).

### 2.2 KPIs

| KPI | Target | How measured |
|---|---|---|
| **Final grade** | ≥ 90 | Lecturer's grading agent (post-bonus) |
| **Self-grade declared** | 85 | Honest calibration; HW1 over-claimed by 4.5 (90 → 85.54) |
| **Coverage** | ≥ 85% statement+branch | `uv run pytest --cov --cov-fail-under=85` |
| **Ruff** | 0 errors | `uv run ruff check src tests` |
| **150-line rule** | 0 violations | `uv run python scripts/check_file_lines.py` |
| **Commits on `main`** | ≥ 50 with meaningful messages | `git log --oneline` |
| **H-gates passed** | 25/25 | Manual audit against integration tests |
| **TODO completion** | 100% checked | `[x]` markers in `docs/TODO.md` |
| **Repo accessibility** | PUBLIC | `gh repo view <url> --json visibility` |
| **README ≥ 200 lines** | Full user manual + session-1 dialogue | Line count + section audit |

---

## 3. Stakeholders

- **Primary user:** Dr. Segal's grading agent — an LLM that auto-reads the repo, runs the test suite, inspects git history, and renders a qualitative letter (no numeric breakdown — syllabus 4.2). Must work with zero hand-holding on a fresh machine.
- **Pair members:** Salah Qadah (lead, this repo's primary author), Andalus Kalash (collaborator on repo; co-submits same PDF on Moodle).
- **Lecturer:** Dr. Yoram Segal (`rmisegal@gmail.com`) — reads sample transcripts, judges the *form* of the debate, expects originality bonus signals (mixed providers / multi-skill / N7 web-search-built-Judge / non-typical topic).
- **Future user (final project):** the HW2 Judge/Pro/Con abstraction will be reused in the syllabus week-11 final project ("League of 20 Questions" tournament). Design with this in mind.

---

## 4. Functional Requirements

Each requirement is one of the 25 HW2 audit gates from `RULES.md` (with source citations to spec / lecture / rubric). Acceptance is verified by the integration tests in `tests/integration/` (mapped in `docs/PLAN.md`).

### 4.1 Core debate behaviour

| ID | Requirement | Source | Verified by |
|---|---|---|---|
| **H1** | All LLM calls are real (Claude CLI shell-out); no faked Python-generated dialogue | spec §8.4 | `test_full_debate_mocked.py` asserts `MockLLMProvider` only in tests; production wires `ClaudeLoginProvider` |
| **H2** | All inter-agent messages serialized as JSON, jsonschema-validated on both send and recv | spec §8.3 rule 8 | `test_message_schema.py` + send/recv validators in `BaseAgent` |
| **H3** | ≥10 pings per side (or 5 with explicit README budget note) | spec §8.3 rule 3 | `config/debate_rules.json` `pings_per_side=10`; `test_full_debate_mocked.py` asserts |
| **H4** | All traffic through Judge — Pro and Con never communicate directly | spec §8.3 rule 7 | `test_full_debate_mocked.py` asserts no message has `from=pro,to=con` or `from=con,to=pro` |
| **H5** | Judge declares a winner; no ties allowed; differential scoring (70/80) permitted | spec §8.3 rule 6 + §9 | `test_no_tie_enforcer.py` asserts `Scorecard.pro.total != Scorecard.con.total`; `ScoringEngine.declare_winner()` raises on tie |
| **H6** | Internet search tool integrated and used during debate; absent web-search = automatic point loss | lec05 L1233-1239 | `tools/web_search.py` + integration tests assert citations populated |
| **H7** | Mutual reference — every turn quotes at least one phrase from opponent's prior message | spec §8.3 rule 4 + lec05 L1576 | `references_opponent` schema field + Judge's `DriftDetector` regex re-verify |
| **H8** | Pro and Con use distinct `Skill` definitions to prevent auto-agreement | spec §8.3 rule 2 | `.claude/skills/pro_skill/` ≠ `.claude/skills/con_skill/`; stance regex differs |

### 4.2 Reliability

| ID | Requirement | Source | Verified by |
|---|---|---|---|
| **H9** | Watchdog with KPI heartbeat — kill+restart child if stuck | HW2 spec §8.6 + lec05 L1302-1314 | `test_chaos_child_kill.py` + `test_chaos_child_hang.py` |
| **H10** | Every LLM call has an explicit timeout | HW2 spec §8.6 | `Gatekeeper.execute()` wraps with `signal.alarm()`; unit test in `test_gatekeeper.py` |
| **H11** | Terminal menu keyboard-operable; GUI optional with screenshots | HW2 spec §8.6 | `menu/tui.py` letter-keyed (A/B/C/D/E/X); `test_tui.py` |

### 4.3 Submission discipline

| ID | Requirement | Source | Verified by |
|---|---|---|---|
| **H12** | Hebrew or English only; no Arabic in debate output | HW2 spec §8.7 | Skill bodies enforce; sample transcript inspected |
| **H13** | Pair submission only (Salah + Andalus) | HW2 spec §8.7 | Submission PDF |
| **H14** | Repo PUBLIC or explicitly shared with `rmisegal@gmail.com`. Inaccessible = automatic zero, no resubmit | lec05 L1641-1652 | Incognito verification step in Task 12.4 |
| **H15** | Each pair member uploads same-repo-link PDF separately on Moodle | HW2 spec §8.7 | Moodle assignment id=264177 |

### 4.4 Judge discipline (added from lec05 — not in spec PDF)

| ID | Requirement | Source | Verified by |
|---|---|---|---|
| **H16** | Judge enforces PC/respectful-language gate; vulgar messages sanitized or rejected before re-broadcast | lec05 L1553-1559 | `pc_filter.py` + `test_pc_intervention.py` |
| **H17** | Skills are PROJECT-LOCAL under `.claude/skills/`, never global `~/.claude/skills/` | lec05 L1330-1332 | Repo layout audit |
| **H18** | Judge issues `setup_directive` messages to each child at debate start (stance, rules, expected JSON format); waits for `ack` before debate loop | lec05 L1213-1221, L1411-1433 | `test_setup_directive_ack.py` |
| **H19** | Judge's system prompt is **topic-agnostic** — does not contain debate topic words | lec05 L1449-1469 | `judge_agent.py` assembles system prompt sans topic; unit test asserts |
| **H20** | Per-message drift check — Judge verifies role-faithfulness on every message; on violation issues `correction_request` + replay | lec05 L1182-1184 | `drift_detector.py` (stance-keyword regex) + `test_drift_correction.py` |

### 4.5 Originality and resilience

| ID | Requirement | Source | Verified by |
|---|---|---|---|
| **H21** | Watchdog with heartbeat — kill+restart on stuck process with backoff | lec05 L1302-1314 | `watchdog.py` + chaos tests |
| **H22** | README includes Phase 1 manual-debate screenshots as evidence | lec05 L1896-1909 | `assets/manual-phase1-*.png` + README section |
| **H23** | Mixed LLM providers encouraged (not built — user chose Claude-only) | lec05 L1131-1142 | `LLMProvider` abstract leaves Gemini swap open (Future Work in PLAN.md) |
| **H24** | Web search serves DUAL purpose — own citations AND fact-check opponent's lies | lec05 L1483-1491 | Skill bodies authorize both uses; sample transcript shows |
| **H25** | Outcome non-reproducibility is DESIRED — different runs different winners | lec05 L1581-1597 | README states this explicitly |

### 4.6 Cross-cutting rubric gates (R1–R13)

| ID | Requirement | Source |
|---|---|---|
| **R1** | All business logic flows through SDK layer (`DebateSDK` is the sole entry point) | Rubric Table 5 |
| **R2** | OOP — no code duplication; class diagram mandatory (HW2 spec §8.6) | Rubric Table 5 |
| **R3** | All external API calls (LLM + search) flow through `ApiGatekeeper` | Rubric Table 5 |
| **R4** | Rate limits + token budget in JSON config, never in code | Rubric Table 5 |
| **R5** | Wave management — FIFO queue with backpressure, no crashes | Rubric Table 5 |
| **R6** | Versioning starts at 1.00 in both code and config; +0.01 per change | Rubric Table 5 |
| **R7** | TDD — red/green/refactor; tests written before/with code | Rubric Table 5 |
| **R8** | ≤150 lines per `.py` file (logical lines, excluding comments and blanks) | Rubric Table 5 |
| **R9** | `ruff check` returns 0 errors | Rubric Table 5 |
| **R10** | `pytest --cov` ≥ 85% | Rubric Table 5 |
| **R11** | 0 hardcoded values in source; everything via config | Rubric Table 5 |
| **R12** | 0 secrets in code; `.env-example` only, `.env` git-ignored | Rubric Table 5 |
| **R13** | `uv` is the only package manager; no `pip` / `python -m` / `venv` / `virtualenv` | Rubric Table 5 |

---

## 5. Non-Functional Requirements — ISO/IEC 25010 (rubric §A10 + §13.1)

Verbatim Hebrew/English term pairs as required by rubric pattern-matching. Each dimension names the concrete HW2 feature satisfying it.

### 5.1 התאמה פונקציונלית / Functional Suitability — שלמות, נכונות, התאמה

All 25 H-gates implemented and verified by integration tests. Judge declares winner with differential scoring (H5). All mandatory rules from HW2 spec §8.3 honored.

### 5.2 יעילות ביצועים / Performance Efficiency — זמני תגובה, ניצול משאבים, יכולת

Per-LLM-call timeout 90 seconds (`config/rate_limits.json`). Token budget capped at 200,000 per debate with warn at 75% / hard refuse at 95% (rubric §A8). Heartbeat polling at 2-second interval — bounded memory + bounded CPU. Three OS processes — true parallelism, not GIL-blocked.

### 5.3 תאימות / Compatibility — יכולת פעולה הדדית ודו-קיום

macOS / Linux / WSL — `multiprocessing.Queue` + `subprocess` are cross-platform. LLM provider swappable via `LLMProvider` ABC (Claude-login default; Gemini / GLM / Anthropic-API stubs in `docs/PLAN.md` Future Work). Search provider swappable via `SearchProvider` ABC (DDG default).

### 5.4 שימושיות / Usability — קלות למידה, הפעלה, נגישות, הגנה מפני שגיאות

Letter-keyed terminal menu (A/B/C/D/E/X) navigable by keyboard alone. README is a full user manual with installation, usage, screenshots, sample run, troubleshooting. Errors surface as structured JSON log entries, never silent failures.

### 5.5 אמינות / Reliability — בשלות, זמינות, סובלנות לתקלות, התאוששות

Watchdog with two-signal detection (alive-check + heartbeat-staleness). Restart with exponential backoff `[1, 2, 4]` seconds, max 3 restarts per child per debate. Graceful shutdown cascade on SIGINT — children get 10-second drain window before SIGKILL. Partial transcript persisted on abort.

### 5.6 אבטחה / Security — סודיות, שלמות, אימות, אחריותיות

Zero secrets in source code. All API keys via `os.environ.get(...)` only. `.env` git-ignored; `.env-example` committed with placeholders. `ApiGatekeeper` enforces token budget and rate limits — no rogue process can bust the cap. JSON wire protocol validated on both send and recv — no arbitrary-shape messages accepted.

### 5.7 תחזוקתיות / Maintainability — מודולריות, שימוש חוזר, ניתנות לניתוח, לשינוי, לבדיקה

Six clean layers (Terminal Menu → SDK → Orchestrator → Watchdog → Agents → Gatekeeper + Tools). Every `.py` file ≤150 lines (R8). Class hierarchy with three mixins; retry policy consolidated into Gatekeeper (single source of truth). 8 named lifecycle hooks (rubric §A9). 124 unit + 9 integration + 3 E2E tests.

### 5.8 ניידות / Portability — התאמה, ניתנות להתקנה, ניתנות להחלפה

`uv sync` on a fresh machine recreates the exact environment from `uv.lock`. Python 3.13 pinned via `.python-version`. No OS-specific code paths (no Unix-domain sockets — kept cross-platform deliberately, see ADR-001). Grader needs only: uv + Python 3.13 + Claude CLI (logged in) + git.

---

## 6. Security Requirements

| # | Requirement | Implementation |
|---|---|---|
| S1 | No API keys, passwords, tokens in source code | `os.environ.get(...)` only; `grep -r "sk-\|api_key" src tests` returns 0 |
| S2 | `.env-example` committed; `.env` git-ignored | `.gitignore` includes `.env`, `*.key`, `*.pem`, `credentials.json`, `*.token` |
| S3 | Gatekeeper enforces every external call | All `claude -p` invocations and DDG queries route through `ApiGatekeeper.execute()` |
| S4 | JSON wire protocol validated on send AND recv | jsonschema on both sides; reject malformed messages with `correction_request` |
| S5 | No arbitrary code execution from LLM output | Child agents return text only; no `exec()` / `eval()` / `subprocess` with LLM-controlled input |
| S6 | Logging never leaks secrets | Structured logger redacts any value matching `sk-*` or `Bearer .*` patterns |
| S7 | Future production hardening (out of scope for HW2) | Key rotation, secret manager, least-privilege — noted in PLAN.md "Production Considerations" for completeness |

---

## 7. Constraints

| # | Constraint | Reason |
|---|---|---|
| C1 | RAG is intentionally out of scope | Lec05 L1228-1232 — *"RAG is NOT mandatory, NOT mandatory, I repeat."* |
| C2 | CLI-only deliverable; no GUI required | Spec §8.6 — *"GUI optional + screenshots if you build one, but evaluation runs from the menu or SDK directly."* |
| C3 | Pairs only — Salah + Andalus (HW1 partner, confirmed via CLAUDE.md) | Spec §8.7 |
| C4 | Hebrew or English in debate dialogue; no Arabic | Spec §8.7 |
| C5 | Claude CLI must be installed and authenticated on grader's machine | Provider choice locked to Claude-login (zero API spend) — Prompt #3 |
| C6 | DuckDuckGo via `ddgs` is the default search provider; no API key required | Prompt #6 |
| C7 | Continuous commits to `main` only — Dr. Segal grades commit density, not PRs (lec04 L577-578) | Workflow discipline |
| C8 | `uv` is the only allowed package manager | R13 + rubric §18 + lec01 L1406-1441 |
| C9 | Each `.py` file ≤150 logical lines, no exceptions | R8 + lec01 L1374-1389 — *"In sacred letters"* (אסור לאף קובץ של פייתון להיות יותר מ-150 שורות) |
| C10 | Deadline: Friday 29 May 2026, 23:59 (Asia/Jerusalem) | Moodle assignment id=264177 |

---

## 8. Out of Scope

Explicit deferrals — each documented in `docs/PLAN.md` "Future Work" with the design seam left open.

| # | Item | Rationale | Where the door is left open |
|---|---|---|---|
| O1 | Multi-skill per agent (N10 originality bonus) | 3× combinatorial test matrix, ~2 days unavailable | `PartisanAgent` loads exactly one Skill today; loader could be extended to a list |
| O2 | Mixed-provider implementation (Pro=Claude, Con=Gemini) | User chose Claude-only (Prompt #3); zero API spend trade-off | `LLMProvider` ABC + factory registry — one new adapter is one config-key change |
| O3 | Compaction strategy in Gatekeeper | Math: 250 words × 20 turns × 3 voices ≈ 20K tokens vs Claude's 200K — not needed at this scale | Mentioned in `docs/PRD_gatekeeper.md` as a future drop-in |
| O4 | Unix-domain socket watchdog (showcase 3rd IPC primitive) | macOS portability risk; ADR-001 already names all 4 primitives | ADR-001 enumerates Signal / FIFO / Queue / Socket |
| O5 | RAG over Wikipedia for debate topic | C1 — lecturer explicitly said optional | Tool factory pattern accepts a `RAGProvider` plug-in if ever added |
| O6 | REST/HTTP API surface on top of SDK | Spec §8.6 says CLI suffices for grading | `DebateSDK` is the single entry point — adding a FastAPI wrapper is a one-file follow-up |

---

## 9. Technical Architecture Summary

Full architecture in `docs/PLAN.md`. Three-line summary:

Three `multiprocessing.Process` children (Judge + Pro + Con) communicate via `multiprocessing.Queue × 6` (in/out per child) plus a single `heartbeat_queue` (child→main) and a shared `multiprocessing.Value + Lock` for global token spend tracking. All Pro↔Con traffic routes through Judge (H4). All LLM and search calls funnel through `ApiGatekeeper`. Skills load statically as system prompts (ADR-002) from `.claude/skills/{pro,con,judge}_skill/SKILL.md`.

---

## 10. Timeline

Deadline: **Friday 29 May 2026, 23:59 Asia/Jerusalem**. Today: 2026-05-25. Effective working window: ~4 days.

| Phase | Day | Output |
|---|---|---|
| **A** — `docs/PRD.md` (this file) | Day 1 (2026-05-25) | This doc, awaiting your approval |
| **B** — `docs/PLAN.md` | Day 1 | C4 + UML + class diagram + 7 ADRs + ISO 25010 paragraph |
| **C** — `docs/TODO.md` | Day 1 | ~800 tasks; "very critical" verify pass adds ~200 |
| **E** — 9 per-mechanism PRDs | Day 1-2 | Approval gate #2 closes Day 2 morning |
| **Phases 0-10** — Execute TODO | Day 2-4 | Scaffold → foundation → providers → gatekeeper → skills → agents → orchestration → watchdog → SDK → tests |
| **Phase 11.1** — README | Day 4 | Full user manual |
| **Phase 12.1-12.2** — Run + Manual Phase 1 evidence | Day 4 | Screenshots + sample-session-1.json |
| **Phase 12.3** — Final audit-gate verification | Day 4 | ruff / coverage / line-enforcer / secrets / commit count / diagrams / cost table |
| **Phase 12.4** — Push to GitHub PUBLIC | Day 4 | Incognito-verified |
| **Phase 12.5** — Submission PDF + Moodle upload | Day 4 evening | Both pair members upload separately |

---

## 11. Acceptance Criteria

This project is "done" when ALL of the following are true:

1. `uv run ruff check src tests` → 0 errors
2. `uv run pytest tests/unit tests/integration --cov` → coverage ≥85%
3. `uv run python scripts/check_file_lines.py` → 0 violations
4. `uv run agent-debate` → menu launches; pressing A runs a full 10-ping debate with real Claude + real DDG; verdict is declared; transcript saved
5. `transcripts/sample-session-1.json` exists and is the full first-run debate
6. `README.md` ≥ 200 lines; contains install, usage, screenshots, the sample-session-1 dialogue inlined, cost analysis table, behavior notes, extension points, AI disclosure (verbatim syllabus paragraph), MIT license credit
7. All 9 `docs/PRD_<mechanism>.md` files exist with Input/Output/Setup docstring shape (rubric §A13)
8. `docs/PLAN.md` exists with class diagram (MANDATORY per HW2 spec §8.6), C4 diagrams, UML sequence for single ping, 7 ADRs, ISO/IEC 25010 paragraph using Hebrew/English term pairs
9. `docs/TODO.md` ≥ 500 tasks, target 800; all `[x]` checked at submission
10. ≥ 50 commits to `main` with meaningful messages
11. Manual Phase 1 evidence: ≥ 2 screenshots in `assets/manual-phase1-*.png` embedded in README
12. Repo is PUBLIC on GitHub; incognito-window-accessible
13. Both pair members have uploaded `uoh-sqak-ex02.pdf` to Moodle assignment id=264177
14. `docs/PROMPTS.md` audit trail includes ≥ 20 prompts captured with the five-field template (rubric §A22)

---

## 12. Risk Register (top 5)

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| 1 | Claude CLI rate-limit hit during debate (login mode shares quota with user) | Medium | Run blocks; partial transcript | Gatekeeper's retry-with-backoff + `retry_after_seconds=60`; debate can resume after window resets; fallback to E2E test at low ping count first |
| 2 | DDG rate-limits during burst (10 queries/min cap) | High | Web search disabled mid-debate | `WebSearchTool` falls back to pre-seeded `references/citations.md` in each Skill — graceful degradation |
| 3 | Watchdog kills a healthy child due to slow LLM response | Low | False restart, lost progress | `stuck_timeout=30s` is calibrated above the LLM `timeout_seconds=90`... wait, this needs fixing — see Open Question 1 |
| 4 | TODO.md verify pass adds so many tasks it can't be completed in 4 days | Medium | Some `[x]` markers fake | Be conservative on additions; accept that "minimum viable" + complete docs beats "all 1000 tasks half-done" |
| 5 | Andalus's GitHub handle unknown; collaborator-share fails | Medium | H14 audit miss (auto-zero risk) | Repo PUBLIC by default makes this a non-blocker for the lecturer; collaborator-add is a nice-to-have for Andalus to push back |

### Open Question 1: heartbeat-stuck threshold vs LLM timeout

The spec sets `stuck_timeout=30s` and `LLM timeout_seconds=90`. A child waiting on a 90-second LLM call would be SIGKILLed at the 30s mark. **Resolution:** the heartbeat fires every 2 seconds and is INDEPENDENT of LLM call state — the child's main thread emits heartbeats while a worker thread handles the LLM. Document this two-thread-per-child contract in `docs/PRD_watchdog.md`.

---

## 13. AI Usage Disclosure (verbatim syllabus + rubric §A25)

> "השימוש בתוצרי Gen AI בקורס זה מחייב דיווח על עצם השימוש והיקפו; האחריות על כתיבת המטלה חלה על המגיש בלבד ואין להסתמך על כלי Gen AI."
>
> *"Use of Gen AI products in this course requires reporting the use and its extent; responsibility for writing the assignment lies on the submitter alone, and one must not rely solely on Gen AI tools."*

This project was authored using **Claude Code CLI** (model: claude-opus-4-7) as the primary AI agent across an orchestrator session and a worker session. Every meaningful prompt is logged in `docs/PROMPTS.md` with the five-field template (Context / Goal / Prompt text / Example output / Iterative improvements / Best practice extracted). The pair members (Salah + Andalus) accept full responsibility for the submission; the AI agent served as a force-multiplier per Dr. Segal's 16× thesis.

---

## 14. Approval Sign-off

**Rubric §2.5 step 1 — first explicit approval gate.**

I (the worker session) have written this PRD derived from the brainstorming spec. **I am now PAUSED.** No code will be written, no other doc will be touched, until the user types **"approved"** (or directs revisions).

The grader inspects git timeline for evidence of this pause. The commit-message convention used for the approval transition:

```
docs(prd): root PRD approved by user — gate 1 cleared
```

After approval, the next phase begins:
- Phase B → `docs/PLAN.md` (architecture detail)
- Phase C → `docs/TODO.md` (~800 tasks)
- Phase E → 9 per-mechanism PRDs
- Approval gate #2 closes the docs phase
- Then code execution begins

---

## 15. Phase 14 (Bonus) — Presidential Debate Stage

> Cinematic 3D presentation layer over the existing Phase 13g viewer.
> Lives on branch `phase14-presidential-stage`; main keeps Phase 13g as
> the primary HW2 submission. Phase 14 is a separately-graded bonus
> exhibit, not a replacement for Phases 0-13.

### 15.1 Problem statement

Phase 13g proves the SSE wire works but reads as a list of slides on a flat
background. After seeing it, the user said: *"It's good, but not wow."*
Phase 14 turns that into a presidential-style broadcast — three illuminated
podiums (Pro / Judge / Con), per-speaker volumetric spotlights, cinematic
camera that swings to the active speaker, speech bubbles + Judge chyron,
fireworks behind the winner.

Real LLM calls are preserved (H1). The backend wire protocol is unchanged.

### 15.2 Functional requirements (numbered for traceability)

| #     | Requirement                                                                                              | User-quote source                              |
|-------|----------------------------------------------------------------------------------------------------------|------------------------------------------------|
| F14-1 | Page auto-starts a fresh live debate on mount, no Start button                                           | "AI grader will see it run without clicking"   |
| F14-2 | Backend uses Claude CLI (`claude /login`), never an API key                                              | Locked: "Do not use API keys"                  |
| F14-3 | Pro/Con responses are split into ~28-word sentence-bundled chunks; each chunk is its own bubble          | "Divide opinions into chunks, not one big bubble" |
| F14-4 | Judge intro slide opens debate; Judge verdict closes; both render in the bottom chyron                   | "At the beginning also the judge should have a turn" |
| F14-5 | Auto-advance dwell scales with text length, tuned for non-native English readers (130 wpm)               | "Time is not sufficient to read each chunk"    |
| F14-6 | Auto-advance does NOT reset when new chunks arrive mid-dwell                                             | "Auto move between chunks not working"         |
| F14-7 | When next slide arrives after current dwell already elapsed, advance immediately                         | Same                                           |
| F14-8 | Title banner shows "ON AIR" while live, "Recorded" after verdict, "Standby" before, "Off Air" on error  | "Where is the debate title?"                   |
| F14-9 | Title banner has a designed Motion pill below the title showing the topic                                | "Title that says motion should have a design"  |
| F14-10| Camera lerps to a per-speaker target on every speaker change                                             | "When it's Pro turn make camera like screenshot 2" |
| F14-11| Bottom strip pill colours match speaker accent; consecutive same-speaker chunks group into ONE pill      | "Points colors same as speaker's turn"         |
| F14-12| Bottom strip only renders past + active turns; future buffered chunks are hidden                          | "Make dashes according to the current turn"    |
| F14-13| Verdict slide shows OUTCOME caps line + Judge's 1-2 sentence rationale                                    | "At evaluation make the judge tell the reasoning" |
| F14-14| Fireworks particle bursts behind the winning podium during the verdict slide                             | "Add fireworks behind the winner at the end"   |
| F14-15| Decimal points inside numbers (`0.002%`, `3.14`) survive through chunking                                 | Regression: "0002%?... I do not see the dot"   |
| F14-16| "OFF AIR" only fires on permanent stream closure, not on transient EventSource reconnects                | "On air turned into off air while still debating" |
| F14-17| Setup-phase timeout renders a clear "Debate Aborted" chyron, not a 0 · 0 verdict                          | "Why sometimes on refresh this happens?"       |

### 15.3 In / out scope

**In:** 3D scene + camera + bubbles + chyron + title + chunking + dwell +
scoring + rationale + fireworks (all backed by tests).

**Out:** mobile / responsive; multi-debate history; audio; replacing the
Phase 13g viewer on `main`; changes to the wire protocol or agent skills.

### 15.4 Acceptance criteria

| #    | Criterion                                                            | How verified                          |
|------|----------------------------------------------------------------------|---------------------------------------|
| 14-A1| Page loads, debate auto-starts within 5 s, no click required         | Manual / screenshot                   |
| 14-A2| First Pro response visible within 30 s of page load                  | Manual / SSE log timing               |
| 14-A3| Camera visibly swings between Pro / Judge / Con podiums              | Manual                                |
| 14-A4| Fireworks visible during verdict slide                               | Manual / screenshot                   |
| 14-A5| Verdict chyron shows score + outcome + rationale                     | Manual                                |
| 14-A6| Different debates produce different scores                          | Run two debates, compare totals       |
| 14-A7| All files ≤150 lines                                                 | Pre-commit hook                       |
| 14-A8| `npx tsc --noEmit` clean; `npx vitest run` green (34 tests)         | CI / manual                           |
| 14-A9| `uv run pytest tests/unit` green (151 tests)                         | CI / manual                           |
| 14-A10| Decimal preservation regression (`0.002%`) passes                   | `lib/__tests__/chunks.test.ts`        |
| 14-A11| Setup-timeout shows "Debate Aborted" cleanly                        | Manual (refresh until it fires)       |

### 15.5 Submission impact

`main` still ships Phase 13g for the HW2 deadline. The `phase14-presidential-stage`
branch is documented in the README's Bonus section with screenshots; if the
user decides Phase 14 is more representative, it can be merged into `main`
before the deadline. **Whichever ships, the other remains accessible by
branch name.**
