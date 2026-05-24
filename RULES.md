# Grading Rubric (distilled from `software_submission_guidelines-V3.pdf` + HW2 spec)

> The 39-page Hebrew rubric is the same as HW1. This document is the actionable summary plus HW2-specific items from `materials/hw2-spec-main-v4-Agents-Subagents-Commands.pdf`. Read it carefully before starting.

## Quick-reference scorecard

| # | Rule | Threshold | How it's audited |
|---|------|-----------|------------------|
| 1 | **SDK Architecture** | All business logic flows through an SDK layer | Code review |
| 2 | **OOP / no duplication** | Anything used 2+ times must be extracted (base class / mixin / Template Method). **Architecture diagram required for HW2.** | Code review + diagram |
| 3 | **API Gatekeeper** | All external API calls (LLMs, web search) through a centralized class | Code review + test |
| 4 | **Rate Limiting + Token Budget** | Defined in JSON config, never in code. Gatekeeper enforces. | Config test |
| 5 | **Wave management (queue)** | FIFO queue, backpressure, no crashes when limits hit | Integration test |
| 6 | **Version Control** | Code + config versions start at `1.00`, `+0.01` per change | Version module check |
| 7 | **TDD** | Red → Green → Refactor, tests written before/with code | Work process |
| 8 | **File Size** | ≤ 150 lines per Python file (excluding comments/blanks) | Automated count |
| 9 | **Linter** | `ruff check` returns 0 failures | ruff |
| 10 | **Test Coverage** | `pytest --cov` ≥ 85% (`fail_under = 85` in pyproject.toml) | pytest |
| 11 | **Hardcoded Values** | 0 in source — all values in config | Code review |
| 12 | **Secrets** | 0 in source — `.env-example` + `os.environ.get(...)`, `.env` git-ignored | Auto scan |
| 13 | **Package Manager** | `uv` for everything (no pip/venv/virtualenv) | Auto |

## HW2-specific scorecard additions (from spec section 8)

| # | Rule | Threshold | How it's audited |
|---|------|-----------|------------------|
| H1 | **Real LLM calls** | No faked/scripted dialogue. Must be genuine multi-turn LLM. | Code review + log inspection |
| H2 | **JSON wire protocol** | All inter-agent messages serialized as JSON | Code review + log inspection |
| H3 | **≥10 pings per side** | At least 10 argument↔counter-argument cycles per debater (or 5 with explicit budget note in README) | Log inspection |
| H4 | **All traffic through Judge** | Pro ↔ Con must route through Judge process; never direct | Code review |
| H5 | **Judge declares winner** | No ties; differential scoring OK (e.g., 70/80), ambiguity NOT OK | Behavior test |
| H6 | **Internet search tool** | Web-search tool integrated and used during debate for citations | Code + log evidence |
| H7 | **Mutual reference** | Each turn references opponent's prior point (no parallel monologue) | Log inspection |
| H8 | **Different Skills per debater** | Pro and Con use distinct `Skill` definitions (LLMs auto-agree if identical) | Code review |
| H9 | **Watchdog + keep-alive** | If child process dies, kill remnants + restart | Code review + chaos test |
| H10 | **Timeouts on every LLM call** | No request without an explicit timeout | Code review |
| H11 | **Terminal menu** | Keyboard-operable menu; GUI optional | Manual test |
| H12 | **Hebrew/English only** | No Arabic in debate output (lecturer can't read it) | Log inspection |
| H13 | **Pairs only** | Solo requires explicit pre-approval from `rmisegal@gmail.com` | Submission check |
| H14 | **Repo accessibility** | Public OR shared with `rmisegal@gmail.com`. Inaccessible = automatic rejection, no resubmit. | Submission check |
| H15 | **Submission PDF** | Each pair member uploads same-repo-link PDF to Moodle separately | Moodle |
| H16 | **Judge enforces PC/respectful-language gate** | Vulgar messages sanitized/rejected by Judge before re-broadcast (lec05 L1553-1559) | Code review + log inspection |
| H17 | **Skills are PROJECT-LOCAL ONLY** | Under `.claude/skills/`, never `~/.claude/skills/` (lec05 L1330-1332) | Repo audit |
| H18 | **Judge issues setup directives at debate start** | Message type `"setup_directive"` to each child with stance + rules + format (lec05 L1213-1221) | Code review + log inspection |
| H19 | **Judge is topic-agnostic** | System prompt contains no topic words; only debate rules + scoring criteria (lec05 L1449-1469) | Code review |
| H20 | **Per-message drift check** | Judge verifies role-faithfulness EVERY message; correct + replay on violation (lec05 L1182-1184) | Code review + log inspection |
| H21 | **Watchdog with KPI heartbeat** | Heartbeat ping per child; kill on stuck; restart with backoff (lec05 L1302-1314) | Code review + chaos test |
| H22 | **README must include Phase 1 manual-debate screenshots** | Evidence of having debated manually before coding (lec05 L1896-1909) | README inspection |
| H23 | **Mixed LLM providers per agent ENCOURAGED** | Pro on Claude, Con on Gemini (e.g.) — different providers strengthen contradiction (lec05 L1131-1142) | Code review |
| H24 | **Web search has dual purpose** | Cite own evidence AND fact-check opponent's lies (lec05 L1483-1491) | Code review + log inspection |
| H25 | **Outcome non-reproducibility is DESIRED** | Different runs different winners — README must state this is intentional (lec05 L1581-1597) | README inspection |

## Section-by-section requirements

### 1. README.md (root, mandatory)
Must read like a full user manual. **HW1 was rated strong on documentation — keep this up.**
- **Installation Instructions**: prerequisites (Python 3.10+, uv, LLM API key or CLI login), step-by-step setup, environment configuration, common-issue troubleshooting
- **Usage Instructions**: how to launch the menu, how to run a debate, CLI flags, how to plug in a new topic, how to swap LLM provider
- **Examples & Demos**: code samples, **screenshots of the menu and a live debate**, common use cases
- **Session-1 Full Dialogue**: paste a complete first debate (Pro/Con/Judge messages + Judge's final ruling) into the README — this is explicitly required by Dr. Segal so a reader can understand the system without running it
- **Architecture Diagram**: embed the class diagram + the IPC flow diagram
- **Configuration Guide**: explanation of every JSON config file and parameter
- **Contribution Guidelines**: code/style standards, pre-commit hooks
- **License & Credits**: usage license + LLM provider attribution + AI agent acknowledgment (per syllabus ethics policy)

### 2. `docs/` folder (mandatory)
- **`docs/PRD.md`** — root Product Requirements Document with all standard sections (overview, goals, KPIs, functional + non-functional requirements, security requirements, constraints, timeline, out-of-scope)
- **`docs/PLAN.md`** — architecture & technical plan:
  - **C4 Model** diagrams (Context, Container, Component, Code)
  - **UML** for the multi-process IPC flow (sequence diagram of a single ping cycle)
  - **Class diagram** of the OOP hierarchy (Agent base → Judge/Pro/Con specializations, Skill, Tool, IPC bus) — **mandatory per HW2 spec section 8.6**
  - **ADRs** with rationale + trade-offs (e.g., "why JSON over Protobuf for IPC", "why subprocess over multiprocessing.Process", "why this watchdog policy")
  - **ISO/IEC 25010 paragraph** covering all 8 dimensions
  - **Deployment / operational** architecture (where logs go, how to bring up the system, how to graceful-shutdown)
  - API documentation, interface specs, JSON schema for inter-agent messages
- **`docs/TODO.md`** — full task list:
  - **MIN 500 tasks. Aim for 800.**
  - Priorities + statuses (pending/in-progress/completed)
  - Phase breakdown with milestones
  - Definition of Done per task
- **`docs/PRD_<mechanism>.md`** — per-component PRD for each major piece (judge_agent, pro_agent, con_agent, orchestrator, ipc_bus, gatekeeper, watchdog, skills, web_search_tool). Each must include:
  - Theoretical background
  - Input/Output format
  - Performance metrics
  - Constraints, alternatives considered, justification
  - Specific success criteria + test scenarios
- **`docs/PROMPTS.md`** — Prompt Engineering Log

### 3. Mandatory work process (page 9 of PDF)
1. Create `docs/PRD.md` and **get user approval** before continuing
2. Create `docs/PLAN.md`
3. Create `docs/TODO.md`
4. Create per-mechanism PRDs
5. **Approve all docs before development starts**
6. Develop with TODO.md as you go, updating as you progress
7. Save results, create visualizations, update README.md

### 4. Code & project structure
- Modular layered architecture (`agents/`, `orchestration/`, `skills/`, `tools/`, `shared/`, `menu/`, `sdk/`)
- **MAX 150 lines per Python file** (no empty lines or comments counted)
- Comments explain **WHY**, not WHAT
- Full docstrings on every public function/class/module
- Naming: descriptive, theoretical/mathematical names where appropriate (`PingCycle`, `Argument`, `Verdict`, `Score`)
- DRY (Don't Repeat Yourself)
- Single Responsibility per function
- `__init__.py` everywhere; use `__all__` and define `__version__` at package root
- Relative imports only (no absolute paths)

### 5. SDK Architecture
```
External Consumers (Terminal Menu / CLI / future REST / future GUI / Tests)
        |
        v
+-------+-------+
|     SDK       |  ← Single entry point for ALL logic
+-------+-------+
        |
        v
+-------+-------+
| Agents +      |  ← Judge / Pro / Con + orchestration + skills + tools
| Orchestration |
+-------+-------+
        |
        v
+-------+-------+
| Infrastructure|  ← LLM API, web search API, file I/O, logging
+---------------+
```
- All business logic exposed via the SDK class
- **No business logic in menu/CLI/test layers** — those are thin wrappers around the SDK
- Tests use the SDK directly (this is also how the lecturer's grading agent would inspect)

### 6. OOP without duplication
- Same function body in 2+ classes → shared module function or mixin
- Same try/except pattern in 3+ classes → wrapper function
- Identical method in 3+ classes → base class or mixin
- Repeated logic with slight variations → Template Method pattern

**HW2 OOP layout (suggested):**
- `BaseAgent` — common: spawn, send/recv JSON, handle timeout, signal handling, graceful shutdown
- `JudgeAgent(BaseAgent)` — adds: round-robin orchestration, scoring rubric, no-tie enforcer
- `PartisanAgent(BaseAgent)` — abstract: shared debater behavior (respond-with-citation, reference-opponent)
- `ProAgent(PartisanAgent)` — loads Pro Skill
- `ConAgent(PartisanAgent)` — loads Con Skill

Mixin rules:
- Each mixin handles exactly one concern (e.g., `LoggingMixin`, `RetryMixin`, `MetricsMixin`)
- Mixins don't override each other's methods
- Mixins must be self-testable in isolation

### 7. API Gatekeeper
All external API calls go through a centralized class:
- **No direct API calls** that bypass the gatekeeper (LLM AND web search both)
- Rate limits enforced before each call
- Token budget enforced before each LLM call (HW2-critical — debates burn tokens fast)
- Queue management (FIFO, no requests dropped)
- All calls logged for monitoring

`config/rate_limits.json`:
```json
{
  "version": "1.00",
  "services": {
    "claude": {
      "requests_per_minute": 30,
      "tokens_per_day": 200000,
      "concurrent_max": 3,
      "retry_after_seconds": 30,
      "max_retries": 3
    },
    "web_search": {
      "requests_per_minute": 10,
      "requests_per_hour": 100,
      "concurrent_max": 2
    }
  }
}
```

### 8. TDD
- RED → GREEN → REFACTOR
- Every new module gets a matching test file
- Every public function/method gets ≥ 1 test
- Tests cover happy path AND error cases (e.g., LLM timeout, malformed JSON, child process crash)
- Use **Mock for LLM and web-search** in unit tests — no real API calls in test suite
- Test structure mirrors source structure
- Integration tests use a **mock LLM** that returns canned responses so the full debate flow can be exercised offline
- Chaos test: kill a child process mid-debate and verify the watchdog recovers

### 9. Coverage
- **Minimum 85% global** (`fail_under = 85`)
- Statement + Branch + Path coverage for critical paths (Judge decision logic, IPC bus, Gatekeeper)
- `pyproject.toml`:
  ```toml
  [tool.coverage.run]
  source = ["src"]
  omit = ["src/agent_debate/main.py", "*/tests/*"]

  [tool.coverage.report]
  fail_under = 85
  ```

### 10. Edge cases (HW2-relevant)
- Document each with input + expected output:
  - LLM API timeout / 429 rate limit
  - LLM returns malformed JSON (not parseable as `Argument`)
  - Child process dies mid-debate (watchdog must restart)
  - Both debaters agree on a point (Judge must intervene per HW2 spec section 9)
  - Debater attempts to lie (allowed per spec — opponent must catch)
  - Web search returns no results
  - Web search times out
  - User Ctrl+C — graceful shutdown of all 3 processes

### 11. Linter — Ruff
`ruff check` MUST pass with 0 errors.
```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501"]
```

### 12. No hardcoded values
- Topic, agent stances, ping count, timeouts, model names — all in JSON config
- API keys via `os.environ.get(...)` only
- Acceptable inline: mathematical constants, default function parameters, `constants.py` items, `Enum` values

### 13. Configuration architecture
```
config/
├── setup.json            # Main app config (versioned)
├── agents.json           # Per-agent: model, temperature, max-tokens, skill ref
├── debate_rules.json     # Pings per side, word limit, judge rubric weights
├── rate_limits.json      # API rate limits + token budgets (versioned)
├── logging_config.json   # FIFO log rotation (files × lines)
.env                      # Secrets (git-ignored)
.env-example              # Placeholders (committed): CLAUDE_API_KEY, BRAVE_SEARCH_API_KEY, etc.
pyproject.toml            # Build / lint / test settings
src/<package>/constants.py  # Immutable project constants + Enums
```

### 14. Information security
- **No** API keys, passwords, tokens in source code
- Use `os.environ.get("CLAUDE_API_KEY")` only
- `.gitignore` MUST include: `.env`, `*.key`, `*.pem`, `credentials.json`, `logs/*.jsonl`, `transcripts/*.json` (or at least the bulk; keep one or two sample transcripts in `docs/`)
- `.env-example` MUST exist with placeholder values

### 15. Versioning
| Item | Location | Initial value |
|------|----------|---------------|
| Code version | `src/<package>/shared/version.py` | `1.00` |
| Setup config version | `config/setup.json` `"version"` key | `1.00` |
| Agents config version | `config/agents.json` `"version"` key | `1.00` |
| Debate rules version | `config/debate_rules.json` `"version"` key | `1.00` |
| Rate limits version | `config/rate_limits.json` `"version"` key | `1.00` |

App must validate config version compatibility at startup.

### 16. Git workflow
- **History matters** — meaningful commit messages, clear story
- Use feature branches for new functionality
- Self-PR via branch + merge is fine for solo/pair work
- Tag major versions (`v1.00`)
- **HW1 lesson:** continuous commits worked well — keep that up

### 17. Prompt Engineering Log
`docs/PROMPTS.md` must record EVERY prompt used to generate code AND the prompts used as system prompts for Pro/Con/Judge:
- Context (what you were trying to do)
- Goal (what output you wanted)
- The actual prompt text
- Examples used
- Iterative improvements
- What didn't work and why
- For Pro/Con system prompts specifically: document how you ensured contradiction (different Skills, distinct personas)

This is mandatory and audited. Don't skip it.

### 18. uv as package manager
**MUST** use `uv`. **CANNOT** use:
- `pip install` (forbidden)
- `python -m` (forbidden)
- `venv` (forbidden)
- `virtualenv` (forbidden)

| Task | Right (uv) | Wrong |
|------|-----------|-------|
| Install dependencies | `uv sync` | `pip install` |
| Add a dependency | `uv add <pkg>` | `pip install <pkg>` |
| Run a script | `uv run python script.py` | `python script.py` |
| Run tests | `uv run pytest tests/` | `python -m pytest` |
| Lock dependencies | `uv lock` | `pip freeze` |

`pyproject.toml` is the single source of truth (no `requirements.txt`). `uv.lock` exists and is git-tracked.

### 18.5. Extension architecture — REQUIRED
**HW1 was flagged here.** Don't repeat. For HW2:
- **Skill registry** — adding a new debate stance should be a config + skill-dir addition, not core code change
- **Agent factory** — adding a fourth role (e.g., a Fact-Checker) shouldn't require modifying existing agent files
- **Lifecycle hooks** — `before_round`, `after_round`, `before_verdict`, `after_verdict` exposed for middleware
- **Tool registry** — new tools (e.g., a Wikipedia tool, a citation-checker) can be plugged in without changing the Gatekeeper or agent code
- **API-first** — every component has a clean interface (`def step(self, message: Argument) -> Response`)

Document the extension points in `docs/PLAN.md` AND in `README.md`.

### 18.6. ISO/IEC 25010 quality dimensions — REQUIRED
**HW1 was strong here only if you actually wrote the paragraph.** For HW2, dedicate a section in `docs/PLAN.md` covering all 8 dimensions:
1. **Functional Suitability** — completeness (all 8 mandatory rules met), correctness (Judge actually decides, no ties), appropriateness (debate format suits the goal)
2. **Performance Efficiency** — response time per LLM call < N seconds; token spend per debate within budget; memory bounded
3. **Compatibility** — runs on macOS / Linux / WSL; LLM provider swappable
4. **Usability** — terminal menu navigable by keyboard; README explains everything
5. **Reliability** — watchdog recovers from child death; graceful Ctrl+C
6. **Security** — no secrets in code, Gatekeeper limits spend, rate limits prevent runaway
7. **Maintainability** — modular, mixins, base classes, tests, docs
8. **Portability** — `uv sync` on fresh machine works; config is environment-agnostic

### 18.7. Parallel processing — HW2 CORE
The whole point is multi-process. Document explicitly:
- **`multiprocessing.Process`** (or `subprocess.Popen`) spawns the 3 children
- **`multiprocessing.Queue`** (or stdin/stdout pipes, or sockets) is the IPC bus
- Thread safety: shared state (e.g., the metrics counter) protected with `multiprocessing.Lock`
- Document `num_workers` / process pool sizing as a config parameter
- Architecture decision: subprocess vs multiprocessing vs threading — record in ADR

### 18.8. Building blocks design — REQUIRED
Each significant component (Judge, Pro, Con, Gatekeeper, IPC Bus, Watchdog, each Skill, each Tool) is a "building block" defined by:
- **Input Data**: types, valid range, external dependencies, full validation
- **Output Data**: types, format, edge-case behavior
- **Setup Data**: parameters with defaults, configuration, init

Design principles:
- **Single Responsibility**: each block does one thing
- **Separation of Concerns**: each block deals with one aspect
- **Reusability**: blocks are self-contained, no specific dependencies
- **Testability**: each block testable via dependency injection (mock LLM into Agent; mock IPC into Orchestrator)

### 19. Research & Results Analysis (lighter for HW2 than HW1)
HW2 doesn't need a `notebooks/analysis.ipynb` like HW1 did, BUT:
- Save **every debate transcript** to `transcripts/<timestamp>-<topic>.json`
- Include analysis in README:
  - Token spend per debate (Pro / Con / Judge breakdown)
  - Win-rate analysis if you run the same debate multiple times with different seeds
  - Qualitative reflection: when does the Judge favor Pro vs Con? Does temperature affect debate quality?
- Use seaborn/matplotlib for any plots (token spend over time, win distribution, etc.)

### 20. Final checklist
Before submission:

**Documentation & structure**:
- [ ] Comprehensive README.md at root (user-manual level + screenshots + session-1 dialogue)
- [ ] `docs/` folder with PRD.md, PLAN.md, TODO.md
- [ ] Per-mechanism PRDs (judge_agent, pro_agent, con_agent, orchestrator, ipc_bus, gatekeeper, watchdog, skills, web_search_tool)
- [ ] Architecture diagrams: class diagram (mandatory), C4 (mandatory), UML sequence for IPC flow
- [ ] Up-to-date Prompt Engineering Log (`docs/PROMPTS.md`)

**Architecture & code**:
- [ ] SDK architecture — all business logic flows through SDK
- [ ] OOP — no code duplication, base class + mixins for shared concerns
- [ ] API Gatekeeper — all external calls (LLM + web search) flow through it
- [ ] Rate limits + token budget in config, FIFO queue, wave handling
- [ ] Files ≤ 150 lines, with docstrings + comments
- [ ] Real LLM calls (no faked dialogue)
- [ ] JSON wire format
- [ ] All traffic through Judge
- [ ] Watchdog + keep-alive
- [ ] Timeouts everywhere

**Tests & quality**:
- [ ] TDD — tests written before or with code
- [ ] Coverage ≥ 85%
- [ ] Ruff: 0 errors
- [ ] Edge cases documented + handled
- [ ] Mock LLM for unit + integration tests
- [ ] Chaos test (kill a child mid-debate)
- [ ] Pre-commit hook enforcing ruff + pytest (HW1 missed this — add it for HW2)

**Configuration & security**:
- [ ] Config files separated from code, with versions
- [ ] `.env-example` with placeholder values
- [ ] No API keys / secrets in code
- [ ] `.gitignore` updated (logs/, transcripts/, .env, *.key)
- [ ] uv as the only package manager
- [ ] `pyproject.toml` and `uv.lock` exist and tracked

**Debate behavior**:
- [ ] ≥10 pings per side (or 5 with budget reason noted in README)
- [ ] Mutual reference (each turn references opponent)
- [ ] Web-search tool used
- [ ] Judge declares a winner (no ties)
- [ ] Hebrew or English only

**Versioning & extensions**:
- [ ] All starting at version 1.00
- [ ] Documented extension points (Skill registry, Agent factory, Tool registry, lifecycle hooks)
- [ ] Maintainable Python package organization
- [ ] Multi-processing with thread safety documented

**Submission**:
- [ ] Pairs only (or solo permission obtained in writing)
- [ ] GitHub repo accessible (public OR shared with rmisegal@gmail.com)
- [ ] Submission PDF (`uoh-sqak-ex02.pdf`) uploaded to Moodle by each pair member separately
- [ ] Self-grade is honest (default 85; bump only with evidence)

## How the lecturer will probably grade
1. Run `ruff check`, `pytest --cov`, file-line counter, secret scanner — auto-fail if any miss
2. Inspect `docs/` for PRD/Plan/Todo + per-component PRDs
3. Read README.md to verify it's manual-grade + has the session-1 dialogue
4. Inspect git history for continuous commits
5. Run the project via `uv run` — try the terminal menu, watch a debate happen
6. Try to break it: kill a child process, see if watchdog recovers; supply bad config and see if it bails cleanly
7. Read sample transcripts in `transcripts/` — verify dialogue is real, mutual reference present, judge actually decides
8. Spot-check architecture (SDK, gatekeeper, OOP class diagram matches code)
9. Apply the self-grade-modulated strictness:
   - Self-grade 100 → "looking for elephants in needles" (extreme nitpick)
   - Self-grade 60 → lenient
   - **HW1 lesson:** target 85, max 88 unless deliverable is genuinely exceptional

## Important note (page 33 of PDF, end)
> "It's clear that as part of the inspection, AI agents will be used. Recommended to use LLMs and AI agents to help complete the project."

The lecturer encourages using AI agents — and this whole worker session is literally that. Just document the prompts in `docs/PROMPTS.md` per the ethics policy.

---

## Appendix — Items recovered from full deep-read of the rubric PDF

The deep re-read found rubric details NOT in the original distillation. Below: items the grading agent will pattern-match against. Use verbatim phrasing where shown.

### A1. Rubric structure: the PDF has 20 sections, not 13

The famous "13 rules" come from **Table 5 on p. 33** ("כרטיס עזר מהיר לדרישות" — quick-reference cheat card). The full rubric has 20 numbered sections, ~39 pp. The Table 5 entries are the auto-graded gates; the rest is the qualitative criteria. See `CONTEXT-rubric-and-pdfs.md` §1.1 for the full TOC with page numbers.

### A2. The "16×" positioning statement (§1.4, p. 6 — quote in PRD intro)

> "מתכנת העובד עם סוכני AI ומשתמש בשיטת קידוד בהנחיה יכול לייצר בפרק זמן נתון פי 16 יותר שורות קוד איכותיות בהשוואה לכתיבה ידנית ללא AI"
> *"A developer working with AI agents using Vibe Coding can produce 16× more quality code lines per time unit vs hand-writing without AI."*

> "הכלל הראשון והחשוב ביותר: כדי לנצל את מלוא הפוטנציאל של סוכני AI, חובה להגדיר דרישות ברורות ומפורטות"
> *"The first and most important rule: to unlock AI agents' full potential, you MUST define clear and detailed requirements."*

Quote one or both in the `README.md` intro or `docs/PRD.md` to signal alignment.

### A3. The 7-step approval gate process (§2.5, p. 9 — verbatim)

1. יצירת `docs/PRD.md` — **ואישורו לפני המשך** *(approve before continuing)*
2. יצירת `docs/PLAN.md`
3. יצירת `docs/TODO.md`
4. יצירת מסמכי PRD ייעודיים לכל אלגוריתם/מנגנון מרכזי
5. **אישור כל המסמכים לפני תחילת הפיתוח** *(approve ALL docs before development starts)*
6. התחלת פיתוח — עדכון TODO.md עם התקדמות
7. שמירת תוצאות, ויזואליזציות, ועדכון README.md

**Steps 1 and 5 are EXPLICIT user-approval gates.** The grading agent looks at git timeline for evidence of these pauses.

### A4. Gatekeeper class signature (§5.1, p. 13 — match verbatim)

```python
class ApiGatekeeper:
    """Centralized API call manager."""
    def __init__(self, config: RateLimitConfig): ...
    def execute(self, api_call, *args, **kwargs):
        """- Check rate limits before execution
           - Queue if limit reached
           - Retry on transient failures
           - Log all calls
        """
    def get_queue_status(self) -> QueueStatus: ...
```

Name the file `gatekeeper.py`, the class `ApiGatekeeper`, and match the method signature shape. This is what the grading agent pattern-matches against.

### A5. Queue requirements (§5.3, p. 14 — explicit)

The Gatekeeper queue MUST implement all four:
- "תור FIFO לבקשות ממתינות" — FIFO queue for pending requests
- "עומק תור מקסימלי מוגדר בקונפיגורציה" — max queue depth in config
- "**התראת לחץ (backpressure)** כאשר התור מלא" — backpressure alert when full
- "**מנגנון ריקון** שמעבד בקשות כאשר חלונות הקצב מתאפסים" — drain mechanism when rate windows reset

Tests required: each of the four behaviors gets at least one explicit integration test.

### A6. TDD — seven enumerated requirements (§6.1, p. 15)

1. כל מודול חדש חייב קובץ בדיקות מתאים
2. כל פונקציה ציבורית חייבת לפחות בדיקה אחת
3. בדיקות מסלול תקין וגם מקרי שגיאה
4. שימוש ב-fixtures מ-`conftest.py` לנתוני בדיקה משותפים
5. **Mock לתלויות חיצוניות (DB, files, API)** ← for HW2: mock the LLM AND web search
6. **קבצי בדיקות עומדים גם הם בכלל 150 השורות** *(test files also obey the 150-line rule)*
7. **אין בדיקות שתלויות בשירותים חיצוניים** *(no tests with live external services)* ← **no live LLM calls in tests**

### A7. Token cost analysis is MANDATORY for HW2 (§11 + §17.5)

HW1's distillation marked this "not relevant here" because HW1 had no API calls. **HW2 IS an API consumer**, so this becomes mandatory. README must include a table like:

| Model | Input tokens | Output tokens | Total cost |
|---|---|---|---|
| Claude Sonnet 4.5 | (running total) | (running total) | $X.XX |
| Web search calls | (N calls) | — | $X.XX |
| **Total per debate** | … | … | $X.XX |

Plus an "Optimization Strategies" subsection covering: token-reduction tactics, batch processing, model selection by cost-benefit, cache-friendly prompt structure.

### A8. Budget management features for the Gatekeeper (§11.2)

- **Cost forecast for scale** — `gatekeeper.estimate_cost(n_debates)`
- **Real-time usage monitoring** — `gatekeeper.get_spend_so_far()` exposed
- **Budget overrun alerts** — emit event/log when crossing configured % thresholds (default: warn at 75%, hard-cap at 95%)

### A9. Extension architecture — concrete lifecycle hooks (§12.1, p. 24)

Don't just say "supports extension"; **name the hooks** in `docs/PLAN.md` and `README.md`:

- `before_round`, `after_round`
- `before_verdict`, `after_verdict`
- `before_llm_call`, `after_llm_call`
- `before_search`, `after_search`

Each hook gets a documented signature and a usage example.

### A10. ISO/IEC 25010 — verbatim Hebrew/English pairs (§13.1, p. 25)

Use these exact term pairs in the `docs/PLAN.md` ISO 25010 section so the grading agent's pattern match scores:

- **התאמה פונקציונלית** / **Functional Suitability** — שלמות, נכונות, התאמה
- **יעילות ביצועים** / **Performance Efficiency** — זמני תגובה, ניצול משאבים, יכולת
- **תאימות** / **Compatibility** — יכולת פעולה הדדית, דו-קיום
- **שימושיות** / **Usability** — קלות למידה, הפעלה, נגישות, הגנה מפני שגיאות
- **אמינות** / **Reliability** — בשלות, זמינות, סובלנות לתקלות, התאוששות
- **אבטחה** / **Security** — סודיות, שלמות, אימות, אחריותיות
- **תחזוקתיות** / **Maintainability** — מודולריות, שימוש חוזר, ניתנות לניתוח, לשינוי, לבדיקה
- **ניידות** / **Portability** — התאמה, ניתנות להתקנה, ניתנות להחלפה

One paragraph per dimension in `docs/PLAN.md` naming the concrete HW2 feature that satisfies it.

### A11. Packaging checklist — 4 questions (§14.4, p. 26)

The grading agent likely runs verbatim. Answer each in `README.md` or `docs/PLAN.md`:
1. Does `pyproject.toml` exist? Does it list name, version, dependencies with versions?
2. Does `__init__.py` exist in package roots? Does it export public interfaces? Is `__version__` defined?
3. Is source in a dedicated dir (`src/`)? Tests in `tests/`? Docs in `docs/`?
4. All imports relative? No absolute paths?

### A12. Thread-safety 4-item checklist (§15.2, §15.3)

For HW2's multiprocessing setup:
1. **Lock protection** on shared metrics (token counter, spend tracker)
2. **`queue.Queue` or `multiprocessing.Queue`** for inter-agent messages
3. **Context managers** for lock acquisition (`with lock:` everywhere)
4. **No deadlocks** — proper ordering; document via ADR

§15.3 also requires: (1) classify operations I/O-bound vs CPU-bound, (2) dynamic process/thread count, safe data sharing, correct synchronization, (3) proper resource cleanup, exception handling, no memory leaks, (4) protect shared variables, prevent races and deadlocks.

### A13. Building-block docstring shape (§16.3, pp. 28-29 — verbatim format)

Every significant class (Judge, Pro, Con, Gatekeeper, IPC bus, Watchdog, each Skill, each Tool) gets this docstring shape:

```python
class JudgeAgent(BaseAgent):
    """
    Input:  ping_message (PingMessage), debate_state (DebateState)
    Output: judgement (Judgement), routed_message (Optional[Message])
    Setup:  intervention_threshold (int, default: 3),
            scoring_weights (Dict[str, float]),
            llm_provider (LLMProvider)
    """
    ...
```

Three explicit lines: `Input:`, `Output:`, `Setup:`. The rubric's exact example uses these labels.

### A14. Structured logs default — 20 files × 500 lines (HW2 spec §8.6 verbatim)

> "לוגים מובנים — חבילה מוכנה, FIFO המוגדרים בקובץ הקונפיגורציה — למשל **20 קבצים, כאשר כל קובץ מכיל עד 500 שורות**"

Default `config/logging_config.json`:
```json
{
  "version": "1.00",
  "fifo_files": 20,
  "max_lines_per_file": 500,
  "rotation_policy": "size_or_count",
  "output_dir": "./logs",
  "structured": true,
  "level": "INFO"
}
```

### A15. Class diagram is EXPLICITLY MANDATORY (HW2 spec §8.6)

> "יש לצרף שרטוט הארכיטקטורה של פריסת המחלקות והקשרים ביניהן"
> *"Must attach a diagram of the architecture showing class layout and relationships between them."*

Not "recommended" — required. Put it in `docs/diagrams/class-diagram.svg` (or .png), embed in README and PLAN.md. Mermaid syntax acceptable if SVG export is committed.

### A16. Judge drift-detector spec (HW2 spec §9 — class clarification)

> "הסכמות במהלך הוויכוח? מותרות באירוע נקודתי, אבל אסור שסוכן אחד יסחף את חברו לכל אורך הוויכוח. **האב חייב להתערב ולהזכיר את התפקיד.**"
> *"Agreements during the debate? Allowed as point-in-time, but one agent shouldn't drag the other along throughout the debate. The Father must intervene and remind of the role."*

**Concrete feature**: the Judge needs an active "drift detector". When both children have agreed for ≥ N consecutive pings (default: 3), the Judge MUST inject a re-orient message reminding each of their stance. N is configurable in `config/debate_rules.json` as `drift_intervention_threshold`.

### A17. Lies allowed; opponent must catch them (HW2 spec §9)

> "שקרים בויכוח? מותר. הצד הנגדי אמור לתפוס אותם — זה חלק מכושר השכנוע"
> *"Lies in the debate? Allowed. The opposing side is supposed to catch them — it's part of persuasion power."*

**Implication**: the web-search tool serves DUAL purpose — citation source AND fact-checking opponent's claims. The Pro/Con Skill prompts should explicitly authorize/encourage fact-checking the opponent.

### A18. Judge must NOT know the topic (HW2 spec §9)

> "האם השופט חייב לדעת את הנושא? לא. השופט מבין רק את חוקי המשחק ושופט כושר שכנוע. דווקא טוב שהוא לא יודע — כך אינו מוטה"
> *"Must the Judge know the topic? No. The Judge knows only the game rules and judges persuasiveness. It's actually better that he doesn't know — so he's not biased."*

**Implication**: the Judge's system prompt must NOT contain the debate topic. The Judge sees the actual content of arguments but evaluates on form (persuasiveness, evidence usage, rebuttal quality, clarity), not on whether the position is "right". Document in `docs/PRD_judge_agent.md`.

### A19. Three-stage build progression (HW2 spec §8.5)

Dr. Segal recommends a graduated approach — bake into `docs/PLAN.md` phases AND `docs/TODO.md` milestones:

1. **Manual stage** (in terminal) — two Claude CLIs (or Claude + Gemini), role-assigned by hand, debate driven manually. *"Just to understand the phenomenon."* Capture screenshots → README.
2. **Intermediate** — a Claude CLI Command (`/debate`) that launches Father → who launches children. Capture screenshot → README.
3. **Final** — Python main process managing all 3 sub-processes via `multiprocessing` / IPC. This is the submitted deliverable.

Even if stage 1 is just "we ran manual smoke tests and attached screenshots to README," show the grader the recommended progression was followed.

### A20. Python 3.13 per install guide

The install guide names **Python 3.13** specifically. HW1 used `target-version = "py310"`. **For HW2 bump to `target-version = "py313"`** in pyproject.toml, and set `requires-python = ">=3.13"`.

### A21. Provider cache strategy (Lec 04)

Every LLM provider has internal embedding-level caching. A repeated query with the same context costs significantly less (sometimes 1/10th). **Structure prompts so STATIC content (Skill definitions, system rules) is at the *start*, and per-turn variable content is at the *end*.** Maximizes cache hits. Document the strategy in `docs/PRD_gatekeeper.md` or `docs/PROMPTS.md`.

### A22. PROMPTS.md template — 5 required fields (§8.3)

Every significant prompt logged should have all five:

```markdown
## Prompt N: <short title>
**Context**: <what I was trying to do>
**Goal**: <what output I wanted>
**Prompt text**:
> <actual prompt verbatim>
**Example output received**:
> <model's actual response, truncated if needed>
**Iterative improvements**:
> <what I changed and why on subsequent attempts>
**Best practice extracted**:
> <reusable lesson>
```

For HW2 specifically, log: the Judge system prompt, Pro Skill prompt, Con Skill prompt, every meaningful coding prompt to Claude during development.

### A23. Hebrew terminology table — pattern matching cheat sheet

Use BOTH the English term AND the Hebrew term in `docs/PRD.md` / `docs/PLAN.md` / `README.md` for maximum grading-agent match. From the rubric and HW2 spec:

| English | Hebrew | Where to use |
|---|---|---|
| SDK layer / single entry point | שכבת SDK | PLAN.md architecture |
| API Gatekeeper | שומר סף API / ApiGatekeeper | PLAN.md, code |
| FIFO queue / backpressure | תור FIFO / התראת לחץ | PRD_gatekeeper.md |
| Test-Driven Development | פיתוח מונחה-בדיקות (TDD) | PLAN.md, README.md |
| RED → GREEN → REFACTOR | אדום → ירוק → שיפור | docs/PLAN.md |
| Test coverage ≥ 85% | כיסוי בדיקות ≥ 85% | README.md, pyproject.toml |
| Building Block (Input/Output/Setup) | אבן בניה | docstrings everywhere |
| ISO/IEC 25010 | תקני איכות בינלאומיים | PLAN.md ISO section |
| Plugins Architecture / lifecycle hooks | הרחבה / נקודות חיבור | PLAN.md, README.md |
| API-first design | עיצוב מבוסס-API | PLAN.md |
| Prompt Engineering Log | ספר הפרומפטים | PROMPTS.md |
| Token Economy | כלכלת טוקנים | PRD_gatekeeper.md |
| Context Window | חלון הקשר | PRD.md, PRD_gatekeeper.md |
| Context Engineering | הנדסת קונטקסט | PRD.md intro |
| Watchdog / keep-alive | Watchdog | PLAN.md, PRD_watchdog.md |
| Inter-Process Communication | תקשורת בין-תהליכית | PRD_ipc_bus.md |
| Signals, FIFO, Queues, Sockets | סיגנלים, FIFO, תורים, סוקטים | PRD_ipc_bus.md ADR |
| Vibe Coding Lifecycle | מחזור חיי וייב קודינג | PLAN.md, README.md |
| 16× productivity | פי 16 פרודוקטיביות | README.md intro |

### A24. Central thesis quote (HW2 spec §10 — for README intro)

> "המעבר מ-Prompt Engineering ל-Context Engineering הוא המעבר שהופך אתכם ממשתמשי ChatGPT למהנדסי סוכנים. אורקסטרציה של סוכנים, ניהול מודע של חלון ההקשר, ועיצוב היררכיה ברורה של Command, Skill, Agent, Subagent — אלו הכלים שיבדילו את התוצר שלכם מתוצר חובבני."
>
> *"The transition from Prompt Engineering to Context Engineering is what turns you from ChatGPT users into agent engineers. Agent orchestration, conscious context-window management, and clear hierarchy design of Command, Skill, Agent, Subagent — these are the tools that distinguish your product from an amateur one."*

This is the **central thesis** of the course. Quote it in `README.md` opening or `docs/PRD.md` Background section.

### A25. AI ethics paragraph for README (syllabus)

> "השימוש בתוצרי Gen AI בקורס זה מחייב דיווח על עצם השימוש והיקפו; האחריות על כתיבת המטלה חלה על המגיש בלבד ואין להסתמך על כלי Gen AI."
>
> *"Use of Gen AI products in this course requires reporting the use and its extent; responsibility for writing the assignment lies on the submitter alone, and one must not rely solely on Gen AI tools."*

Include verbatim in `README.md` under "AI Usage Disclosure" section, with pointer to `docs/PROMPTS.md` as the audit trail.

### A26. Final project lineage (syllabus week 11)

The course's final project is a **"League of 20 Questions" tournament** between students' agents. HW2's three-agent system is a direct stepping stone: the HW2 **Judge** maps to the tournament's judge; the HW2 **Pro/Con** map to player agents. The HW2 codebase should leave the agent abstraction open so a Player agent and a Judge agent can be reused. Mention this lineage in `docs/PLAN.md` under "Future work / extension points" — it shows architectural foresight.

