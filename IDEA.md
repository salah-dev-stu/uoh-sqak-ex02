# HW2 — AI Agent Debate (vibe input for Plan Mode)

> This is the free-text "vibe input" the worker session feeds into Plan Mode to generate `docs/PRD.md`. The source is `materials/hw2-spec-main-v4-Agents-Subagents-Commands.pdf` (Dr. Yoram Segal, Lesson 05 summary). **In any contradiction between this file and the actual lecture recording (`lectures/lecture-05-agents-debate.txt`), the recording wins** — that's what Dr. Segal explicitly stated in the spec.

## The assignment in one sentence

Build a **three-agent debate system** in Python: a Pro agent and a Con agent argue a topic, a Judge (father) agent moderates the conversation and decides a winner — all wired together with **real LLM calls** and **process-level isolation between agents**.

## The architecture you must build

```
                            ┌──────────────────────┐
                            │   Judge (Father)     │  ← unbiased; doesn't know topic
                            │   - moderator        │
                            │   - decider (no tie) │
                            │   - scores persuas.  │
                            └────────┬─────────────┘
                                     │   JSON messages, child→father→child
              ┌──────────────────────┼──────────────────────┐
              ▼                      │                      ▼
     ┌────────────────┐              │            ┌────────────────┐
     │  Pro Agent     │              │            │  Con Agent     │
     │  - own Skill   │     (never talk            │  - own Skill   │
     │  - web search  │      directly)             │  - web search  │
     │  - argues FOR  │              │            │  - argues AGNST│
     └────────────────┘              │            └────────────────┘
                                     │
                            ┌────────▼─────────┐
                            │   Orchestrator   │  ← Python main process
                            │   - spawns 3 procs│
                            │   - watchdog     │
                            │   - timeouts     │
                            │   - JSON IPC bus │
                            └──────────────────┘
```

- **Agents are OS processes.** Two agents = two processes running in parallel (Multi-Process). Inter-process communication uses standard OS primitives — Signals, FIFOs, Queues, Sockets — exactly what was covered in OS class.
- All messages flow **child → father → child**. Pro and Con never speak directly.
- Messages serialized as **JSON** (structured, parseable, token-efficient).

## Choice of topic

Free — whatever sparks a real argument. Examples Dr. Segal mentioned: *Barcelona vs Real Madrid*, *does God exist*, *which diet is better*, *freshwater vs saltwater fish*. Pick something the LLMs will genuinely argue about. Pick before scaffolding so the README + Pro/Con system prompts can be specific.

## Mandatory rules (התניות מחייבות)

1. **Respectful turn-taking** — one speaks, finishes, listens. Cap by time or word count.
2. **Real contradiction** — Pro and Con must have **different `Skill`s** (LLMs tend to "please"; if both are vanilla, they'll just agree). Each Skill enforces a stance and a personality.
3. **≥10 pings per side** (argument → counter-argument). *Budget-limited fallback: reduce to 5 pings and mention explicitly in README — no grade deduction.*
4. **Mutual reference** — each turn must reference the opponent's prior point. No talking past each other.
5. **Internet search tool is required** — agents must be able to back up claims with web sources. Tool-use is mandatory.
6. **Judge MUST decide** — no ties allowed. Judges on **persuasiveness, not factual correctness** (like the TV game "the truth is a lie"). Differential scoring (70%/80% etc.) OK; ambiguity not OK.
7. **All traffic through the Judge** — child → father → child. Children never talk to each other directly.
8. **JSON wire format** — structured records, easy to monitor, log, and replay.

## What you must NOT do

- ❌ Tie outcomes — Judge is required to call a winner
- ❌ Fake debates — generated text from `random.choice(["yes", "no"])` is disqualifying. **Must use real LLM calls.**
- ❌ Vulgar / political-incorrect language
- ❌ Submit "just a Claude CLI workflow" — there **must** be Python code that drives the agents
- ❌ Arabic-only conversations — Dr. Segal wants Hebrew or English so he can read it

## Build order Dr. Segal recommended

1. **Manual** — open two terminals, two Claude CLI instances (or GPT+Gemini), drive a debate by hand. Just to feel the dynamics.
2. **Intermediate** — a Claude CLI Command (`/debate`) that spawns Judge → which spawns Pro/Con.
3. **Final (what you submit)** — Python main process that owns all three sub-processes, the IPC bus, watchdog, timeouts, logging.

## Engineering requirements (these are mandatory — see RULES.md for the full audit list)

- **Timeouts on every LLM call** — agents can hang on slow responses
- **Watchdog + keep-alive** — if a child process dies, kill remnants and restart
- **OOP** — class hierarchy, base classes / mixins for shared concerns. **Submit an architecture diagram** of the class layout.
- **TDD** — tests written with or before code, ≥85% coverage
- **Ruff** — zero lint errors
- **Zero hardcoded values** — everything in `config/*.json` or `.env`
- **Cyber hygiene** — `.env-example` only, never `.env`. `.gitignore` enforces it. No API keys, tokens, or secrets in git, ever.
- **Gatekeeper layer** — every LLM call passes through one class that meters/limits token spend; can also bolt on retry/security policies
- **SDK layer** — Terminal/CLI/UI sit on top of an SDK; the SDK is the only entry point for business logic. This makes the system self-debuggable (an agent can call the SDK to inspect its own state).
- **Structured logs** — FIFO log rotation in config (e.g., 20 files × 500 lines each). No prints. No unstructured stderr.
- **Operable from a terminal menu** — keyboard navigation, no GUI required. GUI optional + screenshots if you build one, but evaluation runs from the menu or SDK directly.
- **`uv` for everything** — `pyproject.toml` is the source of truth; `uv.lock` is committed; `uv sync` recreates the env on the grader's machine without any extra steps.

## Deliverables

- **Detailed `README.md`** with screenshots, exact prompts used, and a **full dialogue dump of session 1** so the reader can see the debate without running it
- **Public GitHub repo** OR private+shared with `rmisegal@gmail.com`. Inaccessible repo = automatic rejection, no resubmit.
- **PDF on Moodle** linking to the repo (use the submission template `uoh-sqak-ex02.docx` → `uoh-sqak-ex02.pdf`)
- **Pairs only.** Each pair member uploads the same PDF separately on Moodle. *Solo policy unclear for HW2 — confirm with Dr. Segal if going solo again.*

## Tech stack hints (from the spec)

- **Claude CLI** is the lecturer's tool of choice. Codex (OpenAI) and Gemini CLI also valid. GLM via Z.AI is the cheap-but-comparable alternative — "a month of Claude ≈ a year of GLM".
- **Login auth vs API key** — login is a flat-rate bundle, API key is pay-per-token (cheaper if you manage budget). Set provider-side spend caps either way.
- **Cache pricing** — every provider has internal embedding/cache. Repeat-context queries cost ~10× less. Structure prompts to maximize cache hits.
- **`--dangerously-skip-permissions` (Claude) / `--yolo` (Gemini)** — only inside trusted project directories. Saves endless approval prompts.

## Context engineering note (Dr. Segal's framing)

"You are no longer ChatGPT users — you are token-economy managers." The course's main point is the transition from **Prompt Engineering** to **Context Engineering**: managing what enters and leaves the Context Window. The hierarchy `Command → Skill → Agent → Subagent` is the toolkit for doing that systematically. Your debate system should reflect this — every prompt, every Skill, every tool invocation should be deliberate about token spend.

## Where to find more context (read on demand)

- `materials/hw2-spec-main-v4-Agents-Subagents-Commands.pdf` — full spec (8 pages, in Hebrew)
- `materials/transformer-book-segal.pdf` — Dr. Segal's book on Transformers (Lec 04 background)
- `materials/lecture-04-transformer-booklet.pdf` — Transformer explanation booklet (Lec 04)
- `materials/lecture-04-transformer-abstract.pdf` — Lec 04 abstract (Token Economy, Agent intro)
- `lectures/lecture-04-transformer.txt` — full Hebrew transcript of Lec 04 (CNN, Transformer, Token Economy, Agent intro)
- `lectures/lecture-05-agents-debate.txt` — **authoritative HW2 spec** (Agents, Subagents, Commands, Skills, debate exercise). **Always check this when the PDF is ambiguous.**
- `../hw1/feedback/Detailed_Feedback_Report.pdf` — Dr. Segal's feedback on HW1. Use it as a checklist of what to fix in HW2.
- `RULES.md` (in this directory) — distilled audit rubric

## Self-grade strategy (read carefully — this is from HW1's painful lesson)

HW1 self-graded at 92 → grader applied "especially rigorous lens" → final 85.54.

For HW2, **target an honest 85–88 self-grade** unless the deliverable is genuinely exceptional. Specifically:
- Default placeholder: **`85`**
- Bump to 88–90 only if every transferable HW1 weakness has been addressed (planning docs, configuration portability, extensibility/plugin pattern, automated quality tooling)
- Never claim a number the work doesn't support — the rubric explicitly penalizes over-confidence

---

## Verbatim quotes from the spec PDF (for `docs/PRD.md` use)

The grading agent pattern-matches against the spec's exact phrasing. Quote these verbatim where applicable.

### Central thesis (spec §10 — quote in `README.md` intro)

> "המעבר מ-Prompt Engineering ל-Context Engineering הוא המעבר שהופך אתכם ממשתמשי ChatGPT למהנדסי סוכנים. אורקסטרציה של סוכנים, ניהול מודע של חלון ההקשר, ועיצוב היררכיה ברורה של Command, Skill, Agent, Subagent — אלו הכלים שיבדילו את התוצר שלכם מתוצר חובבני."
>
> *"The transition from Prompt Engineering to Context Engineering is what turns you from ChatGPT users into agent engineers. Agent orchestration, conscious context-window management, and clear hierarchy design of Command, Skill, Agent, Subagent — these are the tools that distinguish your product from an amateur one."*

### Mandatory debate rules (spec §8.3 — verbatim Hebrew + English)

1. **דו-שיח מכבד** — *"אחד מדבר, מסיים, מאזין; מגבילים בזמן או בכמות מילים"* — respectful dialogue; one speaks, finishes, listens; cap by time OR word count
2. **קונטרדיקציה אמיתית** — *"לכל סוכן Skill שונה משל חברו, כדי שהוויכוח לא ימוטט את עצמו. סוכנים נוטים 'לרצות' — דאגו שלא יסכימו אחד עם השני אוטומטית"* — real contradiction; agents tend to "please", make sure they don't auto-agree
3. **לפחות 10 Pings (טיעון → טיעון-נגד) לכל צד** — at least 10 pings per side
4. **התייחסות הדדית** — *"כל סוכן חייב להתייחס לטיעוני יריבו, לא לדבר במקביל"* — mutual reference; no parallel monologues
5. **אסמכתאות מהאינטרנט** — *"tool של חיפוש באינטרנט הוא חובה"* — internet citations; web-search tool is mandatory
6. **תפקיד האבא** — *"אסור שיהיה תיקו. הוא חייב להחליט מי זכה, ולנמק את הציון. הקריטריון הוא כושר שכנוע, לא נכונות עובדתית — כמו המשחק 'האמת היא שקר' בטלוויזיה"* — Father's role; no ties; persuasiveness not factual correctness
7. **הוויכוח עובר דרך האבא** — *"לא ישירות בין הילדים. כל הודעה: ילד → אבא → ילד"* — through Father; child → father → child
8. **פורמט תקשורת — JSON** — *"מובנה תבניתית, ניתן לניטור ובדיקה, וחוסך טוקנים"* — JSON; structured, monitorable, token-efficient

### Forbidden items (spec §8.4 — verbatim)

- *"אסור תוצאת תיקו בין הצדדים — האב חייב להכריע"* — no tied outcome; Father must decide
- *"אין ויכוח ללא שימוש ב-LLM — הוויכוח חייב להיות אמיתי, לא טקסט מומצא מקוד Python"* — no debate without LLM; real, not Python-generated
- *"אין שפה בוטה — Politically Correct ומכבדת"* — no vulgar language; PC and respectful
- *"אסור להגיש דרך Claude CLI בלבד — חייבים לעבוד עם קוד Python שמפעיל את הסוכנים"* — no Claude-CLI-only submission; Python code drives the agents

### Build stages (spec §8.5 — recommended progression)

Bake all three into `docs/PLAN.md` phases AND `docs/TODO.md` milestones:

1. **שלב ידני (בטרמינל)** — *"לפתוח שני Claude CLI (או GPT + Gemini), להגדיר לכל אחד תפקיד, ולנהל ויכוח ידני. רק כדי להבין את התופעה."*
   → Manual; two terminals; just to feel the phenomenon. Capture screenshots in README.
2. **שלב ביניים** — *"Command ב-Claude CLI שמפעיל את האב, שמפעיל את הילדים."*
   → Intermediate; a slash command that launches Father → children. Capture screenshot.
3. **שלב סופי** — *"קוד Python ראשי שמנהל את שלושת התהליכים."*
   → Final; Python main process managing all 3 sub-processes. **The deliverable.**

### Class-discussion clarifications (spec §9 — easy to miss; ALL graded)

- **תיקו (Tie)? ממש לא.** Differential scoring (70/80) OK, but decision mandatory.
- **Should Judge know the topic?** No. *"השופט מבין רק את חוקי המשחק ושופט כושר שכנוע. דווקא טוב שהוא לא יודע — כך אינו מוטה"* → Judge's system prompt MUST NOT contain the topic.
- **Agreements during debate?** Allowed point-in-time, but *"האב חייב להתערב ולהזכיר את התפקיד"* → Judge needs an active drift detector that intervenes after N consecutive aligned pings (default: 3).
- **Lies in debate?** Allowed. *"הצד הנגדי אמור לתפוס אותם — זה חלק מכושר השכנוע"* → web-search tool serves DUAL purpose (citation + fact-check opponent).

---

## The 8 ambiguities — defaults updated after lecture-05 transcript review

The spec PDF leaves these open. The lecture 05 transcript (now available at `../lectures/lecture-05-agents-debate.txt`) resolved or clarified several. **The values below reflect the post-lecture defaults; the original PDF-only defaults are noted where they changed.** See `CONTEXT-lecture-05.md` for full rationale.

| # | Ambiguity | Default | Where to document |
|---|---|---|---|
| 1 | Word-count cap per turn | **250 words** (lecturer left open; chosen to balance richness vs token cost) | `config/debate_rules.json` `max_words_per_turn` |
| 2 | JSON wire schema | See proposed shape below. Lecturer confirmed JSON. Use quote *"ג'ייסונים זה תבניות"* / "JSONs are templates" (lec05 L1443) as rationale | `docs/PRD_ipc_bus.md` |
| 3 | Judge intervention threshold | **1 ping (per-message check + `correct_and_replay`)** ← changed from 3. Lecture L1182-1184: Judge enforces role-faithfulness on every message, not after N strikes | `config/debate_rules.json` `drift_intervention_threshold: 1`, `drift_intervention_action: "correct_and_replay"` |
| 4 | Persuasiveness scoring axes | **5 axes × 20 each = 100**: clarity, evidence, rebuttal, novelty, **role-fidelity** ← 5th axis added from lec05 L1576 ("MUST reference what he said. Must be a dialogue.") | `docs/PRD_judge_agent.md` |
| 5 | Web search provider | **Brave Search API** (lecturer doesn't care which — only that one exists) | `docs/PRD_web_search_tool.md` ADR |
| 6 | Process model | **`multiprocessing.Process` + `multiprocessing.Queue`**. ADR must enumerate Dr. Segal's 4 IPC primitives (Signal, FIFO/Pipe, Queue, Sockets — lec05 L399) and justify choice | `docs/PLAN.md` ADR-001 |
| 7 | LLM provider per agent | **Different providers per debater ENCOURAGED** ← changed from "same". Lec05 L1131-1142, L1896-1908: *"ensure each comes from a different place so an argument is created"*. Pro on Claude, Con on Gemini is the model setup | `config/agents.json` per-agent `provider` field |
| 8 | Pair vs solo for HW2 | **Pairs (per PDF spec; lecture didn't address)**. User confirmed pair with Andalus Kalash (same as HW1) | already pre-populated in CLAUDE.md |

---

## ➕ NEW requirements surfaced ONLY in the lecture (not in the PDF)

The lecture added these — they are mandatory because Dr. Segal said them out loud and the spec PDF itself defers to the recording.

### N1. Judge MUST issue setup directives at debate start
Lec05 L1213-1221, L1411-1433: *"When the Judge starts, he needs to activate the players and tell them: 'These are the rules of the game, you must be Against...'"*. Plus L1426-1434: *"In what format do you want the response?"*

**Concrete:** Add a `"role": "setup_directive"` message type to the JSON wire schema. Judge sends one to each child at bootstrap with: stance assignment, debate rules, expected JSON response format. Document in `docs/PRD_judge_agent.md`.

### N2. Judge MUST police PC/vulgar-language
Lec05 L1553-1559: *"One of the checks the Father must do: verify no vulgar language, Politically Correct, mutual respect."*

**Concrete:** Implement PC filter inside `JudgeAgent.handle_message()` as a post-processor. Sanitize or reject messages with vulgar/PC violations BEFORE re-broadcasting to opponent. Added to RULES.md as **H12**.

### N3. Skills are PROJECT-LOCAL, never global
Lec05 L1330-1332: *"Notice these are PROJECT skills — don't put them in global skills because you don't want them leaking into other operations."*

**Concrete:** All Skills (Pro/Con/Judge) under `.claude/skills/<name>/` in the project, NOT under `~/.claude/skills/`. Repo audit verifies. Added to RULES.md as **H13**.

### N4. RAG is explicitly optional (out of scope)
Lec05 L1228-1232: *"RAG is NOT mandatory, NOT mandatory, I repeat."*

**Concrete:** Add to `docs/PRD.md` Constraints: "RAG intentionally out of scope per Dr. Segal's lec05 L1228-1232. Agent's memory model = LLM context window + project transcripts only."

### N5. Non-reproducible outcomes are DESIRED (not a bug)
Lec05 L1581-1597: *"Next time, they talk, talk, talk, and next time Real wins. Excellent, very good, that's the BEST."*

**Concrete:** Add to README.md Behavior section: "The same topic can yield different winners across runs — this is intentional and DESIRED per Dr. Segal (lec05 L1597)." Pre-empts grader confusion.

### N6. Judge MUST NOT know the topic
Lec05 L1449-1469: *"He doesn't need to know football, doesn't need to know diet science... I don't want anyone to say a word [from the topic vocabulary], no one understood its meaning, and then 'ah, right, and that's why I give them here.' No."*

**Concrete:** Judge's system prompt must be **topic-agnostic** — only contains rules of debate + scoring criteria. Only Pro/Con system prompts contain the topic. Document explicitly in `docs/PRD_judge_agent.md`.

### N7. Use web search to BUILD the Judge's expertise (not invent it)
Lec05 L1519-1528: *"The Father's expertise = debate expert. Tell Gemini: 'search the world for who's the #1 debate expert and what criteria he sets,' then take those criteria and give them as system prompt to the Father."*

**Concrete:** Before scaffolding Judge's system prompt, do a one-off research session — search for "parliamentary debate scoring", "Lincoln-Douglas format", "Robert's Rules" — and derive the Judge's scoring criteria from real-world authority. Document the research in `docs/PROMPTS.md` or as ADR. Graded as creativity/originality signal.

### N8. Terminal menu keyed for SDK self-testing
Lec05 L1736-1745: *"If you work with SDK, you can take Cloud CLI and tell it 'test this software for me', and it can play with you on the menus."*

**Concrete:** Menu options keyed by letters/numbers ("press A", "press B", "1: start debate", "2: view transcript") so Claude CLI can drive it from a slash command for automated self-testing. Document this as the SDK's design rationale.

### N9. Phase 1 (manual two-terminal) is graded — needs README screenshots
Lec05 L1896-1909: *"I recommend you start all this work manually... feel what a debate between agents is."*

**Concrete:** Even before writing Python code, run a manual debate by hand: open two Claude CLIs (or Claude + Gemini), assign roles, pass messages between them by copy-paste. Take screenshots. Embed in README "Manual exploration" section as evidence of stage 1.

### N10. Multi-Skill per agent (BONUS opportunity)
Lec05 L1254-1259: *"Don't put one skill per player — give him several skills. E.g., one expert at generating arguments, another expert at analyzing the opponent's arguments."*

**Concrete:** Document in `docs/PLAN.md` "Future work" — each debater could have:
- `pro_skill/` — stance + general knowledge
- `argument_generator_skill/` — crisp argument generation
- `opponent_analyzer_skill/` — opponent rebuttal analysis

Same for Judge: `debate_referee_skill/` + `pc_filter_skill/` + `scoring_skill/`. **Bonus territory** — implementing 1-2 of these earns originality points.

### N11. CLI orchestration ≠ deliverable
Lec05 L1281-1297: *"I do NOT recommend [Cloud-CLI-only]... I expect you to write a process for the main supervisor, opponent A, opponent B."*

**Concrete:** Build phase 2 (Claude CLI Command driving the debate) is a **learning checkpoint only**. The submitted deliverable is the Python multi-process system. Don't ship the CLI version.

### N12. Lecture lecturer-confirms inaccessible-repo = AUTO ZERO
Lec05 L1641-1652: *"3-4 submitted with GitHub but without sharing — couldn't open them — **there's a zero there**."* NO resubmission.

**Concrete:** Before submission, verify Andalus can `git clone` and the lecturer (`rmisegal@gmail.com`) can either browse via public repo OR has been added as collaborator. Run a smoke test from a logged-out session.

---

## Cost analysis is MANDATORY for HW2 (rubric §11 + §17.5)

### Proposed JSON wire schema for ambiguity #2

```json
{
  "msg_id": "uuid",
  "from": "pro|con|judge",
  "to": "pro|con|judge",
  "role": "argument|counter|verdict|intervention|status",
  "ping_index": 7,
  "text": "...",
  "citations": [
    {"url": "...", "snippet": "..."}
  ],
  "timestamp": "ISO-8601",
  "tokens_in": 1234,
  "tokens_out": 567
}
```

Versioned (`"schema_version": "1.00"`); validated by jsonschema or pydantic.

---

## Cost analysis is MANDATORY for HW2 (rubric §11 + §17.5)

HW1's rubric distillation marked cost analysis "not relevant" because HW1 had no API calls. **HW2 IS an API consumer**, so this becomes mandatory. The README must include:

1. **Token cost table** (Claude input/output tokens + web-search calls + total $)
2. **Optimization strategies** subsection — token reduction tactics, batch processing, model-cost selection, cache-friendly prompt structure
3. **Budget controls** — `gatekeeper.estimate_cost(n_debates)`, `gatekeeper.get_spend_so_far()`, alerts at 75%/95% of configured budget

Configure pricing in `config/rate_limits.json`:
```json
{
  "services": {
    "claude_sonnet": {
      "price_input_per_million_tokens": 3.00,
      "price_output_per_million_tokens": 15.00,
      "requests_per_minute": 30,
      "tokens_per_debate": 100000,
      "tokens_per_day": 500000,
      "warn_at_percent": 75,
      "hard_cap_percent": 95
    }
  }
}
```

---

## Final-project lineage (syllabus week 11)

The course final project is a **"League of 20 Questions" tournament**. HW2's three-agent system is direct preparation:
- HW2 **Judge** → tournament judge agent
- HW2 **Pro/Con** → tournament player agents

Design HW2's agent abstraction so a Player agent and a Judge agent can be re-used in the final project. Mention this under "Future work / extension points" in `docs/PLAN.md` — it shows architectural foresight (and scores extensibility points).
