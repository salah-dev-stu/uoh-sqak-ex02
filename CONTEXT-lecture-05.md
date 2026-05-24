# Lecture 05 — "Agents Debate" — HW2 Authoritative Digest

**Source:** `/Users/salah/Projects/orch-ai-agents/lectures/lecture-05-agents-debate.txt` (2114 lines, 143 KB, transcribed by whisper.cpp from the recorded Spring 2026 lecture).

> **The lecture is the absolute authority.** Dr. Segal explicitly says (line 1106): *"אני באמת לא כותב לכם אותה, כל אחד אומר את ההידקטציה שלו ועוצר אותה"* — "I'm really not writing it down for you; each person takes their own dictation." The 8-page PDF summary is downstream of this recording. **Where they disagree, this digest's findings (and the underlying transcript) override the PDF.**

**Coverage:** lines 1-30 = whisper Knesset boilerplate (ignore). Lines 32-1050 = backdrop (Agent/Skill/Command/Subagent hierarchy, Context Engineering, Read/Select model). Lines 1056-1102 = mid-lecture noise. **Lines 1104-1780 = HW2 spec delivered orally (CRITICAL).** Lines 1936-2113 = post-lecture chatter.

---

## 1. 🚨 CONTRADICTIONS with the spec PDF (apply to IDEA.md)

### 1.1 RAG is explicitly OPTIONAL for HW2

Line 1228-1232 — verbatim:
> *"אם מישהו מכם למשל רוצה להוסיף רג... אז מי שבוחר לעשות את זה, **זה לא חובה, זה לא חובה, אני חוזר ואומר, לא חובה רג**."*
>
> *"If someone wants to add RAG... but for whoever chooses to: **it's NOT mandatory, NOT mandatory, I repeat: RAG is NOT mandatory**."*

**Apply:** No contradiction with IDEA.md (which doesn't mention RAG), but explicitly state RAG is out of scope in `docs/PRD.md` "Constraints" — showing the worker read the lecture.

### 1.2 Web-search tool is a GRADED ENFORCEMENT GATE

Lecture (line 1233-1239) is stronger than the PDF:
> *"אני כן מצפה לחיפוש באינטרנט, **לכן תול אחד לפחות של חיפוש באינטרנט יהיה לכם**... חיפוש חייב להיות, **כדי שלא יהיה בעיות בבדיקה**."*
>
> *"I DO expect internet search — therefore **at least one tool for internet search must exist for you**... search is mandatory **so there are no problems in grading**."*

**Apply:** Strengthen `RULES.md` H6 — "absent web-search tool = automatic point loss." `tools/web_search.py` must be present in the repo tree even if it's a thin wrapper.

### 1.3 Strong opposition to "all via Claude CLI" — STRONGER than PDF

Line 1281-1297:
> *"מי שרוצה לעשות את הכל דרך ה-Cloud CLI, **אני לא ממליץ. לא ממליץ**... **אני מצפה שאתם תכתבו פרוסס של הסופרן הראשי, פרוסס של מתנגד A, מתנגד B**, ושהם מנהלים ודברים עובדים."*
>
> *"For anyone who wants to do everything through Cloud CLI — **I do not recommend it. Do NOT recommend it**... **I expect you to write a process for the main supervisor, a process for opponent A, opponent B**, and that they manage and things work."*

**Apply:** Update IDEA.md build order — Phase 2 (CLI command) is **a stepping stone only**, NOT a deliverable. Final deliverable = Python multi-process Judge/Pro/Con.

### 1.4 Phase 1 (manual two-terminal) is STRONGLY graded

Line 1896-1909:
> *"אני ממליץ לכם להתחיל את כל העבודה הזאת, **ידנית**. יפתחו שני קלודים, יפתחו את ChatGPT ואת Gemini... אחד, תגידו, אתה תהיה מומחה לברצלונה, אתה מומחה לריאל מדריד... להעביר ביניהם... **כל הזמן תעשו ידנית, תרגישו מה זה דיבייט בין סוכנים. בלי אורכסטרציה וכאלה.**"*
>
> *"I recommend you start all this work **manually**. Open two Claudes, open ChatGPT and Gemini... 'you'll be Barcelona expert, you Real Madrid'... pass [messages] between them... **do it manually all the time, FEEL what debate between agents is. Without orchestration.**"*

**Apply:** Phase 1 MUST produce screenshots embedded in README — evidence of manual exploration before coding. Update CLAUDE.md and IDEA.md to make this hard.

---

## 2. ✅ AMBIGUITY RESOLUTIONS (revise IDEA.md defaults)

### #1: Word-count cap per turn — NOT RESOLVED
Lecture mentions "limit by time or words" (line 1124-1126) without numbers. **Keep 250-word default**, note in config: "lecturer left open; chosen to balance richness against token cost."

### #2: JSON wire schema — PARTIALLY RESOLVED
Line 1437-1444 — verbatim: *"ההמלצה שלי זה ג'ייסונים... **ג'ייסונים זה תבניות**"* ("My recommendation is JSONs... JSONs are templates"). Format = JSON confirmed; schema still open. **Keep proposed schema; add the "JSONs are templates" quote as rationale in `docs/PRD_ipc_bus.md`** (ties to Dr. Segal's "LLM converts text to templates" thesis from Lec 04).

### #3: Judge intervention threshold — **REVISE FROM 3 TO 1 (per-message check)**
Lines 1168-1190, 1410-1430. Dr. Segal: *"השופט צריך כל הזמן לבדוק את הסוכנים שלו"* — **"The Judge must constantly check his agents."** Plus line 1182-1184: "the Father ensures they EACH TIME say something Against, not allowing unwarranted agreement."

**REVISE:** `drift_intervention_threshold: 1` with action `correct_and_replay`. The Judge checks EVERY message for role-faithfulness; on violation, issues a corrective directive and asks for a fresh attempt. Continuous-oversight model, NOT after-N-strikes.

### #4: Persuasiveness scoring axes — ADD 5th AXIS
Line 1576: *"אתה חייב בתשובה להתייחס למה שהוא אמר. זה חייב להיות דו-שיח."* ("You MUST reference what he said. It must be a dialogue.") Plus the "no-tie" 70/80 differential model (line 1404).

**REVISE:** 5 axes × 20 each = 100:
1. **Clarity** — argument is well-structured
2. **Evidence** — backed by citations from web search
3. **Rebuttal** — addresses opponent's prior points
4. **Novelty** — brings new angles, not repetition
5. **Role-fidelity** — stays in role, doesn't drift toward agreement ← NEW from lecture

### #5: Web search provider — NOT RESOLVED
Lecturer doesn't care; only requires "there is one." **Keep Brave Search API default**, document in PRD_web_search_tool.md ADR.

### #6: Process model — STRONGLY RESOLVED (multiprocessing confirmed)
Lines 82-86, 394-409, 1295-1298. Dr. Segal: *"סוכנים זה process... זה IPC... **למדתם סיגנל, טיפו, Q, תורים** — אלו הן השיטות שעליהן הוא לתקשר בין סוכנים."* ("Agents are processes... it's IPC... you learned **Signal, FIFO/Pipe, Queue, queues** — those are the methods to communicate between agents.")

**KEEP `multiprocessing.Process` + `multiprocessing.Queue`** but add to `docs/PLAN.md` ADR: enumerate all four OS-IPC mechanisms (Signal, FIFO, Queue, Pipe) and explain why `multiprocessing.Queue` was chosen. Shows OS-class fundamentals understanding.

**Plus add timeout requirement explicitly** (line 1297-1298): *"לא לשכוח לשים timeoutים, כי יכול להיות שמישהו נתקע"* ("don't forget timeouts, because someone might get stuck"). Already in H8 — reinforce.

### #7: LLM provider per agent — **REVISE: mixed providers ENCOURAGED**
Line 200-213 + 1131-1142: *"תוודאו שכל אחד בא ממקום אחר כדי שייווצר ויכוח"* ("ensure each comes from a DIFFERENT PLACE so an argument is created"). Plus line 1896-1908 — manual demo uses Claude + ChatGPT + Gemini explicitly.

**REVISE:** Default = **different provider per debater** (Pro on Claude, Con on Gemini, e.g.); same provider acceptable IF Skills enforce contradiction strongly. Gatekeeper supports mixed providers in `config/agents.json` per-agent.

### #8: Pair vs solo — NOT RESOLVED
Lecture never discusses pair/solo. **Keep PDF default: pairs required.** User has confirmed pair (Salah + Andalus).

---

## 3. ➕ NEW REQUIREMENTS not in PDF (add to IDEA.md + RULES.md)

### 3.1 Judge MUST issue per-agent setup directives at debate start

Line 1213-1221, 1411-1433:
> *"שימו לב שכשהשופט מתחיל, הוא צריך להפעיל את הגנים... והוא צריך להגיד להם: אלה חוקי המשחק, אתה חייב להיות נגד..."*
>
> *"When the Judge starts, he needs to activate the players... and tell them: 'These are the rules of the game, you must be Against...'"*

And (line 1426-1434): *"הוא צריך להגיד: זה אתה, התפקיד שלך, זה מה שאני מצפה. **באיזה פורמט אתה רוצה לקבל את התשובה?**"* — *"He needs to say: 'this is you, your role, this is what I expect. In what format do you want the response?'"*

**Add to JSON schema:** new message `role: "setup_directive"` sent from Judge to each child at debate start. Contents: stance, rules, expected JSON response format.

### 3.2 Judge MUST police vulgar/political-incorrect language

Line 1553-1559:
> *"אסור שפה בוטה. אחת הבדיקות שאתם צריכים לעבור מהאבא, שהוא בודק שאין שימוש בשפה בוטה, שזה מה שנקרא **פוליטיקלי קורקט**, ושזה מכבד אחד את השני"*
>
> *"Vulgar language is forbidden. One of the checks the Father must do: verify no vulgar language, **Politically Correct**, mutual respect."*

**Add to RULES.md** as **H12** (renumbering subsequent rules): "Judge enforces PC/respectful-language gate. Vulgar messages are sanitized or rejected by Judge BEFORE re-broadcasting to opponent." Implementation: PC filter inside `JudgeAgent.handle_message()` as a post-processor.

### 3.3 Skills MUST be PROJECT-LOCAL, never global

Line 1330-1332:
> *"תשימו לב שזה סקילים של פרויקט, **אל תשימו את זה בסקילים הגלובליים**, כי אתם לא רוצים שאחר כך בפעולות אחרות ייכנסו לכם הסקילים האלה"*
>
> *"Notice these are PROJECT skills — **don't put them in global skills** because you don't want them leaking into other operations."*

**Add to RULES.md** as **H13**: "Skills live under `.claude/skills/<name>/` in the project, NOT `~/.claude/skills/`. Repo audit verifies this."

### 3.4 Non-reproducible outcomes are DESIRED

Line 1581-1597 — student asks if outcome should be reproducible:
> Dr. Segal: *"**פעם הבאה, הם מדברים, מדברים, מדברים, ובפעם הבאה ריאל ניצח. מעולה, טוב מאוד, זה הכי טוב.**"*
>
> *"**Next time, they talk, talk, talk, and next time Real wins. Excellent, very good, that's the BEST.**"*

**Add to README.md Behavior section:** "The same topic can yield different winners across runs — this is intentional and DESIRED per Dr. Segal (lecture 05 line 1597)." Pre-empts grader confusion.

### 3.5 Lying is ALLOWED — opponent catches via web search

Line 1483-1491 — confirmed:
> *"מותר. הצד הנגדי אמור לתפוס אותם — זה חלק מכושר השכנוע"*
>
> *"Allowed. The opposing side is supposed to catch them — part of persuasion power."*

The Judge does NOT verify factual claims. Document in `docs/PRD_pro_agent.md` and `docs/PRD_con_agent.md` that web-search has **DUAL purpose**: (1) cite own evidence, (2) fact-check opponent's claims.

### 3.6 Bonus opportunity: multiple Skills per agent

Line 1254-1259:
> *"לא לשים סקיל אחד לשוחק, **לתת לו כמה סקילים. למשל, סקיל שהוא מומחה לייצר טיעונים, סקיל אחר של מישהו שמומחה לנתח את הטיעונים של השני**"*
>
> *"Don't put one skill per player — **give him several skills. E.g., one expert at generating arguments, another expert at analyzing the opponent's arguments**."*

**Document in PLAN.md "Future work":** multi-skill bonus opportunity (e.g., `argument_generator_skill/` + `opponent_analyzer_skill/` per debater). Implementing this earns originality points.

### 3.7 Use web search to BUILD the Judge's expertise

Line 1519-1528:
> *"מה המומחיות של האבא? **מומחה לדיבייטים**. תגיד לג'מנאי: תגדיר לי, תחפש בעולם מי המומחה מספר אחת לדיבייטים, ומה הקריטריונים, ואז תיקח את הקריטריונים האלה ותיתני את זה כסיספרומפט לאבא."*
>
> *"The Father's expertise = debate expert. Tell Gemini: 'search the world for who's the #1 debate expert and what criteria he sets,' then take those criteria and give them as system prompt to the Father."*

**Worker action:** Before scaffolding the Judge's system prompt, do a one-off research session (search for "parliamentary debate scoring", "Lincoln-Douglas format", "Robert's Rules") and derive the Judge's scoring criteria from real-world authority. Document the research in `docs/PROMPTS.md` or as an ADR. Graded as creativity signal.

### 3.8 Logging defaults: FIFO 20 files × 500 lines (verbatim)

Line 1747-1776 — Dr. Segal's exact config:
> *"לעבוד בפיפו, ונגיד אני אומר לו של 20 קבצים, ובכל קובץ אני אומר לו נגיד 500 שורות... זה למשל שני פרמטרים בקובץ קונפיגורציה שלי, **הם לא בהארדקוד**"*
>
> *"Work in FIFO, say 20 files, each say 500 lines... two parameters in my config file, **NOT hardcoded**."*

**Confirmed default for `config/logging_config.json`:**
```json
{"rotation": "fifo", "file_count": 20, "lines_per_file": 500}
```

### 3.9 SDK enables agent-driven self-testing

Line 1736-1745:
> *"אם אתם עובדים עם SDK, אתם בעצם יכולים לקחת את Cloud CLI ולהגן לו: תבדוק לי את התוכנה בהרצאה, ואז הוא יכול ממש לנגן לכם על התפריטים, ואז כל פעם שיש באג הוא ממש רואה את זה."*
>
> *"If you work with SDK, you can take Cloud CLI and tell it 'test this software for me', and it can really play with you on the menus, and every time there's a bug it sees it."*

**Worker action:** The terminal menu must be **letter/number-keyed** ("press A", "press B") so Claude CLI can drive it from a slash command for automated self-testing. Document this as the SDK's design rationale in `docs/PRD.md`.

### 3.10 Watchdog with KPI/heartbeat — explicitly graded

Line 1302-1314:
> *"אתם צריכים שיהיה לכם וודג'דוגים על הפרוססים שלכם... אתם צריכים לשים KPI ולראות שהדבר חי ועובד, **ואם הוא נתקע, לעשות kill לפרוסס ולהתחיל בו מחדש**."*
>
> *"You need watchdogs on your processes... set KPI to see the thing is alive and working, **and if it gets stuck, kill the process and restart it**."*

**Implementation:** (a) Heartbeat ping per child process, (b) `kill -9` on stuck process, (c) restart logic with backoff. Document in `docs/PRD_watchdog.md` with explicit ping/timeout/restart cycle parameters in `config/debate_rules.json`.

---

## 4. 🎬 LIVE DEMOS Dr. Segal walked through

| Demo | Lines | HW2 use |
|---|---|---|
| Create new agent via Claude CLI (`/agent` → global vs local → generate) | 446-495 | Prototype Pro/Con/Judge in CLI first, then export to project-local `.claude/agents/` |
| GLM 4.7 via z.ai through Claude CLI (`glub5` alias) | 232-274 | Budget-friendly LLM provider option; document in README cost analysis |
| Skill auto-discovery via `description:` field | 530-535, 717-733 | Keep descriptions PRECISE — Claude loads ALL into system prompt at start (token cost) |
| Read/Select Context Engineering pattern | 822-880 | Judge agent can use Read/Select to manage its prompt (extract child key points, select only relevant for scoring) — bonus design |
| `--dangerously-skip-permissions` flag | 239-248 | Use during local dev to avoid endless approval prompts |

---

## 5. ❓ STUDENT Q&A — key clarifications

| Q | Line | Answer summary |
|---|---|---|
| Father intervenes on true opposition? | 1185 | NO — only on drift / false agreement / off-topic / vulgar |
| Sub-agent definition? | 1206 | Student's choice (subprocess/multiprocessing/threading/Task tool) — document rationale |
| RAG required? | 1228 | NO, optional |
| Budget constraint reduces pings 10→5? | 1241 | YES allowed, note in README, no penalty |
| Tie allowed? | 1400 | **ABSOLUTELY NOT**; differential 70/80 OK; one winner must be named |
| Children know stance directly? | 1411 | NO — Father gives directives at runtime |
| Children read spec themselves? | 1424 | Topic yes, operational rules from Father |
| Judge knows topic (football, etc.)? | 1449 | **NO** — topic-blind by design; system prompt must NOT mention topic |
| Truth wins over persuasion? | 1471 | NO — persuasiveness only; opponent catches lies |
| Debate flows directly child↔child? | 1501 | NO — through Father strictly |
| Outcome reproducible? | 1581 | NO — different runs different winners is BEST |
| GUI required? | 1857 | NO — terminal menu only; GUI harder to grade |
| Documentation requirements? | 1856-1894 | README + Markdown + screenshots + actions + full session-1 dialogue |

---

## 6. 📅 DEADLINES & SCHEDULE

### No explicit HW2 deadline in this lecture
Worker MUST check Moodle: https://mw26.haifa.ac.il/mod/assign/view.php?id=264177

### Holiday context
- Line 1779-1796: next week (Shavuot) cancelled. Following Friday: half-holiday, possibly Zoom-only.
- Line 1994-1997: Dr. Segal implies students should use Shavuot break for HW2 ("here's your chance to celebrate the dairy delicacy and debate cheesecake vs chocolate cake"). **Strong signal: deadline is shortly after Shavuot.**

### Inaccessible repo = AUTO-ZERO confirmed
Line 1641-1652:
> *"יש פה שלושה או ארבעה שהגישו לי עם גיטאפ בלי פתיחה, ולא יכולתי לפתוח אותם, **ויש שם אפס**"*
>
> *"3 or 4 submitted with GitHub but without sharing — couldn't open them — **there's a ZERO**."*

NO resubmission. Either public OR explicitly share with `rmisegal@gmail.com`. **Verify before submission.**

---

## 7. 🧠 PHILOSOPHY threads for the worker

1. **"Not ChatGPT users — Context Engineers"** (line 843-849) — every token deliberate; document Gatekeeper's token economics
2. **Orchestration = token economy** (line 768-784) — every agent doubles the context window; justify the 3-agent design
3. **Router/Select mindset** (line 759-764, 832-865) — Judge's prompt should be selectively constructed, not full history
4. **Code is the artifact, conversation is evidence** (line 1284-1297) — Python multi-process is the deliverable
5. **Manual-first, autonomous-last** (line 1896-1909) — Phase 1 = manual debate screenshots
6. **Failure documented > "perfection" claimed** (line 1875-1879) — README should narrate bugs and fixes honestly

---

## 8. Summary — CRITICAL CHANGES TO APPLY

Apply to `hw2/IDEA.md`:

1. ✏️ RAG explicitly optional (§1.1)
2. ✏️ Web-search is a graded gate (§1.2)
3. ✏️ CLI-only is NOT a deliverable (§1.3)
4. ✏️ Manual two-terminal Phase 1 with screenshots (§1.4)
5. ✏️ **Drift threshold: 3 → 1** (§Ambiguity #3)
6. ✏️ **5th scoring axis: role-fidelity** (§Ambiguity #4)
7. ✏️ **Mixed providers per agent ENCOURAGED** (§Ambiguity #7)
8. ➕ Judge setup directives at runtime (§3.1)
9. ➕ Non-reproducible outcomes desired (§3.4)
10. ➕ Multi-skill per agent bonus (§3.6)
11. ➕ Search-built Judge expertise (§3.7)
12. ➕ Letter-keyed menu for SDK self-testing (§3.9)

Apply to `hw2/RULES.md`:

13. ➕ **H12: Judge PC/vulgar filter** (§3.2)
14. ➕ **H13: Skills project-local only** (§3.3)
15. ✏️ Logging defaults: FIFO 20×500 (§3.8) — already in Appendix A14
16. ✏️ Watchdog with KPI heartbeat (§3.10)
17. ✏️ Inaccessible repo = auto-zero, confirmed by lecturer (§6)

**Source:** lecture transcript `/Users/salah/Projects/orch-ai-agents/lectures/lecture-05-agents-debate.txt`. Reference line numbers in any verbatim quoting.
