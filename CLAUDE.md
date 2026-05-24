# HW2 Worker Session — Orchestration of AI Agents (Course 203.3763)

## Who you are
You are the **HW2 worker session**. The orchestrator session (in `/Users/salah/Projects/orch-ai-agents/`) read all course materials, downloaded everything from Moodle, transcribed all 4 available lectures (5 still in progress), and distilled the rubric. It scaffolded this directory for you:

- **`CLAUDE.md`** (this file) — orientation, the rules, the workflow, gotchas
- **`IDEA.md`** — vibe input you feed into Plan Mode to generate the PRD
- **`RULES.md`** — distilled grading rubric (the source PDF is 39 pages of Hebrew; this is the actionable summary)
- **`CONTEXT-lectures.md`** — digest of lectures 1-4 with Dr. Segal's verbatim phrasing on the workflow + rules
- **`CONTEXT-lecture-05.md`** — digest of lecture 5 specifically (the AUTHORITATIVE HW2 spec). Contradictions with the PDF, the 8 ambiguities resolved, new requirements (H16-H25), and Dr. Segal's philosophy threads
- **`CONTEXT-rubric-and-pdfs.md`** — digest of the rubric PDF + HW2 spec + syllabus + install guide, with verbatim quotes, ambiguity flags, and grading-agent terminology
- **`IDEA-raw.txt`** — raw Hebrew text extraction from the HW2 spec PDF (backup for verbatim quoting)

The user runs you in a separate window. When you finish (or get blocked), they go back to the orchestrator with results.

## Course context
- **Course**: 203.3763 — "Orchestration of AI Agents" (אורקסטרציה של סוכני AI)
- **Institution**: University of Haifa, Spring 2026 (תשפ"ו, semester ב)
- **Lecturer**: Dr. Yoram Reuven Segal — `rmisegal@gmail.com`
- **Today**: orchestrator will inject current date on handoff
- **HW2 deadline**: **Friday, 29 May 2026, 23:59** (Asia/Jerusalem) — assignment id=264177. Opened 15 May 2026. Confirmed by orchestrator on 2026-05-24 ~20:23 — remaining time at that moment was ≈ 5 days 3 hours.
- **Late penalty**: −5 points per 24h (no special request needed)
- **Grade weight**: HW2 ≈ 10% of course (60% homeworks ÷ 6 assignments)

## Previous assignment results
- **HW1 final grade**: **85.54/100** (75.54 pre-bonus + 10 automatic compensation bonus). Below the 92 target.
- **Detailed feedback** is at `../hw1/feedback/Detailed_Feedback_Report.pdf`. **Read it before drafting the PRD.** Concrete transferable lessons:
  - Project planning docs were called out as weak — make `docs/PRD.md` / `docs/PLAN.md` rigorous
  - Config & security portability — the grader should be able to clone, `uv sync`, and run on a different machine with zero hand-holding
  - Extensibility / plugin architecture — must be visible even if not currently used
  - Quality standards automation — pre-commit + CI, not just "ruff was run once"
- **Strengths to keep:** code documentation, testing quality, research depth, UI/UX presentation, continuous git commits, cost awareness, visualization quality.

## The mandatory workflow (Vibe Coding Lifecycle)
Dr. Segal walked through this live in Lecture 1 (~lines 1140–1500). Quotes are verbatim from the transcript (Hebrew → English).

```
Idea → PRD → Plan → TODO → Verify → Execute → README → Run → Push to GitHub
```

The full canonical sequence — **use these prompt phrases verbatim** so Claude recognizes them as the standard lifecycle:

1. **Read context first**: `IDEA.md` → `RULES.md` → `CONTEXT-lectures.md` → `CONTEXT-rubric-and-pdfs.md` → `../hw1/feedback/Detailed_Feedback_Report.pdf` → `../lectures/lecture-05-agents-debate.txt` (when available — this is the **authoritative HW2 spec** and overrides anything else if there's a conflict, per the spec PDF's own note).
2. **Collect user-specific info** (see below).
3. **Enter Plan Mode**: type `/plan` or write *"insert into plan mode"*.
4. **PRD** (`docs/PRD.md`): the master prompt is verbatim *"your mission is to create the following PRD document based on the following description"* followed by bullets distilled from `IDEA.md`. **⚠️ STOP HERE AND GET USER APPROVAL** — rubric §2.5 makes this an explicit gate. The grading agent inspects git timeline for evidence.
5. **Plan** (`docs/PLAN.md`): architecture and technical plan — C4 model, UML sequence diagram for the multi-process IPC flow, **class diagram (mandatory per HW2 spec §8.6)**, ADRs, ISO/IEC 25010 paragraph (using both Hebrew and English term pairs — see RULES.md).
6. **TODO** (`docs/TODO.md`): Dr. Segal's verbatim quote (Lec 1 line 1170): *"מינימום 500 משימות, בדרך כלל 1000 משימות, 900, 800"* — **MIN 500 tasks, typically 800–1000**. The screenshot-circulated "300-800" number was older guidance; use 500-1000.
7. **Per-mechanism PRDs**: `docs/PRD_judge_agent.md`, `docs/PRD_pro_agent.md`, `docs/PRD_con_agent.md`, `docs/PRD_orchestrator.md`, `docs/PRD_ipc_bus.md`, `docs/PRD_gatekeeper.md`, `docs/PRD_watchdog.md`, `docs/PRD_skills.md`, `docs/PRD_web_search_tool.md` — one per significant component, each with Input/Output/Setup docstring shape (rubric §16.3).
8. **⚠️ APPROVAL GATE #2**: get user approval on the **entire docs package** (PRD + PLAN + TODO + per-mechanism PRDs) before any code is written. Rubric §2.5 step 5 makes this explicit.
9. **Verify**: verbatim prompt: *"you must be very critical: check that every PRD requirement appears in TODO. Add missing tasks."* Dr. Segal said this typically adds ~200 missed tasks.
10. **Execute**: verbatim: *"execute the to do list one by one and mark each that was done or complete"*. This marking is what enables session resumption.
11. **README** (`README.md`): verbatim Lec 1 line 1247: *"you must create a readme file — this is the most important thing"* (because you forget what you did).
12. **Run**: verbatim: *"run the project"* — verify it works end-to-end before pushing.
13. **Push to GitHub continuously**: verbatim: *"push to github [public]"*. Continuous commits — Dr. Segal grades commit *density* and *progression*, not just count. **One big-bang push at the end is a significant grade reduction.** He only inspects commits on `main` (Lec 4 line 577).

## User-specific info — pre-populated from HW1 (confirm with user, don't re-ask)

The orchestrator has confirmed the following fields directly from `hw1/uoh-sqak-ex01.pdf` and the user's verbal confirmation. **These are locked; just verify with the user that nothing has changed before using them in `docs/PRD.md` or the submission template.**

| Field | Value | Source |
|---|---|---|
| **Group code** | `uoh-sqak` | HW1 submission; user keeping for semester |
| **Pair status** | **Pair** (not solo) | HW1 was a pair too — orchestrator misremembered earlier |
| **Student 1 (you)** | Salah Qadah / סלאח קדח / ID **323039974** | HW1 submission |
| **Student 2 (partner)** | Andalus Kalash / אנדלוס כלש / ID **211435797** | HW1 submission; user confirmed same partner for HW2 |
| **Repo owner** | `salah-dev-stu` on GitHub (HW1 pattern) — confirm with Andalus | HW1 was `salah-dev-stu/uoh-sqak-ex01` |
| **Repo URL** | `https://github.com/salah-dev-stu/uoh-sqak-ex02` (suggested) | follows HW1 naming |
| **Self-grade placeholder** | `85` | HW1 self-graded 90, actual 85.54 → over-claimed by ~4.5pts. Calibrate down. |
| **Late submission** | `no` (default) | adjust if late |

**Still to ask the user at session start (NOT covered above):**

1. **Andalus's GitHub username** — for repo collaborator invite (HW1 didn't capture it; would help avoid the "not shared" auto-reject)
2. **Debate topic** — free choice. Examples: Barcelona vs Real Madrid, ketogenic vs vegan diet, freshwater vs saltwater fish. Pick before scaffolding so Pro/Con system prompts and the README can be topic-specific.
3. **LLM provider strategy** — Claude CLI (login bundle, the lecturer's default), or API key (cheaper per-token but needs Gatekeeper spend limits), or GLM via Z.AI (cheapest comparable). Mixed providers (Pro on Claude, Con on Gemini) is an interesting "guaranteed contradiction" option.
4. **Pings per side** — default 10 (per spec); reduce to 5 if budget-constrained (allowed per spec §8.7 with README note, no grade deduction).
5. **Resolutions for the 8 ambiguities** in `IDEA.md` (word-count cap, JSON schema, judge intervention threshold, scoring axes, web-search provider, process model, single-vs-multi LLM, etc.). Defaults are provided; user may want to override before PRD locks them in.

A `scripts/fill_submission_pdf.py` script (carried over from HW1 and adapted for ex02) already has Student 1, Student 2, group code, and structure pre-filled. The worker can run `uv run python scripts/fill_submission_pdf.py` at submission time and just verify the auto-filled values match what's in `docs/PRD.md`.

## Quality target — READ THIS

**The user's target is ≥92 overall in the course.** HW1 came in at 85.54 — they're now ~6.5 points below par on the homework average. To recover, HW2 must materially beat HW1's quality. This means:

- **Aim for 90+ on HW2** by genuinely addressing every HW1 weakness, *and* honest self-grade of 85–88
- **TODO must have 800–1000 tasks**, not the 500 minimum
- **Planning docs must be rigorous** — Dr. Segal flagged HW1 planning as weak. Don't repeat that.
- **Architecture diagrams are explicit** — class diagram for OOP layout (mandatory per spec), C4 model in PLAN.md, UML for IPC flow
- **Config portability** — grader on a fresh machine should `git clone && uv sync && menu-up` and have everything work
- **Extensibility shown** — Skill registry, agent factory, plugin pattern; document the extension points
- **Quality automation** — pre-commit hook running ruff + pytest, CI workflow file (even if minimal), coverage threshold in pyproject.toml
- **README reads like a published product manual** — install, usage, examples, configuration, contribution, license
- **Prompt log includes meta-reflections** (`docs/PROMPTS.md`) — not just prompt dumps
- **Continuous commits with meaningful messages** — ideally one per significant TODO completion
- **ISO/IEC 25010 paragraph in PLAN.md** covering all 8 dimensions
- **Building blocks design** (Input/Output/Setup) explicit on every component

When the orchestrator audits before submission, the bar is "would this score 90+ from a strict grading agent?" — not "is this passable?"

## What HW2 actually is — short version

Build **three Python processes** (Judge / Pro / Con) that conduct a structured debate through JSON IPC messages. The Judge moderates, all child↔child traffic goes through the Judge, and the Judge must declare a winner (no ties). Real LLM calls only — no faked dialogue. The orchestration code itself is the deliverable, not just the conversation logs.

Full spec is in `IDEA.md`. Strict requirements are in `RULES.md`. Authoritative source-of-truth is `lectures/lecture-05-agents-debate.txt` when it exists.

## Reference materials available locally (read on demand)

```
~/Projects/orch-ai-agents/
├── hw2/                            ← you are here
│   ├── CLAUDE.md (this file)
│   ├── IDEA.md
│   ├── RULES.md
│   └── (worker writes everything else)
├── hw1/                            ← reference for prior work
│   ├── feedback/
│   │   └── Detailed_Feedback_Report.pdf   ← READ THIS BEFORE PRD
│   ├── docs/                       ← prior PRD/PLAN/TODO as reference style
│   ├── src/sinusoid_extractor/     ← prior code structure (SDK / services / shared layout)
│   └── README.md                   ← prior README style
├── lectures/                       ← whisper transcripts of all 5 lectures
│   ├── lecture-01b-vibe-coding-part2.txt
│   ├── lecture-02-deep-learning.txt
│   ├── lecture-03-rnn-lstm.txt
│   ├── lecture-04-transformer.txt   ← CNN, Transformer, Token Economy, Agent intro
│   ├── lecture-05-agents-debate.txt ← AUTHORITATIVE HW2 SPEC (when transcribed)
│   ├── *.srt                       ← timestamped versions
│   └── *.json                      ← full token-level data
└── materials/
    ├── software_submission_guidelines-V3.pdf  ← the 39-page rubric
    ├── hw2-spec-main-v4-Agents-Subagents-Commands.pdf  ← 8-page HW2 summary
    ├── transformer-book-segal.pdf        ← Dr. Segal's Transformers book
    ├── lecture-04-transformers-presentation.pdf   ← Lec 04 slides
    ├── lecture-04-transformer-booklet.pdf         ← Lec 04 explanation booklet
    ├── lecture-04-transformer-abstract.pdf        ← Lec 04 short abstract
    ├── rnn-book.pdf, lstm-book.pdf, deep-learning-abstract-book.pdf  ← prior reference
    ├── syllabus-2026-semester-b.pdf
    ├── installation-guide.pdf
    └── slides/                     ← misc slide screenshots
```

You may read parent-dir files (`../lectures/`, `../materials/`, `../hw1/feedback/`); ask the user for permission once if Claude Code prompts.

## Top 13 hard rules (the grading agent enforces these — see `RULES.md` for full list)

| # | Rule | Audit |
|---|------|-------|
| 1 | All business logic flows through an SDK layer | Code review |
| 2 | OOP, no code duplication (extract via base class / mixin / Template Method). **Submit class diagram.** | Code review + diagram |
| 3 | All external API calls (LLMs, web search) go through the Gatekeeper class | Code review + test |
| 4 | Rate limits + token budgets in JSON config, never in code | Config test |
| 5 | Versioning: starts at `1.00`, `+0.01` per change, in code AND config | Version module |
| 6 | TDD: Red → Green → Refactor, tests written before/with code | Work process |
| 7 | **≤ 150 lines per Python file** (no comments/blanks counted) | Automated |
| 8 | `ruff check` returns zero failures (line-length 100, py310+, rules E/F/W/I/N/UP/B/C4/SIM, ignore E501) | ruff |
| 9 | `pytest --cov` ≥ **85%** coverage (`fail_under = 85` in pyproject.toml) | pytest |
| 10 | **Zero hardcoded values** in source — everything via config | Code review |
| 11 | Zero secrets in code — `.env-example` + `os.environ.get(...)`, `.env` git-ignored | Auto scan |
| 12 | `uv` is mandatory — pip / `python -m` / `pip install` / venv / virtualenv all FORBIDDEN. Everything via `uv run`, `uv sync`, `uv add`, `uv lock` | Auto |
| 13 | Continuous git commits with meaningful messages — one big push at the end is heavily penalized | Git history audit |

## HW2-specific additions to the rule set (from the spec)

| # | Rule | Audit |
|---|------|-------|
| H1 | **Real LLM calls only** — no faked or scripted dialogue. The debate must be genuine multi-turn LLM conversation. | Code + logs |
| H2 | **JSON wire protocol** between agents — structured, parseable, monitorable | Code + logs |
| H3 | **≥10 pings per side** (or 5 with explicit budget reason in README) | Logs |
| H4 | **All traffic through Judge** — children never communicate directly | Code review |
| H5 | **Judge declares winner** — no ties allowed | Behavior test |
| H6 | **Internet search tool** is required and used | Code + logs |
| H7 | **Watchdog + keep-alive** — if a child dies, kill remnants, restart | Code review |
| H8 | **Timeouts on every LLM call** | Code review |
| H9 | **Terminal menu** — operable from keyboard with no GUI | Manual test |
| H10 | **Pairs only** (HW2 spec) — solo requires explicit pre-approval from rmisegal@gmail.com | Submission check |
| H11 | **Hebrew or English** dialogue, not Arabic — Dr. Segal needs to read it | Sample log check |

## Required project layout

```
hw2/
├── src/
│   └── <package>/                 ← name it after the project, e.g. agent_debate
│       ├── __init__.py            ← MUST define __version__ and __all__
│       ├── sdk/                   ← public single-entry SDK
│       │   ├── __init__.py
│       │   └── sdk.py
│       ├── agents/                ← Pro / Con / Judge agent classes
│       │   ├── __init__.py
│       │   ├── base_agent.py      ← shared base class (OOP, no duplication)
│       │   ├── judge_agent.py
│       │   ├── pro_agent.py
│       │   └── con_agent.py
│       ├── orchestration/         ← process spawn, IPC bus, watchdog
│       │   ├── __init__.py
│       │   ├── orchestrator.py
│       │   ├── ipc_bus.py
│       │   └── watchdog.py
│       ├── skills/                ← Pro Skill, Con Skill, Judge Skill — markdown + helper Python
│       │   ├── __init__.py
│       │   ├── pro_skill/
│       │   ├── con_skill/
│       │   └── judge_skill/
│       ├── tools/                 ← search tool, citation formatter, etc.
│       │   ├── __init__.py
│       │   └── web_search.py
│       ├── shared/                ← cross-cutting concerns
│       │   ├── __init__.py
│       │   ├── gatekeeper.py      ← API gatekeeper (token budget, rate limits, retry policy)
│       │   ├── config.py          ← config loader
│       │   ├── logging_fifo.py    ← FIFO log rotation
│       │   └── version.py         ← __version__ tracker
│       ├── menu/                  ← terminal menu
│       │   ├── __init__.py
│       │   └── tui.py
│       ├── constants.py           ← project constants + Enums
│       └── main.py                ← CLI entry point
├── tests/
│   ├── unit/                      ← mirror src/ structure
│   ├── integration/               ← end-to-end debate runs with mock LLM
│   └── conftest.py                ← shared fixtures (mock LLM, mock search tool)
├── docs/
│   ├── PRD.md                     ← MANDATORY (root product requirements)
│   ├── PLAN.md                    ← MANDATORY (architecture & technical plan + ISO 25010 paragraph)
│   ├── TODO.md                    ← MANDATORY (≥500 tasks, [x] completed)
│   ├── PRD_judge_agent.md         ← per-mechanism PRDs
│   ├── PRD_pro_agent.md
│   ├── PRD_con_agent.md
│   ├── PRD_orchestrator.md
│   ├── PRD_ipc_bus.md
│   ├── PRD_gatekeeper.md
│   ├── PRD_watchdog.md
│   ├── PRD_skills.md
│   ├── PRD_web_search_tool.md
│   ├── PROMPTS.md                 ← Prompt Engineering Log: every prompt + why + iterations
│   ├── ADRs/                      ← Architecture Decision Records
│   └── diagrams/                  ← C4 / UML / class diagram (mandatory per HW2 spec)
├── config/
│   ├── setup.json                 ← versioned ("version": "1.00")
│   ├── agents.json                ← per-agent configuration (model, temperature, skill ref)
│   ├── debate_rules.json          ← pings per side, timeout, word limit, etc.
│   ├── rate_limits.json           ← LLM + search-tool rate limits (versioned)
│   └── logging_config.json        ← FIFO log config (file count, lines per file)
├── logs/                          ← FIFO-rotated structured logs (git-ignored bulk)
├── transcripts/                   ← saved JSON dumps of past debates
├── assets/                        ← screenshots, architecture diagram exports
├── README.md                      ← MANDATORY (full user manual + screenshots + session-1 dialogue)
├── pyproject.toml                 ← uv config, ruff config, pytest+coverage config
├── uv.lock                        ← MUST exist and be tracked in git
├── .env-example                   ← committed; placeholder values (CLAUDE_API_KEY, SEARCH_API_KEY, etc.)
├── .env                           ← git-ignored
├── .gitignore                     ← includes .env, *.key, *.pem, credentials.json, logs/*.jsonl
└── .pre-commit-config.yaml        ← ruff + pytest hooks (HW1 missed this — don't repeat)
```

## Submission process (last steps)

1. Final code + README + transcripts committed and pushed to GitHub (public OR shared with `rmisegal@gmail.com`).
2. Open the submission template (orchestrator will copy `uoh-rl07-ex01.docx` from hw1/ as a starting point). **Do not change the field structure.** Fill in:
   - Submitting an exercise number: **02**
   - Group ID code: **`uoh-sqak`** (or whatever the user confirmed)
   - Recommendation for self-scoring: **85** (placeholder; orchestrator will calibrate after audit)
   - Student 1: ID, English first/last name, Hebrew first/last name (Salah Qadah / סלאח קדח)
   - Student 2: partner's details (or blank if solo + permission obtained)
   - Link to GitHub: (repo URL — must be accessible)
   - Late submission confirmation: yes/no
3. Save as PDF named `uoh-sqak-ex02.pdf`.
4. Upload to Moodle assignment id=264177.
5. **Each pair member submits separately** — submission timestamp is per-individual.

## Gotchas / Dr. Segal's pet peeves

- **Don't dump the rubric PDF into your context.** It's Hebrew, ~30k tokens. Use `RULES.md` instead, and only Read specific pages of the PDF if you need a verbatim quote.
- **TODO.md must be exhaustive.** 500 tasks is the floor. Dr. Segal said anything less means you're skipping things. Aim for 800.
- **Continuous commits.** Push after each completed major task. The grader looks at history density.
- **`uv run` for everything.** Even pytest: `uv run pytest`. Even running the script: `uv run python -m agent_debate.main`.
- **150 lines is strict.** When a file gets long, split. Don't shrink whitespace to dodge the limit; the lecturer's agent looks for that and penalizes.
- **Children never talk directly.** Every Pro→Con and Con→Pro message MUST go through the Judge. The Judge is the bus + the arbiter.
- **No ties.** The Judge MUST decide. Differential scoring (Pro 65 / Con 80) is fine; a "they're both right" cop-out is disqualifying.
- **Real LLM calls.** If a grader sees random.choice() in the debate flow, you fail. The dialogue must come from actual LLM responses.
- **The README is half the grade.** Screenshots, prompts, session-1 dialogue dump, architecture diagram embedded. Treat it as a published product manual.
- **Dr. Segal wants analysis, not perfect debates.** A losing strategy that you analyze well > a winning strategy you don't explain.

## Tools the lecturer expects
- **Claude CLI** (this is you) — Login auth preferred, NOT API key (saves the user's quota)
- `uv` — package manager (mandatory)
- `ruff` — linter
- `pytest` + `pytest-cov`
- `git` + GitHub
- `jupyter` — optional for HW2 (no analysis notebook required), but helpful for transcript exploration
- The user is on macOS, so plain terminal is fine

## Lecturer contact (use sparingly, only if truly stuck)
- **Email**: `rmisegal@gmail.com`
- **Office hours**: Mondays 20:00–21:00 via Zoom (advance booking required via the lecturer's Google Calendar)
- **AI ethics policy**: from the syllabus — "use of Gen AI must be reported, including the extent of use. Responsibility for the assignment lies with the submitter alone." Add a brief paragraph in the README acknowledging that AI agents (you) generated parts of the code, with the prompt log in `docs/PROMPTS.md`.

## Reporting back

This worker session has no direct channel to the orchestrator. When you finish a major milestone (PRD done, Plan done, code complete, repo pushed), surface a clear summary so the user can copy-paste it back to the orchestrator. The orchestrator session will:
- Spot-check the deliverables
- Suggest fixes targeting the HW1 weak areas specifically
- Confirm the submission PDF before upload

## First action — required reading order

Before asking the user anything or drafting any document, read these files in this exact order:

1. **`IDEA.md`** (this dir) — what HW2 is, distilled from the spec PDF
2. **`RULES.md`** (this dir) — the grading rubric, audit gates, terminology to use verbatim
3. **`CONTEXT-lectures.md`** (this dir) — Dr. Segal's verbatim workflow + 4 prior lectures' digest
4. **`CONTEXT-lecture-05.md`** (this dir) — **THE most important context file.** Lecture 05 was authoritative for HW2 per the spec PDF itself. This digest has the contradictions with the PDF, all 8 ambiguities resolved, new requirements H16-H25, and Dr. Segal's philosophy threads. Read carefully.
5. **`CONTEXT-rubric-and-pdfs.md`** (this dir) — full rubric breakdown, HW2 spec verbatim quotes, syllabus, ambiguity flags + suggested defaults
6. **`../hw1/feedback/Detailed_Feedback_Report.pdf`** — the lecturer's HW1 feedback. **This is your checklist of what to fix.** Read with `pdftotext -layout`.
7. **`../lectures/lecture-05-agents-debate.txt`** — the authoritative HW2 spec from the recording (2114 lines, Hebrew). Read this directly if `CONTEXT-lecture-05.md` references a passage you want verbatim. Per the spec PDF itself: *"In any contradiction between this summary and what is said in the lecture (as appears in the recording), the lecture instructions override."*

Then:

7. Ask the user for the **7 placeholder fields** (group code, pair partner with name+ID, GitHub user, target self-grade, student ID, debate topic, LLM provider strategy). See the "User-specific info" section above for the full list.
8. Acknowledge constraints and ask any clarifying questions about the **8 ambiguities** flagged in `CONTEXT-rubric-and-pdfs.md` §2.9 (word-count cap, JSON schema, judge intervention threshold, persuasiveness scoring axes, web-search provider, process model, single-vs-multi LLM provider, pair vs solo for HW2 specifically).
9. **Enter Plan Mode** (`/plan` or "insert into plan mode") and begin the Vibe Coding lifecycle.

**Do not start writing code until PRD + PLAN + TODO + per-mechanism PRDs are approved by the user — this is two explicit approval gates per rubric §2.5.**
