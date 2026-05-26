# Prompt Engineering Log — HW2 Multi-Agent Debate System

> Audit trail of every meaningful design prompt and decision. Required by rubric §8.3 and §A22 (five-field template: Context, Goal, Prompt text, Example output, Iterative improvements, Best practice extracted). Required by syllabus AI ethics policy: "use of Gen AI products in this course requires reporting the use and its extent."

**Project**: HW2 — Multi-agent debate system (course 203.3763, Spring 2026)
**Pair**: Salah Qadah (323039974) + Andalus Kalash (211435797), group code `uoh-sqak`
**Authoring agent**: Claude Opus 4.7 (claude-opus-4-7), via Claude Code CLI
**Authoring session start**: 2026-05-24

---

## Prompt #1: Context ingestion

**Context**: First action of the HW2 worker session. CLAUDE.md mandates a required reading order (IDEA.md → RULES.md → CONTEXT-lectures.md → CONTEXT-lecture-05.md → CONTEXT-rubric-and-pdfs.md → ../hw1/feedback/Detailed_Feedback_Report.pdf) before any clarifying questions.

**Goal**: Build a complete mental model of: (a) what HW2 is, (b) the audit gates the grading agent enforces, (c) the four HW1 weak spots to correct, (d) Dr. Segal's verbatim phrasing and pet peeves.

**Prompt text**: User's first turn after the SessionStart hook fired: `"read and understand"`.

**Example output received**: Concise summary identifying the four HW1 weak spots (Project Planning, Configuration & Security, Extensibility, Quality Standards) and the non-negotiable gates (≤150 lines/file, uv only, ruff 0 errors, coverage ≥85%, class diagram mandatory per HW2 spec §8.6, Judge topic-blind, mixed providers encouraged, manual Phase 1 with screenshots, cost analysis mandatory for HW2).

**Iterative improvements**: The orchestrator session had pre-distilled 6 context files (RULES.md, CONTEXT-*.md) to avoid pushing the full 39-page Hebrew rubric PDF into the worker's context — this was the right call; reading the source PDFs took ~30k tokens just for context, whereas the distillations are ~7k.

**Best practice extracted**: For Hebrew/RTL-heavy source documents, generate an English distillation in a separate session and read the distillation in the working session. Saves tokens + keeps the working context window focused.

---

## Prompt #2: Brainstorming activation

**Context**: After context ingestion, before asking the user any clarifying questions, the user typed `/brainstorming` to invoke the superpowers brainstorming skill. The skill mandates: explore project context → ask clarifying questions one at a time → propose 2-3 approaches → present design in sections → write design doc → user reviews → invoke writing-plans.

**Goal**: Drive a structured design conversation that ends in an approved spec, before writing any code (rubric §2.5 step-1 and step-5 are explicit user-approval gates).

**Prompt text**: User: `"/brainstorming"`.

**Example output received**: Skill activated. Created 8 brainstorming checklist tasks (Explore context → Ask questions → Propose approaches → Present design → Write doc → Self-review → User review → Invoke writing-plans).

**Iterative improvements**: First attempt tried to ask 4 clarifying questions in one `AskUserQuestion` call — user interrupted to invoke `/brainstorming` retroactively. Lesson: respect the "one question per message" rule the skill mandates, even when the questions feel batchable.

**Best practice extracted**: When a workflow skill mandates one-question-per-message, do not optimize for round-trip count — the skill is shaped this way to keep the user in control of each decision.

---

## Prompt #3: Decision Q1 — LLM provider strategy

**Context**: The most architecture-shaping decision. Determines what API adapters live in the codebase, what env vars the grader needs, whether the H23 "mixed providers" creativity bonus is available, and what failure modes the Gatekeeper must handle.

**Goal**: Lock the LLM provider mix before designing the agent class hierarchy.

**Prompt text**: Four-option multi-choice — (1) Mixed: Pro=Claude, Con=Gemini, Judge=Claude [recommended for H23 bonus]; (2) Claude-only login auth; (3) Claude-only API key; (4) GLM via Z.AI.

**Example output received**: User chose **Claude-only via login auth (CLI bundle)**. Rationale: zero API spend, uses existing Claude CLI bundle.

**Iterative improvements**: My initial recommendation was the mixed-provider option (strongest lecturer-signal). User overrode for budget reasons — accepted, but trade-off documented: same-provider debaters tend to auto-agree (H8 risk). Mitigation strategy: hard-differentiated Skills with stance-emphatic system prompts, temperature spread (Pro 0.85, Con 0.85, Judge 0.30), and adversarial drift-detection inside the Judge process.

**Best practice extracted**: When the user overrides the model recommendation, articulate the now-active risk explicitly + propose mitigations in the same message. The audit trail then shows the trade-off was conscious, not blind.

---

## Prompt #4: Decision Q2 — Debate topic

**Context**: Topic shapes Skill content, web-search queries, README session-1 sample, and the lecturer's reading experience. Originality is bonus-graded; PC violations are auto-disqualifying (H12).

**Goal**: Pick a topic that is genuinely contested, web-searchable on both sides, PC-safe, and memorable (originality bonus).

**Prompt text**: First attempt offered 4 typical topics (Barcelona vs Real Madrid, Keto vs Vegan, Freshwater vs Saltwater fish, Cats vs Dogs). User picked Cats vs Dogs initially.

**Iterative improvements**: User reversed: *"wait, lets change topics, give me something interesting, search the web for a good non typical topic"*. Did web search on unconventional debate topics. Returned 4 non-typical options: (1) Meta — *Can AI agents create genuinely original art?* [recommended for originality bonus]; (2) Is a hot dog a sandwich?; (3) Was Pluto's demotion correct?; (4) Could humans delete painful memories?

**Example output received**: User chose **"Can AI agents create genuinely original art, or only remix human work?"**. Stance assignment: Pro = AI=originality, Con = AI=remix-only. Meta-topic — AI agents debating their own creative capability.

**Best practice extracted**: When a user asks for "something interesting", do not assume their first-pass acceptance was their preference. The reversal here turned a generic Cats-vs-Dogs into a course-specific meta-debate that maps directly onto the lecturer's domain — high creativity-bonus payoff. For future Q's, lead with non-typical options on the menu and let the user pick the safer fallback if they want.

---

## Prompt #5: Decision Q3 — Pings per side

**Context**: H3 mandates ≥10 pings/side; spec §8.7 allows 5 with a README note (no grade deduction). With Claude-login (no per-token cost), the constraint is rate limits, not money.

**Goal**: Lock debate length.

**Prompt text**: Two-option choice — 10 (spec default, no README excuse) [recommended] vs 5 (with explicit README budget note).

**Example output received**: User chose **10 pings/side**.

**Best practice extracted**: When two options differ only in deliverable scope (not architecture), the recommendation should weight "meet the spec directly without footnotes" higher unless there's a real budget reason to footnote.

---

## Prompt #6: Decision Q4 — Web-search backend

**Context**: H6 makes web-search a graded enforcement gate (*"absent web-search = automatic point loss"* per lec05 L1233-1239). The agents need it for both citation and opponent fact-checking (H24, dual purpose).

**Goal**: Pick a backend the grader can run with zero friction.

**Prompt text**: Four-option choice — DuckDuckGo via `ddgs` (no API key, recommended); Brave Search API (free tier, needs signup); Tavily ($0.01/query, $10 free credit); pluggable design with DDG default.

**Example output received**: User chose **DuckDuckGo via `ddgs`** — zero-config, no key, grader can run instantly.

**Iterative improvements**: The "pluggable design" option I listed (DDG default + Brave/Tavily plug-in) was probably the right architectural recommendation given HW1 was weak on extensibility. Capturing this for revision: the `SearchProvider` interface should still be abstract even though we default to DDG, so swapping in Brave is a config change, not a code change. Updating in the design doc.

**Best practice extracted**: When a question is framed as "pick a backend", the implicit question is also "should this be pluggable?" — answer both, even if only one is asked.

---

## Prompt #7: Decision Q5 — IPC architecture (Approach 1/2/3)

**Context**: Lec05 L399 enumerates four IPC primitives (Signal, FIFO, Queue, Sockets) and Dr. Segal expects an ADR justifying the choice. Three viable approaches: pure multiprocessing.Queue (conservative), subprocess.Popen + JSON-lines (simplest), mixed primitives (showcase).

**Goal**: Pick the IPC mechanism before designing the agent class hierarchy.

**Prompt text**: Three-option choice with explicit recommendation for Approach 1 (multiprocessing.Queue) on grounds of: (a) matches lecturer's most-named primitive, (b) true OS processes satisfy the spec, (c) 5-day deadline favors low-risk implementation over showcase complexity, (d) ADR can still enumerate all 4 primitives to capture the breadth signal.

**Example output received**: User chose **Approach 1 — pure multiprocessing.Queue**.

**Best practice extracted**: When three approaches differ on a complexity↔originality axis, the deadline pressure should be a first-class factor in the recommendation, not an afterthought. HW1's lesson was over-promising scope.

---

## Prompt #8: Design §1 — initial architecture proposal

**Context**: Brainstorming skill mandates "Present design in sections, get approval after each section."

**Goal**: Walk through architecture overview, get approval before moving to §2 (components).

**Prompt text**: Proposed 7-layer architecture diagram with: terminal menu (letter-keyed), SDK (sole entry point), orchestrator (spawns + Watchdog + LifecycleRegistry), agents (Judge + Pro + Con + BaseAgent), Gatekeeper + tools, project-local Skills + structured logger.

**Example output received**: User asked me to **revise and propose improvements**.

**Iterative improvements (Self-critique applied)**: Identified 7 gaps in initial §1: (A) two-phase boot invisible — H18 requires Judge to send `setup_directive` messages and wait for ack before debate loop; (B) lifecycle hooks unnamed — rubric §12.1 demands explicit names; (C) cross-process spend not shared — global token budget needs `multiprocessing.Value` + Lock; (D) Judge scoring criteria not web-sourced — N7 lecturer-specific request; (E) drift detector + PC filter unnamed as Judge sub-modules; (F) structured FIFO logger missing from layer 7; (G) test seam `BaseAgent.step()` not declared.

**YAGNI cuts**: Multi-skill per agent (defer to PLAN.md Future Work), compaction strategy (math says we won't bust context at this scale — 250 words × 20 turns × 3 voices ≈ 20K tokens vs Claude's 200K), socket-based watchdog (3rd primitive nice-to-have but adds macOS portability risk).

**Best practice extracted**: After presenting a design section, do a self-critique pass with the same lens the grader will use. The user's "revise" prompt was an invitation to find the gaps myself rather than wait for the user to spot them.

---

## Prompt #9: Skills design — web research + three-skill proposal

**Context**: User asked: *"add skills for each type, search the web on how and the best practices."* Skills are H17-mandated project-local; rubric expects idiomatic `.claude/skills/` structure.

**Goal**: Design the three skill directories (pro_skill, con_skill, judge_skill) per Anthropic's official skill-authoring best practices.

**Prompt text**: Three parallel web searches — Claude Code skill best practices; Agent SDK skill structure (progressive disclosure, frontmatter); persona/stance design in markdown body.

**Example output received**: Comprehensive best-practice summary (third-person descriptions, "pushy" trigger phrasing, 1500-2000 word bodies, scope+testing-expectations at top, progressive disclosure of references via filesystem on demand).

**Iterative improvements**: Generated three skill directory designs with frontmatter + body sketches. Pro skill argues AI=originality (Klingemann, Edmond de Belamy auction, transformative-use doctrine); Con skill argues AI=remix-only (Stochastic Parrots paper, NYT v OpenAI, Getty v Stability AI, Chinese Room); Judge skill is **topic-blind (H19)** and pulls scoring criteria from `references/debate_criteria.md` which is **generated by `scripts/build_judge_criteria.py` (N7 originality)** — a one-off pre-flight that web-searches for "parliamentary debate / Lincoln-Douglas / Robert's Rules" and persists the synthesized criteria.

**ADR-002 introduced**: Skills loaded statically as system prompts (not Claude-auto-discovered). Each child process reads its assigned SKILL.md body via filesystem on boot and passes it as `--append-system-prompt` to `claude -p`. The Claude-Code skill format gives idiomatic file structure the grader recognizes; the frontmatter doubles as machine-readable metadata.

**Best practice extracted**: When a user invokes a skill mid-design ("search the web on best practices"), the answer is rarely just "here's what I found" — it's "here's what I found AND here's what to do with it in our specific project." Combine the findings with concrete file proposals in the same message.

---

## Prompt #10: User feedback — "show the work"

**Context**: After §1 revisions and the three-skill design, user said: *"Okay. Okay. But you see all of this? We need to write PRD to do plan and progress the plan. And, you know, progress that you do. This is part of the job. what we are doing right now, we need to show it."*

**Goal**: Capture the brainstorming conversation as committed file artifacts NOW, not at the end. The audit trail must be visible incrementally — Dr. Segal explicitly grades commit density and progression over time (lec01 L270-289, lec04 L132-141, L559).

**Prompt text**: Direct user feedback — no question, just an instruction to bake the design into files.

**Example output received**: This file (`docs/PROMPTS.md`) — every decision so far captured with the five-field template. Followed by `docs/superpowers/specs/2026-05-24-hw2-debate-design.md` (in-progress design doc) and a git init + first commit.

**Best practice extracted**: Brainstorming is a deliverable, not a precondition to deliverables. The five-field PROMPTS template (rubric §A22) is the natural place to capture in-flight design rationale — it doubles as the audit trail Dr. Segal demands AND as documentation for future-me who'll forget the trade-offs in two weeks.

---

## Decisions locked (running list)

| # | Decision | Locked at | Source |
|---|----------|-----------|--------|
| 1 | LLM provider: Claude-only via login CLI | Prompt #3 | User |
| 2 | Debate topic: *"Can AI agents create genuinely original art, or only remix human work?"* | Prompt #4 | User |
| 3 | Pro = originality side; Con = remix-only side | Prompt #4 | Recommended |
| 4 | Pings per side: 10 | Prompt #5 | User |
| 5 | Web search: DuckDuckGo via `ddgs` (pluggable interface) | Prompt #6 | User |
| 6 | IPC: `multiprocessing.Process` + `multiprocessing.Queue` | Prompt #7 | User |
| 7 | Word cap per turn: 250 words | Lecture default | Lec05 default |
| 8 | Drift threshold: 1 (per-message check + correct_and_replay) | Lecture default | Lec05 L1182-1184 |
| 9 | Scoring: 5 axes × 20 = 100 (clarity, evidence, rebuttal, novelty, role-fidelity) | Lecture default | Lec05 L1576 |
| 10 | Logging: FIFO 20 files × 500 lines structured JSON | Spec default | HW2 spec §8.6 |
| 11 | Judge scoring criteria sourced via web-search pre-flight (N7) | Design choice | Lec05 L1519-1528 |
| 12 | Skills: project-local under `.claude/skills/`, loaded statically as system prompts (ADR-002) | Design choice | H17 + Prompt #9 |
| 13 | Pair: Salah Qadah + Andalus Kalash (group `uoh-sqak`) | Pre-confirmed | HW1 submission |

---

---

## Prompt #11: Design §2 — Components (class hierarchy + per-mechanism PRDs)

**Context**: After §1 architecture and the three-skill design were locked, brainstorming flow moved to §2 (components). Rubric §A13 requires every significant class to follow the building-block docstring shape (`Input:` / `Output:` / `Setup:`). HW1 was specifically flagged on extensibility — §2 must name concrete extension points.

**Goal**: Lock the class hierarchy, mixin set, factory/registry patterns, and the 9 per-mechanism PRDs that will sit under `docs/`.

**Prompt text**: Presented the full agent hierarchy (`BaseAgent` → `PartisanAgent` → `ProAgent`/`ConAgent`; `BaseAgent` → `JudgeAgent`), 4 orthogonal mixins (`LoggingMixin`, `LifecycleMixin`, `HeartbeatMixin`, `RetryMixin`), the `ApiGatekeeper` matching rubric §A4 signature verbatim, `LLMProvider` + `SearchProvider` plugin interfaces with factory registry, the 8-hook `LifecycleRegistry`, `DebateOrchestrator`, `Watchdog`, `DebateSDK`, and letter-keyed terminal menu. Plus a table of 9 per-mechanism PRDs (judge, pro, con, orchestrator, ipc_bus, gatekeeper, watchdog, skills, web_search_tool) with target line counts (~150-250 each).

**Example output received**: User responded *"ok proceed"* — approval. Three open clarifying questions I had asked (whether RetryMixin lives outside Gatekeeper, `max_restarts=3` threshold, `simulate_keystroke()` naming) didn't get explicit answers, so I applied my own defaults: retry consolidated into Gatekeeper (dropped `RetryMixin`), `max_restarts=3` kept, `simulate_keystroke()` kept.

**Iterative improvements**: My initial mixin list had `RetryMixin` — but that splits retry policy across two locations (Gatekeeper had its own retry logic). Consolidated: ONE retry policy lives in Gatekeeper, mixins shrink to 3 (Logging, Lifecycle, Heartbeat). Cleaner.

**Best practice extracted**: When a user accepts a section with "ok" without answering the trailing open questions, default to the recommendations you flagged as preferred — and log the defaults explicitly here so the audit trail shows the calls were made consciously, not silently.

---

## Prompt #12: Design §3 — Data flow + JSON wire protocol

**Context**: H2 mandates JSON wire format. Lec05 L1437-1444 quotes Dr. Segal: *"JSONs are templates"* — JSONs map directly to the lecturer's "LLM converts free text into TEMPLATES" thesis (Lec04 §8). The protocol must support the H18 setup_directive, H20 per-message drift check, H16 PC filter, H4 child→father→child routing, and H5 no-tie verdict.

**Goal**: Lock the JSON wire schema, message roles, single-ping sequence diagram, two-phase boot timeline, and agent state machines.

**Prompt text**: Presented the full schema file (`config/schemas/message-1.00.json` versioned, jsonschema-validated at every send/recv), 8 message roles (`setup_directive`, `ack`, `argument`, `counter`, `correction_request`, `intervention`, `status`, `verdict`), single-ping sequence diagram (Pro → Judge → validate → forward to Con), two-phase boot timeline (T+0 spawn → T+0.5 acks received → T+5min verdict), state machines for both Pro/Con and Judge, mutual-reference enforcement via `references_opponent` schema flag, transcript persistence.

**Example output received**: User responded *"ok"* — approval.

**Iterative improvements**: First draft of message roles had 6; added `ack` (for setup_directive confirmation, H18) and `intervention` (separate from `correction_request`, since the H16 PC filter is a distinct concern from H20 drift detection). The two should not be conflated — the action is different (intervention sanitizes content; correction_request requests a stance-faithful replay).

**Best practice extracted**: When the lecturer's specific rules (H16, H18, H20) map to discrete checks, each gets its own message role — even if the schema then has 8 roles instead of 4. Conflating reduces clarity and makes the audit logs harder to grep for "which check fired."

---

## Prompt #13: Design §4 — Error handling + Watchdog

**Context**: H21 explicitly graded. The chaos test from rubric §6.3 will deliberately `kill -9` a child mid-debate. H10 requires timeouts on every LLM call. The Gatekeeper must enforce budget caps with 75%/95% thresholds per rubric §A8.

**Goal**: Catalog every failure mode, name detection mechanism + action, design the Watchdog with heartbeat contract + state replay on restart, lock the graceful shutdown cascade.

**Prompt text**: Presented a 13-row failure-mode catalog (per layer: LLM provider, web search, IPC bus, child process, budget, user). Watchdog design with `poll_interval=2s`, `stuck_timeout=30s`, `max_restarts=3` with exponential backoff `[1, 2, 4]`. Heartbeat contract: each child fires `status` every 2s; missed heartbeats beyond timeout trigger `SIGKILL` + respawn with state replay (re-inject shared spend + skill_dir + most-recent `setup_directive`). Graceful shutdown cascade on SIGINT/SIGTERM. 10 chaos-test edge cases with explicit verification criteria.

**Example output received**: User responded *"ok, but all of this we are showing right? the planning, we need to get points"* — reinforced the meta-instruction that the brainstorming is itself the deliverable. Triggered the current commit cycle.

**Iterative improvements**: Initial draft had Watchdog detecting "hung" children purely via `is_alive()`. Refined: `is_alive()` only catches crashed processes; hung-but-alive processes need the heartbeat-timeout check. So the Watchdog has two parallel detectors (`Process.is_alive()` + `last_heartbeat_age > stuck_timeout`). Both must agree before SIGKILL to avoid false-positives.

**Best practice extracted**: Failure detection that depends on a single signal (e.g. `is_alive()` alone) misses orthogonal failure classes (crashed vs hung). Two-signal detection (alive-check + heartbeat-staleness) covers the union without requiring either signal to be perfect.

---

## Prompt #14: Recurring user feedback — "the planning is graded, show it"

**Context**: For the second time, the user pushed back that the brainstorming work needs to be visible in the repo, not only in conversation. The first push (Prompt #10) triggered the initial commit and the in-progress design doc + PROMPTS.md scaffold. After §3-§4 were presented purely in conversation, the user repeated: *"ok, but all of this we are showing right? the planning, we need to get points"*.

**Goal**: Treat every approved section as a committable artifact. The pattern: approve in conversation → write to spec doc → log in PROMPTS.md → commit. Section completion is not just verbal approval, it's the file landing.

**Prompt text**: The user's reminder — short, sharp, twice now.

**Example output received**: This entry plus prompts #11-13 above, plus a §2-§4 expansion of the design doc, plus a commit.

**Best practice extracted**: When the user has had to remind me twice that conversation alone isn't the deliverable, lock the rhythm: after EVERY section approval, run a quick capture cycle before moving forward. Don't let three sections pile up before committing again. Mid-section, the spec doc gains a "WIP" marker so it's always parseable.

---

---

## Prompt #15: Design §5 — Testing strategy

**Context**: HW1 was rated *strong* on Testing Quality — keep that bar. Rubric §6.1 has 7 enumerated TDD rules; H17 + rule 7 forbid live external services in tests; rubric §A8 demands budget-threshold tests; HW1's biggest *weak* spot was Quality Standards — a CI/pre-commit pipeline fixes that.

**Goal**: Lock the test pyramid (unit / integration / e2e), enumerate ~124 unit tests across 13 files, ~9 integration scenarios with H-gate cross-references, ~3 E2E tests gated by `RUN_E2E=1`, CI workflow, pre-commit config, file-line enforcer script, and fixture surface.

**Prompt text**: Presented test pyramid ASCII diagram; per-file unit-test counts with mocked LLM/search via `tests/conftest.py`; integration scenarios mapped explicitly to H1-H21 audit gates; E2E tests for the real-Claude path; `.github/workflows/ci.yml` minimal config; `.pre-commit-config.yaml` (HW1 missed this); `scripts/check_file_lines.py` enforcer that also flags `line > 100 chars + no comments` to catch whitespace games the lecturer's agent looks for; fixture set covering mock LLM, mock search, temp skill dir, shared spend Value/Lock, canned transcripts.

**Example output received**: User responded *"ok"* — approval.

**Iterative improvements**: First draft had `pytest-cov` running on all 136 tests in pre-commit — way too slow (~minutes). Refined: pre-commit only runs unit (`tests/unit -x -q`); CI runs unit + integration with coverage; E2E gated on env var. Three-tier gating matches the cost/speed of each layer.

**Best practice extracted**: Test strategy must respect the developer feedback loop. Pre-commit = sub-second runs (unit only). CI = minutes (unit + integration). E2E = real-money calls, opt-in only. A pre-commit hook that runs slow tests teaches developers to `--no-verify`, which is worse than no hook.

---

## Prompt #16: Spec self-review pass

**Context**: Brainstorming skill step 7: "look at the spec doc with fresh eyes" — placeholder scan, internal consistency, scope check, ambiguity check. Fix inline.

**Goal**: Find and resolve gaps before the user reviews the spec, so the user-review gate has a clean artifact to evaluate.

**Prompt text**: Internal pass — no user prompt. Applied four-axis review.

**Example output received (findings + fixes)**:

1. *Placeholder scan*: stance assignment was implicit in §2 but missing from §0 quick-reference table → added stance row. `LLMResponse` and `SearchHit` types referenced but never defined → added DTO cheatsheet in §7.5. Token budget mentioned without a number → added concrete config (`tokens_per_debate=200000`, warn at 75%, hard cap at 95%).

2. *Internal consistency*: cross-referenced class hierarchy in §3 against state machines in §4 — match. Watchdog `max_restarts=3` consistent §4 ↔ §5. Lifecycle hooks named in §3 match the 8 listed elsewhere — match.

3. *Scope*: large but coherent. Fits a single 4-day execution window — no decomposition required. Estimated artifacts: ~500-line PRD, ~800-line PLAN, 800-1000 task TODO, 9 per-mechanism PRDs of ~150-250 lines each, ~20-30 .py files at ≤150 lines, ~136 tests.

4. *Ambiguity*: "claude -p exact flags" was open → added verbatim command in §7.5. DriftDetector mechanism ambiguous (regex vs LLM-based?) → locked to stance-keyword regex (deterministic, no extra LLM cost). Token budget numbers were qualitative → added rate_limits.json concrete values.

**Best practice extracted**: The self-review pass is where you find the assumptions you didn't realize you were making. The most valuable finding here was the DriftDetector mechanism — I had been assuming "the agent will figure it out" without specifying. A stance-keyword regex is deterministic, cheap, debuggable, and the failure mode is obvious — exactly what an audit-graded system needs.

---

---

## Prompt #17: Plan alignment to Dr. Segal's slide

**Context**: While drafting `docs/superpowers/plans/2026-05-25-hw2-agent-debate-system.md`, the user sent a screenshot of Dr. Segal's lifecycle slide:

> "Insert into plan mode / Your mission is to create the following PRD document base on the following description / Bullets A B C / prd.md / Plan.md / Todo.md (300-800) / Verify that all PRD demand implemented in the todo list. You must be very critical / Execute the todo list one by one and mark each task that was done / You must create a readme file / Run the project / push to github as public"

The user said *"use this, from the lectures"* — meaning the plan must follow this exact sequence and use the verbatim prompts.

**Goal**: Refactor the implementation plan so the execution order matches the slide (docs-first → execute → README → run → push public), and inject the lecturer's exact prompt phrasings at the corresponding tasks.

**Prompt text**: User's instruction + the slide screenshot.

**Example output received (changes applied to the plan)**:
1. Added a "Canonical Vibe Coding Lifecycle (Dr. Segal's slide — follow verbatim)" section directly under the plan header, reproducing the slide text and mapping each step to the plan's phases/tasks.
2. Task 11.2 (PRD) — now uses the verbatim prompt *"Your mission is to create the following PRD document based on the following description: [bullets]"* when invoking the PRD-writer.
3. Task 11.4 (TODO) — now uses the verbatim verify prompt *"Verify that all PRD demand implemented in the todo list. You must be very critical."* — and documents in the TODO header why we picked 800 tasks (top of the slide's 300-800 range, bottom of CLAUDE.md's 800-1000 target).
4. Task 11.1 (README) — marked explicitly as POST-execution per the slide order, with lec01 L1249-1250 quote ("you'll quickly forget what you did") as rationale.
5. Task 12.4 (push) — now marked **PUBLIC** explicitly, with `gh repo create --public` command, incognito verification, and a quote from lec05 L1641-1652 about the auto-zero risk of inaccessible repos.

**Iterative improvements**: First draft of the plan had docs in Phase 11 (after code). The slide explicitly puts docs FIRST. Restructuring the plan in-place via an "execution order overrides phase numbers" note in the lifecycle section is cleaner than renumbering every section header — the executor reads the lifecycle table first, then walks phases in lifecycle order.

**Best practice extracted**: When the lecturer's workflow ordering conflicts with the natural dependency-DAG ordering of an engineering plan, lead with a "Lifecycle (this is the order)" section that maps lecturer steps to phase numbers. Don't fight the slide — restructure to honor it, and document the deliberate choice in the PROMPTS audit trail.

---

## Prompt #18: Phase 0 execution + orchestrator-update reconciliation

**Context**: After approval gates 1 and 2 closed, switched to `superpowers:subagent-driven-development` for code execution. Dispatched the Phase 0 implementer subagent (Opus) with the full task text from `docs/superpowers/plans/2026-05-25-hw2-agent-debate-system.md` and scene-setting context (working dir, locked decisions, source-of-truth files). Implementer returned DONE_WITH_CONCERNS after 8 commits. Spec-compliance reviewer found one must-fix (`.python-version` not committed) + one accepted pragmatic adaptation (`tests/unit/test_smoke.py` added to keep the pre-commit pytest hook from blocking subsequent commits on empty test dirs).

While Phase 0 was running, the orchestrator session injected six additional files into the working dir and sent a "substantial new context" update with 7 deltas (A–G). Cross-checked all deltas against my already-committed PRD / PLAN / PROMPTS / per-mechanism PRDs / ADRs / configs — **every delta was already honored** because the same authoritative files (CONTEXT-lecture-05.md, IDEA.md, RULES.md) were read at session start and informed every locked decision. The reconciliation was a pure no-op on design; only `IDEA-handwritten-notes-salah.md` was new (Salah's personal mental model; surfaced no fresh requirements).

**Goal**: Close out Phase 0 cleanly — apply must-fix, document the smoke-test deviation, log the orchestrator-update reconciliation for the audit trail.

**Prompt text / actions**:
- Removed the `.python-version` exclusion from `.gitignore` and committed the file (commit `16f6745`) — the original Task 0.1 spec required this for fresh-machine reproducibility.
- Documented the `tests/unit/test_smoke.py` rationale here (deviation flagged transparently).
- Logged the orchestrator-update no-op outcome.

**Example output received**: 9 Phase 0 commits visible on `main` (initial 8 from implementer + the .python-version fix). All acceptance checks pass: ruff clean, pytest collects, line enforcer green, configs valid, .pre-commit installed.

**Iterative improvements**: The spec-compliance reviewer correctly caught the must-fix; the implementer's self-review missed it because the `.gitignore` exclusion of `.python-version` looked benign. **Lesson**: when a previous phase produced a `.gitignore` (initial scaffolding commit in this session), later phases inherit its exclusions silently — review the .gitignore against each phase's spec.

**Smoke test discussion** (`tests/unit/test_smoke.py`): the pre-commit hook runs `pytest tests/unit -x -q` which exits 5 ("no tests collected") on an empty `tests/unit/`. Empty exit-5 blocks subsequent commits. The implementer added a one-test file asserting `__version__ == "1.00"` (R6 versioning sanity check). This is a legitimate pragmatic adaptation — it asserts something meaningful and will be naturally subsumed by Phase 1 unit tests for the constants/version modules. Keeping.

**Best practice extracted**: When a downstream tool (pre-commit hook) has a strict expectation (must find ≥1 test), and the upstream spec doesn't yet provide that input (Phase 0 has no test files), bridge the gap with the smallest meaningful placeholder that asserts a real invariant — not a stub.

---

---

## Prompt #19: Phase 12 audit + submission-PDF resolution

**Context**: Phase 12 automatable subagent ran final audit verification. Wrote `docs/AUDIT.md` covering all 13 R-gates + 25 H-gates with PASS/FAIL/PARTIAL annotations. Also rewrote the HW1-skinned `SUBMISSION_CHECKLIST.md` for HW2. Tested the pre-existing `scripts/fill_submission_pdf.py` (carryover from HW1) — failed with `ModuleNotFoundError: No module named 'docx'` (missing python-docx dep) and used the HW1 filename `uoh-sqak-ex01.pdf` instead of HW2's `uoh-sqak-ex02.pdf`.

**Goal**: Close the script-blocker concern flagged by Phase 12 so the user can run the PDF generator on submission day without manual fixes.

**Prompt text**: Internal — fix the two script issues uncovered by the audit.

**Example output received**:
1. `uv add --dev python-docx` → installed python-docx 1.2.0 (updates pyproject.toml + uv.lock).
2. `sed`-replace in `scripts/fill_submission_pdf.py` swapping every `ex01` → `ex02` (2 occurrences, both filename refs).
3. `rm uoh-sqak-ex01.* && uv run python scripts/fill_submission_pdf.py` → produces `uoh-sqak-ex02.pdf` (26 KB) at repo root, ready for Moodle upload.
4. Added `uoh-sqak-ex02.docx` and `uoh-sqak-ex02.pdf` to `.gitignore` — they're build artifacts, regenerated from the template at submission time.

**Iterative improvements**: The audit's BLOCKED report was correct to flag this even though it offered 3 manual workarounds — adding the dep + fixing the filename is a 30-second fix that turns submission-day risk into a non-event. Trust the script; gitignore the output.

**Best practice extracted**: When a carryover script has a known-trivial blocker (missing dep, hardcoded prior assignment number), fix it in the same session that flags it — don't defer to submission day. The cost to fix now is seconds; the cost of debugging the blocker on Friday at 23:00 with the deadline looming is hours.

---

## Prompt #20: Lifecycle closure — Phase 11.1 README + handoff to user

**Context**: Phase 11.1 wrote the full 869-line README (target ≥200). All sections delivered: 16× thesis + Context Engineering quotes verbatim Hebrew/English; quick-start; installation; usage; architecture (3 Mermaid diagrams embedded); config guide; full session-1 dialogue from `transcripts/sample-session-1.json` (22-message dry-run); manual Phase 1 placeholder; cost analysis table (login=$0 / API=$0.36); behavior notes (N5 non-reproducibility); 8 lifecycle hooks + plugin pattern; testing & quality; AI Usage Disclosure verbatim; project structure; authors + MIT license; grader recipe.

**Goal**: Per Dr. Segal's lec01 L1247 ("you must create a readme file — this is the most important thing"), close out the docs-side of the lifecycle. Hand off remaining user-only Phase 12 actions cleanly: manual screenshots (12.1), real Claude debate run + verdict screenshot (12.2), `gh repo create --public` push (12.4), Moodle upload (12.5).

**Prompt text**: Internal — close the lifecycle and document the handoff.

**Example output received**: Single Phase 11.1 commit `b62ab52` containing README.md (869 lines) + transcripts/sample-session-1.json + 37 Phase 11.1 TODO items flipped to `[x]`. Followed by Phase 12 automatable commits closing the audit + checklist.

**Best practice extracted**: The README is the "single shippable artifact" that the grader will read FIRST. It must stand alone — assume the grader hasn't read PRD.md or PLAN.md (those are for code-review depth, not first-touch). Embed diagrams, paste the session-1 dialogue inline, quote ethics policy verbatim. The README is also where the lecturer-bonus signals (16× thesis quote, N5 non-reproducibility note, AI Usage Disclosure) become visible.

---

## Prompt #21: Phase 13g — Scroll-driven debate presentation (eighth frontend iteration)

**Context (2026-05-26 to 2026-05-27)**: After phases 13c through 13f all collapsed under the same root cause — multi-panel layouts that "felt chaotic" and broke at non-default viewports — the user landed on a fundamentally different metaphor in conversation:

> "I am thinking about something that looks like a presentation, the opinion of the pro appears smoothly, then disappears smoothly and so is the con and at the end the judge also at the beginning the judge … and every opinion agent has an avatar, they do not appear at the same time, but the timeline is saved so when they finish you can navigate the conversation"

Then later, refining how the user navigates the timeline:

> "Okay. But not with arrows, with scroll, but it's not scrolling. When you scroll, the animation moves. The smooth transition animation. You know what I mean?"

That second clarification was the lock: **scroll-driven scrubbing** rather than arrow-key advance. The canonical 2026 pattern (Linear, Apple product pages, awwwards) uses Lenis smooth-scroll + Framer Motion `useScroll` + `useTransform` to map scroll progress onto opacity/Y across a stack of slides pinned to a sticky viewport.

**Workflow**:

1. **Brainstorm** in conversation (no tool calls) — single-speaker presentation, Pro/Con/Judge anchoring, scroll-driven scrubbing, JUMP TO LIVE follow pattern.
2. **Spec** → `docs/superpowers/specs/2026-05-26-hw2-gui-scroll-presentation.md` (design tokens, transitions table, state model, SSE handling, acceptance criteria).
3. **Spec self-review** — inline fix to the word-fade-duration ambiguity.
4. **PRD** → `docs/PRD_gui.md` with Input/Output/Setup docstring (rubric §A13) + 18 functional reqs (G1–G18) + 14 acceptance criteria.
5. **Implementation plan** → `docs/superpowers/plans/2026-05-26-hw2-gui-scroll-presentation.md` with 15 bite-sized TDD tasks, one commit per step.
6. **TODO append** — Phase 13g.A–P sections (~80 sub-tasks) in `docs/TODO.md`.
7. **Approval gate** per rubric §2.5 step 5 — user approved with "ok".
8. **Subagent-driven execution** — fresh general-purpose subagent per plan task, two of them did meaningful spec-improving fixes (Task 7 unblocked the JSX runtime for all subsequent component tests; Task 10 fixed a rules-of-hooks bug latent in the plan).
9. **E2E visual verification** — Playwright MCP captured `assets/13g-empty.png`, `assets/13g-pro-turn.png`, `assets/13g-con-turn.png`, `assets/13g-verdict.png`.
10. **Closure** — full Python regression (164 passed) + full Vitest suite (17 passed) + README Web GUI section + this Prompt #21.

**Best practice extracted**:

- **When the user rejects N iterations of a class of designs, change the metaphor, not the polish.** Phases 13c–13f all iterated on "multi-panel responsive layouts" with different aesthetics. The win was abandoning the class entirely — one speaker at a time, scroll-as-scrubber — not finding the "right" panel arrangement.
- **The brainstorming skill's hard gate "no code until user approves the design" is load-bearing.** I tried to short-circuit it earlier in this conversation by jumping to implementation; that's what produced the rejected iterations.
- **For multi-task plans, the plan itself can contain bugs.** Two of fifteen tasks had latent issues (the LenisProvider import order in Task 2, the rules-of-hooks violation in Task 10). Spec reviewer subagents caught them at dispatch time, but only because the implementer prompts explicitly flagged them with workarounds. Subagent execution without those callouts would have produced a runtime-failing build.
- **A pivot-prompt for an external design tool (`docs/CLAUDE_DESIGN_PROMPT.md`) is itself a valuable artifact** even when the user decides not to use it. It captures, in paste-ready form, the design intent that took eight iterations to converge on. Useful for the next graded course (or a future re-do).

---

## Decisions locked (updated running list)

| # | Decision | Locked at | Source |
|---|----------|-----------|--------|
| 1 | LLM provider: Claude-only via login CLI | Prompt #3 | User |
| 2 | Debate topic: *"Can AI agents create genuinely original art, or only remix human work?"* | Prompt #4 | User |
| 3 | Pro = originality side; Con = remix-only side | Prompt #4 | Recommended |
| 4 | Pings per side: 10 | Prompt #5 | User |
| 5 | Web search: DuckDuckGo via `ddgs` (pluggable interface) | Prompt #6 | User |
| 6 | IPC: `multiprocessing.Process` + `multiprocessing.Queue` | Prompt #7 | User |
| 7 | Word cap per turn: 250 words | Lecture default | Lec05 default |
| 8 | Drift threshold: 1 (per-message check + correct_and_replay) | Lecture default | Lec05 L1182-1184 |
| 9 | Scoring: 5 axes × 20 = 100 (clarity, evidence, rebuttal, novelty, role-fidelity) | Lecture default | Lec05 L1576 |
| 10 | Logging: FIFO 20 files × 500 lines structured JSON | Spec default | HW2 spec §8.6 |
| 11 | Judge scoring criteria sourced via web-search pre-flight (N7) | Design choice | Lec05 L1519-1528 |
| 12 | Skills: project-local under `.claude/skills/`, loaded statically as system prompts (ADR-002) | Design choice | H17 + Prompt #9 |
| 13 | Pair: Salah Qadah + Andalus Kalash (group `uoh-sqak`) | Pre-confirmed | HW1 submission |
| 14 | Class hierarchy: `BaseAgent` → `PartisanAgent` → `Pro/Con`; `BaseAgent` → `Judge` | Prompt #11 | Design |
| 15 | 3 mixins (Logging, Lifecycle, Heartbeat) — retry consolidated into Gatekeeper | Prompt #11 | Design |
| 16 | Plugin pattern: `LLMProvider` + `SearchProvider` abstract bases + factory registry | Prompt #11 | Extensibility fix |
| 17 | 8 lifecycle hooks: before/after × round/verdict/llm_call/search | Prompt #11 | Rubric §A9 |
| 18 | JSON wire schema versioned at 1.00, jsonschema-validated on both send and recv | Prompt #12 | H2 + R6 |
| 19 | 8 message roles (setup_directive, ack, argument, counter, correction_request, intervention, status, verdict) | Prompt #12 | H4+H16+H18+H20 |
| 20 | Mutual-reference enforcement via `references_opponent` schema flag + Judge re-verify regex | Prompt #12 | H7 |
| 21 | Watchdog: 2s heartbeat, 30s stuck timeout, max_restarts=3, backoff [1,2,4] | Prompt #13 | H21 |
| 22 | Watchdog detection uses BOTH `is_alive()` AND heartbeat-staleness (two-signal) | Prompt #13 | Design refinement |
| 23 | Lying allowed; opponent fact-checks via web search; Judge does NOT verify facts | Prompt #13 | H17 + lec05 L1483-1491 |
| 24 | Graceful shutdown: SIGINT → main → SIGTERM cascade → 10s drain → SIGKILL stragglers → flush transcript | Prompt #13 | Spec §8.6 |
| 25 | Budget caps: warn at 75%, hard refuse + early verdict at 95% | Prompt #13 | Rubric §A8 |
| 26 | Test pyramid: ~124 unit + ~9 integration + ~3 e2e (`@pytest.mark.e2e` gate) | Prompt #15 | HW1 testing-quality bar |
| 27 | Pre-commit runs unit only (fast); CI runs unit + integration with coverage; E2E opt-in | Prompt #15 | Dev feedback loop |
| 28 | DriftDetector mechanism: stance-keyword regex (deterministic, no extra LLM call) | Prompt #16 | Self-review locked |
| 29 | Token budget concrete: tokens_per_debate=200000, warn@75%, hard@95% | Prompt #16 | Self-review locked |
| 30 | DTOs: `LLMResponse`, `SearchHit`, `SpendReport`, `HealthStatus` defined as frozen dataclasses | Prompt #16 | Self-review locked |
| 31 | ClaudeLoginProvider invocation: `claude -p --append-system-prompt <skill> --output-format json --max-turns 1` | Prompt #16 | Self-review locked |
| 32 | Plan execution order: docs FIRST per Dr. Segal's slide (PRD → PLAN → TODO → verify → execute → README → run → push public) | Prompt #17 | Lecturer slide |
| 33 | TODO.md target size: 800 tasks (top of slide's 300-800, bottom of CLAUDE.md's 800-1000) | Prompt #17 | Reconciles slide + spoken lecture + project target |
| 34 | Push to GitHub explicitly PUBLIC (`gh repo create --public`); incognito verify; lec05 L1641-1652 auto-zero risk | Prompt #17 | Lecturer slide |
| 35 | README is POST-execution per slide order (lec01 L1249-1250: "you'll forget what you did") | Prompt #17 | Lecturer slide |
| 36 | Use verbatim prompts: "Your mission is to create the following PRD document…" + "Verify that all PRD demand implemented in the todo list. You must be very critical." | Prompt #17 | Lecturer slide |
| 37 | Phase 10 design refinement: JudgeAgent runs in **main process** (not a Process child) for routing simplicity. Pro + Con run as real Processes; main hosts the Judge logic between their queues. Satisfies the 3-process requirement (main = orchestrator/judge, pro = Process, con = Process) without bidirectional-routing-through-a-child complexity. | Prompt #18 (Phase 10) | Pragmatic over dogmatic |
| 38 | Phase 10 split: `process_flow.py` owns the IPC dance (setup_phase, ping_loop, route_with_replay, await_partisan); `process_verdict.py` owns scoring + verdict; orchestrator.py orchestrates only. Each module ≤150 lines. | Prompt #18 (Phase 10) | 150-line rule |
| 39 | PartisanAgent.handle_message now responds: setup_directive → ack; argument/counter/correction/intervention cues → LLM-driven argument or counter. Previously was no-op. | Prompt #18 (Phase 10) | Required for real IPC |
| 40 | E2E tests (`tests/e2e/`) are gated by `RUN_E2E=1`; unit tests + integration with mocked LLM cover CI. Real-Claude e2e only runs locally before submission. | Prompt #18 (Phase 10) | Cost + flakiness control |

---

## To-be-resolved (will surface as new prompts)

- Andalus's GitHub username (for repo collaborator invite — H14 audit blocker if mis-shared)
- Whether to push the existing `CONTEXT-*.md` orchestrator scaffolding files to the public repo, gitignore them, or move them to `.workspace/`
- Final repo URL — suggested `salah-dev-stu/uoh-sqak-ex02` per HW1 pattern, but partner may want a co-owned org
- The `SUBMISSION_CHECKLIST.md` at root is still HW1-skinned (mentions LSTM/RNN/dataset mechanisms, notebook analysis); needs full rewrite for HW2 deliverables — schedule after PRD is approved
