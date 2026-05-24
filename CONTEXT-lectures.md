# Course Digest for HW2 Worker — Lectures 01-04

**Source:** Lectures 01b (Vibe Coding Part 2), 02 (Deep Learning), 03 (RNN/LSTM), 04 (CNN/Transformer/Agents). Instructor: Dr. Yoram Segal. Compiled 2026-05-24. **Lecture 05 ("Agents Debate") still transcribing — will be appended when ready. Per HW2 spec, lecture 05 recording overrides this digest where they disagree.**

---

## 1. Canonical Vibe Coding Workflow (Lecture 01b — Authoritative)

Dr. Segal walked through the full lifecycle live in Lecture 1, lines ~1140-1500.

### 1.1 The Three Mandatory Files

Lecture 1, lines 1147-1180:
> "כולם עובדים אך ורק אך ורק בכתיבת קוד במינימום עם שלושה קבצים"
> *"Everyone works ONLY ONLY in code writing minimum with three files."*

The three files (exact terms used):
- **`prd.markdown`** (line 1155) — "prd program requirement document" — "מסמך שפה מאפיינים את התוכנה" (the document that characterizes the software). Quote (line 1160): *"There's no way you write to it in a prompt like I wrote Hello World; we don't work that way."*
- **`plan.md`** (line 1164) — "האסטרטגיה איך הולכים לעשות" (strategy of how we're going to do it) — installation, dependencies, algorithm design, action plan, MILESTONES. Lines 2031-2035: *"the plan is what breaks it into phases... the milestone, it breaks it for you into milestones".*
- **`to-do.md`** (line 1168) — "to-do list... הקובץ הזה מכיל tasks משימות" (this file contains tasks).

### 1.2 The Magic Number for TODO Tasks (CORRECTED)

Lecture 1, lines 1170-1180 — Dr. Segal's EXACT quote:
> "ופה הסוד הגדול שלכם... תמוה לפי גודל התוכנה אבל **מינימום 500 משימות בדרך כלל 1000 משימות 900 משימות 800 משימות**"
> *"And here's your big secret — you tell it to scale by the size of the software but **MINIMUM 500 TASKS, usually 1000 tasks, 900 tasks, 800 tasks**."*

Reconfirmed Lecture 3, lines 2022-2027 (student question about "at least 500 tasks"). Dr. Segal confirmed the count.

**Resolution of the screenshot discrepancy (300-800 vs. 500-1000):** The lecture-spoken authoritative number is **minimum 500, typical 800-1000**. The on-screen "300-800" was likely older guidance. Use 500-1000.

### 1.3 The Verification / "Be Very Critical" Step

Lecture 1, lines 1183-1205 — verbatim prompt phrasing:
> "**verify** — תלך ותבדוק שכל הדרישות ב-PRD מומשו ב-to do list"
> *"Verify — go and check that all requirements in the PRD are implemented in the to-do list"*
> "**you must be very critical תהיה מאוד מאוד ביקורתי**"
> *"you must be very critical, be very very critical"*

Quote (line 1199-1201): *"I tell you that usually when I do this step, he adds about 200 more tasks to the to-do that he missed."*

### 1.4 Execute Step

Lecture 1, line 1207-1211:
> "**execute the to do list one by one and mark each that was done or complete**"

(The transcript renders "execute" as "exec mute" — whisper artifact.)

Marking enables session resumption — Lecture 1 lines 1323-1328: *"In the to-do list I told him you need to mark every task you did, every task that is done — this contains both what needs to be done and what he did."*

### 1.5 Mandatory README

Lecture 1, line 1247:
> "**you must create a readme file** זה הדבר הכי חשוב"
> *"you must create a readme file — this is the most important thing"*

Why (line 1249-1250): *"Because you'll create lots of projects, you'll quickly forget what you did."*

### 1.6 Run Then Push

Lecture 1, lines 1344-1357:
- "**run the project**" (line 1345)
- "**push to github**" (line 1349-1351). Quote: *"And here you decide if you want it public or private, so let's say I tell him 'public' so public."*
- Public is the recommended/default ("שיהיה הכי בטוח" — "to be safest", line 894).

### 1.7 Plan Mode Entry — verbatim slash-mode prompt

Lecture 1, line 1227:
> "**insert into plan mode**"

And the master prompt template (lines 1230-1236):
> "**your mission is to create the following PRD document based on the following description**"

He notes: *"I could have written everything in Hebrew or any language"* — but recommends English (or even broken English) because Hebrew in terminals is ugly (line 1237-1239). Typos and broken English are FINE — *"it doesn't matter, he eats it"* (line 1238).

### 1.8 The Full Canonical Sequence (worker should follow verbatim)

Reconstructed from lecture lines 1140-1363:

```
1. Open terminal; enter Claude/Gemini/etc. CLI.
2. /plan (insert into plan mode)
3. "your mission is to create the following PRD document based on the following description: <bullets A, B, C, ...>"
4. → produces prd.md (or docs/<feature>/prd.md for sub-features)
5. "now create plan.md" → strategy + phases + milestones
6. "now create todo.md with minimum 500 tasks (typically 800-1000)"
7. VERIFY: "verify that all PRD demands implemented in todo. You must be very critical." → adds ~200 missed tasks
8. EXECUTE: "execute the to do list one by one and mark each that was done"
9. "you must create a readme file"
10. "run the project"
11. "push to github" (public)
```

For **adding features** to existing project: create a new PRD under `docs/<feature-name>/` and tell Claude to read prior PRDs as reference (lines 1264-1278).

### 1.9 The 150-Line Rule (MANDATORY, drilled across lectures)

Lecture 1, lines 1374-1389:
> "**אסור לאף קובץ של פייתון להיות יותר מ-150 שורות**"
> ***"It is forbidden for any Python file to be more than 150 lines."***

He says he writes this in "אותיות קידוש" (sacred letters) — i.e., a hard rule. Why? Context-window limits cause bugs on large files.

Reconfirmed Lecture 3 line 1879. Reconfirmed Lecture 4 line 1940 (Dr. Segal's example System Prompt): *"Always when working with Python code, write up to 150 lines. These are fixed closed things."*

The unit-test trick to enforce it (line 1389-1396): Claude writes itself a Python checker that scans files; if any > 150 lines, it spawns a sub-agent to plan a split.

### 1.10 The uv Requirement

Lecture 1, lines 1406-1441:
> *"I told you the code MUST run with uv"*

Reasons: (a) auto-manages versions, (b) `uv run` checks for updates online and auto-updates, (c) cross-platform portability, (d) generates `python cache` for faster runs. The cache directory should NOT be pushed to GitHub (line 1447); `pyproject.toml` SHOULD be.

### 1.11 Git Discipline

Lecture 1, lines 270-289: GitHub commit frequency is GRADED.
- *"One of the metrics the agent checks is how much you actually work with GitHub."*
- Big-bang upload = drastic point loss
- "כל כמה שעות שמר כל הזמן... לגיבוי לגיטאב" — commit every few hours.
- Lecture 1, lines 1450-1480: Push EVERY change.

Lecture 4, lines 132-141 reconfirms: agent checks commit count AND progression ("התפתחות"). Quote (line 559): *"I look for improvement, I want to see [it]"*.

PR/merge details: Dr. Segal does NOT track at PR granularity — only commits on `main` (Lecture 4, lines 577-578: *"I look at commits on main, OK? only on main"*).

### 1.12 TERMINALS ONLY — Mandatory CLI

Lecture 1, lines 562-578:
> "**אנחנו נעבוד אך ורק עם טרמינלים. בקורס הזה עובדים אך ורק עם CLI**"
> ***"We work ONLY with terminals. In this course we work ONLY with CLI."***

NO Copilot, NO Cursor, NO Gravity, NO IDE integrations. VSCode allowed only as a Markdown viewer (line 641-643), NOT as the working IDE. Don't use VSCode's terminal either (line 650).

Why (Lecture 3 lines 2042-2073): Terminals are universal, work anywhere, will still work in 5 years. *"Whoever knows terminals, no matter how he falls, always has the basic tool to escape from it."*

---

## 2. Lecture 4 HW2-Relevant Deep Dive

Lecture 4 covers CNN → Transformer → Token Economy → Agent intro. The last third is HW2 conceptual backdrop.

### 2.1 Four Layers of AI (Dr. Segal's Mental Model)

Lecture 4, lines 1799-1860:

1. **Software** (~pre-2022): functions, arguments, return values; rigid templates, deterministic.
2. **LLM**: *"כלי להמיר שפה טבעית לתבניות"* — **"a tool to convert natural language INTO TEMPLATES."** Example: free-text "let's meet tomorrow at 8" → structured calendar event. **HW2 implication**: Watchdog/Gatekeeper sit between free agent output and structured IPC.
3. **AI Agents** (started "2025"): Agent = "LLM + tools". Quote: *"LLM is like a vegetative person. Can't move a hand, foot, head — can ONLY think."* Agent = LLM + ability to ACT via tools.
4. **Sub-agents/orchestration** — implied. HW2's Pro/Con/Judge = agents; Watchdog/Gatekeeper = orchestration-layer.

### 2.2 Agent Anatomy (CRITICAL for HW2 OOP class diagram)

Lecture 4, lines 1898-1928 — Dr. Segal's exact decomposition:

An AI Agent has FOUR components:
1. **LLM** — translates free text to templates
2. **Tools** — *"all the Python code you write"*; the agent's hands/eyes/mouth
3. **Memory / Context Window** — *"Agent memory is called context window. Limited in size."* Million tokens for Gemini and Claude.
4. **RAG** — vector database; *"Last thing an agent has is RAG"* — for retrieving relevant docs by cosine similarity.

**Where MCP fits** (line 1891-1893): *"MCP is in tools, or inside tools."* MCP is a TOOL transport.

### 2.3 Token Economy (Lecture 4, lines 1255-1378, 1929-1994)

For the **Gatekeeper** design:

- **Tokenization**: English 1M tokens ≈ 750K words. **Hebrew: 1M tokens ≈ 400K words** (~2× more expensive). **HW2 implication:** keep agent prompts/system messages in English.
- **Pricing approximation**: ~$5 per 1M tokens (rough).
- **Context Window Math** (lines 1937-1994) — Dr. Segal's exact accounting formula:

  ```
  WC = S + C + Q1 + R1 + A1
  ```
  - `S` = System prompt
  - `C` = Claude.md / CLAUDE.md persistent prompts
  - `Qn` = nth user question
  - `Rn` = nth RAG injection
  - `An` = nth assistant answer

  After turn 2:
  ```
  WC2 = WC1 + Q2 + R2 + A2  (monotonically grows)
  ```

  **CRITICAL** (line 1988-1990): *"**The transformer HAS NO MEMORY. None. It remembers nothing.**"* The illusion of memory is because FULL HISTORY is re-injected every turn. **This is why the Gatekeeper exists** — every byte costs tokens, every turn.

- **Compaction** (line 2424-2429): When context overflows, Claude auto-summarizes — *"summary by procedures"*.

### 2.4 Cost Management Patterns (relevant to Gatekeeper)

Lecture 4, lines 2294-2329:
> *"I think we should give a budget — say each email costs 2 shekels"*
> *"**The whole AI problem is that people stop thinking**"*
> *"They see the car drives itself"*

Systemic risk (lines 2320-2329): internet filling with agent-generated content → training-data feedback loops. **HW2 Gatekeeper should embody discipline of cost-throttling, schema-validation, forcing thought.**

### 2.5 Model & Provider Recommendations

Lecture 1 lines 462-550:
- **Claude** = "המרצדס של התחום" — Mercedes of the field. Best for code. RECOMMENDED.
- **Gemini** = "פנטסטי" — fantastic, better price.
- **GLM 4.7** (Chinese, z.ai) — Dr. Segal personally uses through Claude Code's `/model` switch. *"A year of GLM = a month of Claude max."* Free tier permissive.
- **OpenAI / DeepSeek / Manus / Qwen** all valid.
- Course can be done entirely free.

### 2.6 Slash Commands

Lecture 1, lines 1595-1623 — Dr. Segal's "secret weapon":
> *"Claude has a thing called command, slash command"*

Method:
1. Write your prompt
2. Tell Claude: "convert it into claude CLI command"
3. Claude creates `.claude/commands/<name>.md`
4. Invoke with `/<name>` from now on

Perfect for HW2: `/check-150-lines`, `/verify-todo`, `/push-github`.

### 2.7 Skill vs Tool vs Command (terminology overlap with HW2 spec)

Lecture 4, line 2286: *"I even have **skills** connected to Gmail."* The hierarchy implied:
- **Tool** = the raw callable (function, MCP method)
- **Skill** = a packaged capability (a directory with code + manifest)
- **Command** = a stored prompt template invoked via `/name`

Worker should reflect this layering in the HW2 class diagram.

---

## 3. Cross-Cutting Principles (Dr. Segal's Repeated Themes)

### 3.1 The "Be A Senior, Not A Junior" Doctrine (the meta-thesis)

Lecture 1, lines 53-95: This entire course is "מכפלי 16" (16×-multiplier). Quote (line 78-79): *"At Google 25% of code is now written by AI agents — that's exactly junior-level."*

Implication for HW2: deliver something that shows architectural thinking, not implementation labor.

### 3.2 Creativity & Personal Interpretation (graded explicitly)

Lecture 1, lines 305-341 and 1582-1588:
> *"I expect to see your humanity, your stepping out of the box"*

Assignments given orally, NOT in writing. Each student/pair must interpret personally. **Originality is graded as a BONUS via an outlier-detection agent** (Lecture 4 lines 252-263).

### 3.3 Self-Grading Mechanism (relevant for HW2 submission)

Lecture 1, lines 350-432:
- Set yourself 100 → agent hunts for elephants in the bushes
- Set yourself 60 → agent is lenient
- Best to land within ±5 of agent's grade — there's a BONUS for accurate self-assessment
- Over-estimating is harsher than under-estimating (Lecture 1, lines 594-614)

### 3.4 No Quantitative Feedback — Only Qualitative

Lecture 4, lines 281-309:
> *"You will NOT get quantitative values, no 'I removed 7 points because of XYZ' — no such thing"*

You get a qualitative narrative letter — interpret it like literature ("what did the poet mean").

### 3.5 Critical Thinking About AI Output

Lecture 4, lines 191-198:
> *"The idea of handing reading off to the agent won't lead you anywhere good"*
> *"I want you to ARGUE with the agent, say: this is wrong, do it this way, I read elsewhere it should be this way."*

### 3.6 The "13 Hard Rules" Question

**No explicit numbered list of 13 rules is enumerated in lectures.** The "13" comes from rubric Table 5 (p. 33). What IS consistent across lectures:
1. PRD → Plan → Todo flow
2. 500-1000 todo tasks minimum
3. README mandatory
4. Run before push
5. Push to GitHub (public) frequently
6. 150-line max per Python file (hard rule)
7. uv for Python execution
8. Tree directory structure (no flat code)
9. OO design
10. TDD / unit tests
11. CLI/terminals only — no Copilot/Cursor/IDE
12. Critical engagement with AI output
13. Cybersecurity awareness

---

## 4. Lectures 2 & 3 — Anything Still Relevant

### 4.1 From Lecture 2
- Vector embeddings, cosine similarity, vector DB foundation (lines 540-600). Worker should know cosine-distance is the basis of all agent memory/RAG retrieval.
- No new workflow guidance.

### 4.2 From Lecture 3
- Self-grading mechanism reiterated (lines 63-74) — identical to Lecture 1
- 150-line rule reiterated (line 1879)
- Unit-tests reiterated (line 1881)
- PRD→Plan→Todo confirmed (lines 2027-2036). **Plan = phases/milestones; Todo = granular tasks under the plan.**
- 500-task minimum REAFFIRMED with rationale: lower task counts produce more mock-ups, more forgotten requirements.
- CLI-only justification (lines 2042-2073)
- Lecture 3 line 1872-1874: course booklet is large and Hebrew — don't brute-force paste it into prompts. Be strategic.

---

## 5. Hebrew → English Glossary

Terms the worker WILL encounter:

| Hebrew | English / Meaning |
|---|---|
| סוכן (sokhen) | Agent |
| תת-סוכן (tat-sokhen) | Sub-agent |
| כלי (kli) / טול | Tool |
| מיומנות (meyumanut) / סקיל | Skill |
| פקודה (pkuda) / קומנדה | Command (slash command) |
| טוקן / טוקנים | Token(s) |
| כלכלת טוקנים | Token economy |
| חלון הקשר / קונטקסט וינדואים | Context window |
| זיכרון | Memory |
| מסמך דרישות תוכנה | Software Requirements Document (PRD) |
| תוכנית | Plan |
| משימות | Tasks (todo list items) |
| וייב קודינג | Vibe Coding |
| טרמינל | Terminal (CLI) |
| בקורתי | Critical (as in "be very critical") |
| גרסה | Version |
| לדחוף / "פוש" | Push (to GitHub) |
| מאגר / "רפוזיטורי" | Repository |
| קומיט | Commit |
| מילסטון / פאזה | Milestone / phase |
| מודל שפה | Language Model |
| ארכיטקטורה | Architecture |
| ערעור | Appeal (a grade) |
| מטלה / תרגיל | Assignment / exercise |
| הגשה | Submission |
| ציון | Grade |
| הערכה עצמית | Self-assessment |
| ספרון / חוברת | Booklet / pamphlet (the rubric handbook) |

---

## Synthesis — What the HW2 Worker Should Internalize

1. **Process is the deliverable.** Dr. Segal grades the journey (commits, todo evolution, PRD discipline) as much as the result. Big-bang commits = failed.
2. **Follow the canonical 11-step workflow EXACTLY** (§1.8) — don't improvise.
3. **Todo size: minimum 500, target 800-1000.** Verify step adds ~200 more.
4. **150 lines hard cap** on every Python file. Use a tree, never flat.
5. **uv-managed Python ONLY.** `pyproject.toml` in repo, caches NOT in repo.
6. **OO design + class diagram** is a course expectation (mandatory for HW2 per spec).
7. **Agent = LLM + Tools + Memory + RAG** — Dr. Segal's canonical 4-part anatomy. HW2 class diagram for Pro/Con/Judge should reflect this.
8. **Watchdog = the "force-thinking" pattern** Dr. Segal preaches. **Gatekeeper = token-economy throttle.** Both embody "stop pressing the trigger mindlessly."
9. **JSON IPC** aligns with Dr. Segal's "LLM converts free text into TEMPLATES" framing — Pro/Con produce text, IPC layer forces structured templates the Judge can deterministically parse.
10. **Use English for prompts/system messages** (Hebrew is ~2× more expensive). Code comments either.
11. **Push every meaningful change to GitHub `main`** — Dr. Segal doesn't track PRs, only main commits.
12. **Self-grade carefully.** ±5 of agent's grade = bonus. Over-estimating triggers harsh review.
13. **Originality counts as a bonus** (outlier-detection agent). Don't just match the spec — interpret personally.

---

**Coverage notes:** All 4 lecture transcripts read in full (Lecture 1: 1789 lines; Lecture 2: 1838 lines; Lecture 3: 2197 lines; Lecture 4: 2434 lines). Lecture 05 ("Agents Debate") to be added after transcription.

**Source files (absolute paths):**
- `/Users/salah/Projects/orch-ai-agents/lectures/lecture-01b-vibe-coding-part2.txt`
- `/Users/salah/Projects/orch-ai-agents/lectures/lecture-02-deep-learning.txt`
- `/Users/salah/Projects/orch-ai-agents/lectures/lecture-03-rnn-lstm.txt`
- `/Users/salah/Projects/orch-ai-agents/lectures/lecture-04-transformer.txt`
- `/Users/salah/Projects/orch-ai-agents/lectures/lecture-05-agents-debate.txt` *(when ready)*
