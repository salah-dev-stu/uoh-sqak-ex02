# Salah's Handwritten Notes — HW2 (transcribed by Gemini Vision from a photo)

> **Status**: personal recap, not the authoritative spec. For the authoritative HW2 spec see `CONTEXT-lecture-05.md` (lecture transcript digest). For verbatim PDF spec quotes see `IDEA.md`. Use this file to understand how Salah personally framed the problem — useful when proposing design choices that need his approval.

---

## Project Overview & Architecture

- **Core concept**: simulate a debate between AI agents.
- **The Master/Judge**: a central "Judge agent" (referred to as the master) oversees and manages the dialogue between the debating agents.
- **Debate mechanics**: agents submit claims; the Master extracts the core arguments to facilitate the back-and-forth. The Master can limit text or word count to keep the debate focused.

## Rules & Constraints

- **Concurrency control**: to prevent agents from "talking over" each other or one agent taking over the conversation entirely, the notes suggest implementing time limits (e.g., using Time to prevent process collisions) or turn-based constraints.
  - **Salah wrote "10 שניות" (10 seconds)** as the limit. The authoritative spec says "10 pings per side" (10 argument↔counter-argument cycles), NOT 10 seconds per turn. Two possibilities:
    1. Gemini misread "10 פינגים" as "10 שניות"
    2. Salah meant a per-turn timeout in seconds (separate parameter from ping count)
  - **Action for worker**: treat both as legitimate config params — `pings_per_side: 10` AND `per_turn_timeout_seconds: 10` (or whatever) — confirm with Salah before locking.
- **Stopping conditions**: the Judge constantly checks if convincing, concrete arguments have been reached.
- **The Verdict (highlighted in RED)**: the system must decide a winner, provide reasoning, and assign a final score to each participating agent.

## Technical Implementation

- **RAG integration (highlighted in GREEN/YELLOW)**: note suggesting addition of RAG to enhance the agents' knowledge.
  - Aligns with Dr. Segal's lec05 statement: RAG is **optional**, not mandatory.
- **Processes**: agents run on separate processes. The `main` function initializes the agents; each agent triggers its own process.
- **Keep-Alive**: agents send a "KeepAlive" signal so the process doesn't drop. This is the Watchdog pattern (H21 in RULES.md).
- **Security**: explicit reminder at the bottom — do NOT expose the API key when sending the conversation stages to the API.

## Hebrew Transcription (verbatim, as Gemini read it)

```
Agent Debate מטלה 2

הדמיית ויכוח בין סוכנים.

סוכן שופט - (master).

כל סוכן מגיש טענות.

הבנת שאלת ויכוח (ע"י סוכן 1 או 2) איזה נושא.

הסוכנים מתחילים לייצר דו-שיח מנוהל ע"י שופט או מאסטר.

יוכל להגביל אורך של טקסט / מילים.

מתוך טקסט של סוכן 1 השופט יגזור את הטענה וייצר ויכוח בין השניים.

לחלופין כל סוכן בא מנקודת מבט כדי שנייצר ויכוח.

סוכנים משתלטים אחד על השני אז נייצר לכל אחד 10 שניות ויעבירו את התוכן (בצד: יציגו טענות ויסבירו תוצאות).

תנאי עצירה: שלא נייצר מצב שסוכן משתלט על השיחה.

השופט תמיד בודק אם הגענו לטענות משכנעות.

(טקסט אדום):
חובה להחליט מי נצח בויכוח וחובה שיהיה נימוק. וניתן ציון לכל אחד מהסוכנים.

(טקסט ירוק):
נוכל להוסיף RAG או משהו.

Process של סוכן 1 -> שימוש ב- Time כדי שלא יתנגשו.
Process של סוכן 2 -> כל סוכן מתחזק מול מאסטר KeepAlive.

main מכיל סוכנים, סוכן מפעיל פרוסס.
השיחות בכל שלב נשלחות אל ה- API.
בלי לחשוף API.
```

## Orchestrator's evaluation

Salah's understanding aligns with the authoritative spec. No new requirements were surfaced by these notes. Three potential design refinements:

1. The "10 seconds per turn" idea could become `per_turn_timeout_seconds: 10` in `config/debate_rules.json` — useful as a hang-prevention timeout, separate from the 10-pings-per-side count.
2. The phrase "הסוכן יגזור את הטענה" (Judge extracts the claim) hints that the Judge does light parsing/summarization of child output before passing to the other child — this is a slightly stronger interpretation of the "all traffic through Father" rule than the spec requires. Could be a feature ("Judge as intelligent router"), could be over-engineering. Worker should ask Salah whether the Judge merely RELAYS messages or actively SUMMARIZES them.
3. The note about RAG being optional is correct — keep it out of scope for the initial deliverable, document as future-work extension.
