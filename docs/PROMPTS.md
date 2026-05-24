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

## To-be-resolved (will surface as new prompts)

- Andalus's GitHub username (for repo collaborator invite — H14 audit blocker if mis-shared)
- Whether to push the existing `CONTEXT-*.md` orchestrator scaffolding files to the public repo, gitignore them, or move them to `.workspace/`
- Final repo URL — suggested `salah-dev-stu/uoh-sqak-ex02` per HW1 pattern, but partner may want a co-owned org
