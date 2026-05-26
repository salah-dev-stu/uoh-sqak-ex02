# Claude Design Prompt — HW2 Live Debate Viewer

**Purpose:** Paste this prompt into [Claude Design](https://claude.ai/design) (or Claude.ai with Artifacts enabled, or Claude Code) to generate a complete, working prototype of the live debate viewer.

**Why this prompt is structured this way:**
- Uses the XML-tagged sections recommended by [Anthropic's Frontend Aesthetics cookbook](https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics) so Claude treats each block as a distinct instruction domain.
- Follows the **9-section DESIGN.md framework** from `awesome-claude-design` (Theme · Palette · Typography · Components · Layout · Depth · Do/Don't · Responsive · Agent Guide).
- Explicit "avoid generic AI aesthetics" callouts so it doesn't default to Inter / Space Grotesk / purple gradients / cookie-cutter chat threads.
- **Responsiveness is the #1 acceptance criterion** because every prior iteration broke at non-default viewport sizes — this is called out at the top, in the do/don't list, and in the acceptance criteria.

---

## ✂ Copy everything below the line into Claude Design

---

```
Build a complete, working, fullscreen web prototype for a LIVE AI DEBATE VIEWER. The prototype must be one self-contained Next.js 16 + React 19 + TypeScript + Tailwind v4 page that compiles and runs locally with `npm run dev`. Backend is already implemented and not changeable — your job is the frontend only.

<context>
A Python orchestrator runs three AI agents — Pro, Con, Judge — that debate a topic in real time over Server-Sent Events. I need a viewer for that debate.

Backend API (already implemented, FastAPI on port 8765):
- POST /api/debate/start?live=<0|1>&n_pings=<int>  → returns { debate_id, topic, n_pings, live }
- GET  /api/debate/{id}/stream                     → SSE stream
- POST /api/debate/{id}/stop                       → stop early

SSE event types arriving on /stream:
  started | message | before_round | after_round | verdict | after_verdict | done | error | stop_requested

A `message` event payload:
  { msg_id: string, from: "pro"|"con"|"judge"|"main", to: "pro"|"con"|"judge"|"main",
    role: "setup_directive"|"argument"|"counter"|"rebuttal", ping_index: number,
    text: string, timestamp: string, tokens_in?: number, tokens_out?: number }

A `verdict` event payload (NESTED — note the inner key):
  { verdict: { pro_total: number, con_total: number, outcome: "pro_wins"|"con_wins"|"debate_aborted"|"budget_exhausted" } }

⚠ Dedup rule the viewer MUST implement (or the same slide renders twice):
  - Skip any payload without an msg_id (boot directive)
  - Skip already-seen msg_ids
  - Skip messages where from ∈ {pro, con} AND to !== "judge" (those are the judge's forwarded copies — render only the original send-to-judge)

For n_pings=10 the full debate is exactly 22 events the viewer should show:
  1 Judge intro · 10 Pro · 10 Con · 1 Judge verdict.
</context>

<user_vision>
This is a PRESENTATION-style viewer, NOT a chat thread, NOT a dashboard, NOT a side-by-side comparison.

Show ONE speaker at a time, fullscreen. The viewer crossfades smoothly from speaker to speaker as the debate progresses, like Apple Keynote slides or a TED talk cut.

Structural rules:
- Judge appears at the BEGINNING (intro slide stating the topic + rules) AND at the END (verdict slide showing tally + winner).
- Pro and Con alternate between the bookends. They never appear on the same slide. They never appear at the same time.
- Each agent has an avatar — a simple visual identity (e.g. colored disc with a glyph: "P" / "C" / "⚖").
- Pro slides anchor visually to the LEFT side of the viewport (text reads left-aligned, avatar top-left).
- Con slides anchor visually to the RIGHT side of the viewport (text reads right-aligned, avatar top-right).
- Judge slides anchor visually to CENTER (text centered, avatar top-center).
- This left/right/center convention is borrowed from parliamentary debate. Government left, opposition right, moderator center.

Scroll-driven timeline:
- The page is NOT a normal scrolling thread. Instead the scroll wheel acts as a TIMELINE SCRUBBER. As the user scrolls down, the current slide crossfades smoothly to the next slide. Scroll up = previous. Lenis + Framer Motion useScroll() + useTransform() is the canonical 2026 pattern; use it.
- During the live debate: when a new SSE message arrives, the page auto-scrolls (programmatic Lenis.scrollTo, ~700ms easeOutCubic) to the latest slide. A bottom-right "◉ LIVE" badge pulses while in follow-live mode.
- If the user manually scrolls UP away from the latest slide, auto-follow pauses and the badge becomes a clickable button: "◉ JUMP TO LIVE". Clicking it smooth-scrolls back to the latest slide and resumes auto-follow.
- After the debate's `done` SSE event, the live badge disappears. The full timeline becomes a permanent scrubbable archive. The user can scroll back and forth through all 22 saved slides forever.

Bottom strip (always visible after the first slide):
- LEFT: running tally — "Pro 7 · Con 4" (Pro accent color · Con accent color) — updates from `after_round` events.
- CENTER: dot scrubber — one tiny circle per slide, color-coded by speaker (Pro · Con · Judge). The current slide's dot is enlarged. Hover shows a tooltip "Con · counter · ping 4". Click jumps to that slide via Lenis.scrollTo.
- RIGHT: "ping 7/22" counter + the live badge.

Landing screen (before any debate starts):
- A single centered dark stage with the title "AGENT DEBATE", a topic field (textarea), pings selector (1-20, default 10), a "Live (real Claude)" checkbox, and one big "▶ START DEBATE" button. That's it. No marketing copy. No hero illustrations.
</user_vision>

<frontend_aesthetics>
You tend to converge toward generic, "on distribution" outputs. In frontend design, this creates what users call the "AI slop" aesthetic. Avoid this: make a creative, distinctive frontend that surprises and delights. Focus on:

Typography: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter. ALSO AVOID Space Grotesk — Claude converges on this across generations; pick something more distinctive (see <use_interesting_fonts> block).

Color & Theme: Commit to a cohesive dark futuristic aesthetic. Use CSS variables for consistency. Dominant near-black canvas with sharp accent colors per agent (one for Pro, one for Con, one for the Judge). No purple gradients. No glassmorphism.

Motion: Use animations for crossfades, avatar entries, body text reveals, and the dot scrubber. Prioritize CSS-only solutions where possible. Use Motion (the framer-motion successor, import from "motion/react") for the scroll-driven effects. Focus on high-impact moments: per-word body text reveal on slide entry creates more delight than scattered micro-interactions.

Backgrounds: Near-black canvas with a soft radial vignette and a very subtle film-grain noise overlay (mix-blend-mode: overlay, ~2% opacity). Do NOT use Aurora WebGL shaders, blob morphs, or other busy backgrounds. The speaker is the focal point.

Avoid generic AI-generated aesthetics:
- Overused font families (Inter, Roboto, Arial, system fonts, Space Grotesk)
- Clichéd color schemes (especially purple gradients)
- Side-by-side Pro/Con panels (this is explicitly rejected — show ONE speaker at a time)
- Chat-thread vertical scroll lists (also explicitly rejected)
- Dashboard layouts with multiple cards
- Glassmorphism / backdrop-filter overload
- Cookie-cutter Vercel-template landing pages
</frontend_aesthetics>

<use_interesting_fonts>
Pick a triad of fonts, all loaded via next/font/google or @import Google Fonts:

- Display (the "AGENT DEBATE" title, agent names PRO/CON/JUDGE, big numbers): one of Clash Display, Bricolage Grotesque, Obviously, or PP Neue Montreal. Use weights 500-700 with letter-spacing +0.08em uppercase.
- Body (the debate text): one of IBM Plex Sans, Newsreader (a serif — surprisingly modern in this context), or Source Sans 3. Weight 300, line-height 1.45, max-width 65ch.
- Mono (the metadata line "argument · ping 3 · 11:32 PM" and the tally numbers): one of IBM Plex Mono, JetBrains Mono, or Fira Code. Weight 400, uppercase, letter-spacing +0.05em, opacity 0.45 for the metadata.

State your specific choice at the top of the artifact. Do NOT default to Space Grotesk + Inter.
</use_interesting_fonts>

<always_use_modern_futuristic_dark_theme>
Visual theme: modern futuristic dark.

Inspirations to evoke (don't copy any one of them — synthesize):
- Apple keynote slide minimalism
- Linear's landing page typography density
- Stripe Sessions stage video
- xAI's Grok website monochrome with one sharp accent
- a movie title card sequence — let typography do the heavy lifting

Concrete rules:
- Background: near-black #07070a (NOT pure #000), with a radial vignette gradient from #0f0f18 center to #07070a edges, plus a 2% opacity film grain noise overlay.
- Foreground primary text: off-white #f0f0f5 (NOT pure white).
- Three sharp accent colors, one per agent. Choose them yourself — they should be vivid but not neon-arcade. Suggested directions: an electric coral or amber for Pro, a deep electric blue or jade for Con, a luminous gold or warm white for the Judge. Each accent also has a "glow" variant at 30-35% opacity for soft halos.
- Every accent is also exposed as a CSS custom property: --color-pro, --color-pro-glow, etc.
- Avatars: 96px circle, 12% accent-color background, 1px accent border, 24px outer glow at the accent-glow color. Glyph is the agent's letter / symbol at 2rem in the display font.
- Transitions are deliberate: 700ms easeOutCubic for slide crossfades, 600ms for Lenis scrollTo, 220ms per-word body text fade with 25ms successive stagger, spring physics (damping 18, stiffness 220) for avatar entry.
- Respect `prefers-reduced-motion: reduce` — collapse all transitions to ≤80ms.
</always_use_modern_futuristic_dark_theme>

<responsiveness_requirements_TOP_PRIORITY>
THIS IS THE #1 ACCEPTANCE CRITERION. Every prior iteration broke here. Be ruthless about it.

The page MUST adapt cleanly to every viewport from 320px wide (small phone) to 3840px wide (4K monitor) without:
- Horizontal scrollbars
- Text overflowing slide boundaries
- Content getting cut off the screen
- Elements becoming unreadably tiny or comically oversized
- Layout shifting awkwardly at intermediate breakpoints (1024px, 1440px)
- Looking "zoomed in" at any common viewport (1280×800, 1440×900, 1920×1080)

How to achieve this:
- Body text font-size: `clamp(1rem, 1.2vw + 0.5rem, 1.875rem)` — viewport-fluid, not jumping at breakpoints.
- Display font-size (agent name, title): `clamp(2rem, 4vw + 0.5rem, 4.5rem)`.
- Slide content container: `max-width: 65ch`, padded `5vh 6vw`, never exceeding 60% of the viewport width for Pro/Con anchored slides.
- Avatar: `clamp(64px, 8vw, 120px)`. Scales with viewport.
- Bottom strip: stays fixed bottom; its three sections stack vertically below ~640px wide.
- The "AGENT DEBATE" landing title MUST fit on one line at 320px (use clamp to shrink).
- DO NOT use fixed px font sizes for typography. DO use clamp() everywhere.
- DO NOT use 100vh for the stage container — use `100dvh` (dynamic viewport height) so mobile browser chrome doesn't cause overflow.
- Test mentally at three sizes before declaring done: 375px (iPhone), 1024px (iPad), 1920px (desktop).
</responsiveness_requirements_TOP_PRIORITY>

<do_and_dont>
DO:
- Show exactly ONE speaker at a time, fullscreen.
- Crossfade smoothly between slides via scroll position (Framer Motion useScroll + useTransform per slide).
- Lenis for smooth scroll inertia + programmatic scrollTo.
- Three distinct accent colors per agent, never confused.
- Pro anchored left, Con anchored right, Judge centered.
- Bottom strip persists across all slides once a debate starts.
- Use clamp() for every typographic size.
- Use 100dvh, not 100vh.
- Respect prefers-reduced-motion.

DO NOT:
- Show Pro and Con side by side. Never.
- Render as a chat thread / message list / Discord-style transcript.
- Use a multi-card dashboard.
- Use Aurora WebGL shaders, blob morphs, animated gradients in the background.
- Use glassmorphism / backdrop-blur / liquid glass.
- Use Inter, Roboto, or Space Grotesk.
- Use purple-pink gradients on dark.
- Hardcode pixel font sizes.
- Use 100vh.
- Show all 22 turns on screen at once.
- Add a hero illustration / marketing copy / signup form / pricing section to the landing screen.
</do_and_dont>

<file_structure_expected>
Generate everything in a single Next.js 16 project. Approximate file tree:

frontend/
├── app/
│   ├── layout.tsx          # fonts via next/font/google, Lenis provider, body
│   ├── page.tsx            # conditional StartScreen | Stage + persistent BottomStrip
│   └── globals.css         # Tailwind v4 @theme block with CSS vars + base styles
├── components/
│   ├── start-screen.tsx
│   ├── stage.tsx           # sticky viewport + useScroll-driven per-slide opacity/y
│   ├── slide.tsx           # one slide (avatar + name + meta + body OR verdict tally)
│   ├── avatar.tsx
│   ├── word-reveal.tsx     # per-word fade on entry
│   ├── bottom-strip.tsx
│   └── lenis-provider.tsx
├── lib/
│   ├── state.ts            # module-level pub-sub (NOT Zustand, NOT Context)
│   ├── sse.ts              # EventSource wrapper + shouldSkip dedup logic
│   ├── api.ts              # startDebate, stopDebate, streamUrl
│   ├── types.ts
│   └── config.ts
└── .env.local              # NEXT_PUBLIC_API_BASE=http://localhost:8765
</file_structure_expected>

<acceptance_criteria>
The prototype is done when ALL of these pass:

1. `npm run dev` starts in <2s, page loads at localhost:3000.
2. Landing screen visible with title + topic + pings + live toggle + START button. No other elements.
3. Clicking START with default options opens the SSE stream and the Judge intro slide crossfades in within 1s.
4. Each new SSE `message` produces a new slide that auto-scrolls into view smoothly.
5. Pro slides anchor visibly LEFT, Con slides anchor visibly RIGHT, Judge slides anchor visibly CENTER. A glance at any slide unambiguously tells you who is speaking by position alone.
6. Scroll wheel up scrubs back through the timeline with smooth crossfades; scroll down advances.
7. Manually scrolling up mid-debate triggers the "JUMP TO LIVE" badge; clicking it smooth-scrolls back to the latest slide and resumes auto-follow.
8. After the verdict event + `done`, the live badge hides and the timeline becomes a permanent scrubbable archive.
9. The dot scrubber at the bottom: hover shows a tooltip naming the agent/role/ping; click jumps to that slide.
10. RESIZING THE BROWSER between 320px wide and 1920px wide keeps every slide coherent — no overflow, no cut-off text, no horizontal scroll, no element looking "zoomed in".
11. `prefers-reduced-motion: reduce` collapses every transition to ≤80ms with no scale or Y translate.
12. The SSE dedup logic correctly skips boot directives, duplicate msg_ids, and judge-forwarded copies (mention this explicitly in your sse.ts file as a comment block).
</acceptance_criteria>

<final_instructions>
Output:
1. State your chosen font triad and three accent colors at the top of your response, before any code.
2. Generate ALL files as separate artifacts so they can be saved individually.
3. Include a one-paragraph "How to run" at the very end.
4. Do NOT explain code line by line. The code IS the explanation.
5. Do NOT add features I did not ask for: no sharing, no auth, no debate history list, no settings page, no dark/light toggle (it's permanently dark), no token-spend chart. JUST the viewer.

Begin.
```

---

## How to use this prompt

1. Go to **[Claude Design](https://claude.ai/design)** (or Claude.ai with Artifacts) — make sure you're on Opus 4.7 or later for the best design output.
2. Paste everything inside the fenced ``` block above (start at "Build a complete...", end at "Begin.").
3. Let Claude generate the artifacts. It will produce one self-contained Next.js project broken into individual files.
4. Save each artifact to its corresponding path in `frontend/` (per the `<file_structure_expected>` section).
5. `cd frontend && npm install && npm run dev` — check responsiveness at multiple viewport sizes before approving.

## If the result is wrong

Iterate via these follow-up prompts (one at a time, after the initial output):

- *"The text is overflowing the slide at 768px. Re-apply the clamp() typography rules in `<responsiveness_requirements>` and reflow body text to max-width 65ch."*
- *"The Pro and Con slides look identical — make the left/right anchoring visually obvious at any viewport. Pro should be ~40% from the left edge, Con ~40% from the right edge, with a generous gutter."*
- *"Drop Space Grotesk. Pick Clash Display or Bricolage Grotesque instead."*
- *"The auto-follow is too aggressive — slow Lenis.scrollTo to 900ms with easeOutQuint."*

Do not iterate on more than one dimension at a time. Each iteration should be one focused change.

---

## Why the previous frontend attempts kept failing

For the record, here's a short post-mortem to inform future iterations:

| Iteration | What went wrong |
|---|---|
| 13a (vanilla HTML) | Plain, no real design system. |
| 13c v1 (Apple-VP + Aurora + glass) | Aurora WebGL + glass = "absolute chaos." Cognitive overload. |
| 13c reset (editorial Fraunces + gold) | Centered single column never filled the viewport — "doesn't span the page." |
| 13d (FloatingLines + GlassSurface) | Glass library broke layout (off-screen at x=-720); background distracted from content. |
| 13e (stage panels) | Multi-panel layout couldn't responsively scale; clamp() couldn't span the design dimensions enough. |
| 13f (React Bits Pro Minimal fork) | A marketing-page template doesn't fit a live debate viewer no matter how good its individual sections look. |
| 13g (scroll presentation, current attempt) | Was on the right track per the user's actual vision but still suffered from "zoomed in" appearance at non-default viewports because every component used hardcoded base sizes instead of clamp() throughout. |

The throughline: **multi-panel layouts cannot be made responsive enough for a casual viewer**, and **fixed px or single-breakpoint sizes break responsiveness**. This prompt forces the AI design tool to commit to one-speaker-at-a-time + clamp()-everywhere, which together remove both failure modes.

---

## References

- [Anthropic Cookbook — Prompting for frontend aesthetics](https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics)
- [VoltAgent / awesome-claude-design — DESIGN.md format](https://github.com/VoltAgent/awesome-claude-design)
- [rohitg00 / awesome-claude-design — design system inspirations](https://github.com/rohitg00/awesome-claude-design)
- [How to Use Claude Design — Tosea.ai guide (2026)](https://tosea.ai/blog/claude-design-complete-guide)
- [Claude Artifacts: What They Are and How to Use Them (2026)](https://albato.com/blog/publications/how-to-use-claude-artifacts-guide)
