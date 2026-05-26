# Phase 13 — Scroll-driven Debate Presentation (Design Spec)

**Date:** 2026-05-26
**Status:** Approved by user; ready for plan
**Supersedes:** all prior Phase 13c/d/e/f frontend specs (now wiped from disk)

## 1. Vision

A presentation-style live debate viewer. One agent fills the viewport at a time. Smooth crossfades between turns. Scroll wheel scrubs the timeline. Judge bookends the debate (intro + verdict) at center stage; Pro speaks from the left, Con from the right. Modern, futuristic aesthetic — dark stage, neon agent colors, generous typography, no clutter.

This replaces the rejected Phase 13a HTML page and the seven rejected Phase 13c–f iterations. The backend (FastAPI + SSE + orchestrator at `src/agent_debate/web/`) is unchanged.

## 2. Why this design (lessons from the rejected iterations)

Seven prior attempts failed because they all tried to show **everything at once**: side-by-side panels, dashboards, multi-column comparisons, chat threads. The user's repeated feedback was variations of "this is chaos" and "it doesn't fit the page." The fix is the opposite metaphor: **show one thing at a time, perfectly.**

This design also fixes the responsiveness problem (the dominant complaint in iterations 13c–13e). A single fullscreen slide trivially adapts to any viewport — there is no multi-panel layout to break.

## 3. User flow

1. **Landing**: Empty dark stage, centered "AGENT DEBATE" title, topic field, pings selector, Live toggle, START button.
2. **Click START**: `POST /api/debate/start?live=<0|1>&n_pings=10` → backend returns `{debate_id}`. Frontend opens `EventSource("/api/debate/{id}/stream")`. Landing fades out, Judge intro slide fades in.
3. **Judge intro slide** (auto, centered): Judge avatar, "JUDGE — setup · ping 0", body = `setup_directive` text (today's topic + rules).
4. **Live debate**: each `message` SSE event appends a new slide. The page auto-scrolls smoothly to the latest slide (~600ms crossfade). Pro slides are left-anchored, Con slides are right-anchored.
5. **User intervention** (optional): scrolling back pauses auto-follow. A bottom-right `◉ JUMP TO LIVE` badge pulses; clicking it resumes auto-follow.
6. **Verdict**: after the final ping, the Judge centered slide fades in with `Pro X · Con Y` tally + winner + tagline.
7. **Archive mode**: `done` SSE event arrives → live badge disappears → full timeline is scrubbable indefinitely. User can scroll-scrub or click any bottom-strip dot to jump.

## 4. Layout

### 4.1 Slide types

| Type | Anchor | Avatar | Color accent | Body |
|---|---|---|---|---|
| Judge intro | center | ⚖ disc | gold `#ffc94c` | setup_directive text |
| Pro turn | left 40% of width | `P` disc | magenta `#ff3da8` | argument text |
| Con turn | right 40% of width | `C` disc | cyan `#3da8ff` | counter text |
| Judge verdict | center | ⚖ disc | gold | tally + winner + tagline |

### 4.2 Slide composition

```
[avatar 96px, color glow ring]
[AGENT NAME — large, tracked +0.1em, agent color]
[role · ping N · timestamp — monospace, 11px, 60% opacity]

[body text — light-weight, 1.5rem mobile / 2rem desktop,
 line-height 1.4, max-width 65ch, word-by-word reveal]
```

### 4.3 Bottom strip (always visible after first slide)

```
Pro 0 · Con 0    ⚖•••○•○•○•○•...•○•⚖     ping 1/22    ◉ LIVE
[running tally]  [dot scrubber, color-coded] [counter]  [live badge]
```

- Each dot is a slide. Current slide's dot is 1.4× bigger. Hover = tooltip `Pro · opening · ping 3`. Click = smooth-scroll to that slide.
- Tally updates from `after_round` SSE events.
- Counter shows `ping N / 22` (22 = 1 intro + 20 turns + 1 verdict).
- Live badge: `◉ LIVE` (red, pulsing) during streaming. Auto-follow paused → text becomes `◉ JUMP TO LIVE` (clickable). After `done` event → badge disappears.

## 5. Scroll-driven animation

### 5.1 Mechanics

- Page DOM = a single tall scrollable section: `height: (N_slides + 1) × 100vh`.
- Inner stage container: `position: sticky; top: 0; height: 100vh; overflow: hidden`.
- Lenis (already in template stack) provides smooth scroll inertia.
- Framer Motion `useScroll()` measures scroll progress 0..1 across the full document.
- For each slide `i`, its `progress = clamp((scroll - i/N) × N, 0, 1)`.
- Opacity curve: `progress 0→0.3` fade in, `0.3→0.7` fully visible, `0.7→1.0` fade out.
- Y-translate curve: `progress 0→0.3` enter from +24px, `0.7→1.0` exit to -24px.
- Avatar scale curve: enters from 0.92, springs to 1.0 with damping 18, stiffness 220.
- Body text: word-by-word reveal when slide enters the viewport. Each word fades in over 220ms (opacity 0 → 1, easeOutCubic). Successive words start 25ms apart. A 60-word paragraph completes in ~1.7s.

### 5.2 Auto-follow during live mode

- A `followLive` boolean lives in module-level pub-sub state. Default: `true`.
- New `message` SSE event → if `followLive`, programmatic smooth-scroll to last slide via Lenis `scrollTo`. Duration ~700ms, ease `easeOutCubic`.
- User scroll input (wheel, trackpad, key) → set `followLive = false`. Live badge becomes `JUMP TO LIVE` (clickable).
- Click `JUMP TO LIVE` → smooth-scroll to last slide → set `followLive = true`.
- After `done` SSE event → `followLive` becomes irrelevant; badge hides.

### 5.3 Click-to-jump (dot scrubber)

- Clicking a dot in the bottom strip → Lenis `scrollTo(dotIndex × viewHeight)`. Pauses `followLive`.

## 6. Aesthetic — modern futuristic

### 6.1 Color system

```
--bg-base       #07070a   (near-black, slight blue tint)
--bg-vignette   radial-gradient from #0f0f18 to #07070a
--fg-primary    #f0f0f5   (off-white)
--fg-muted      rgba(240, 240, 245, 0.45)
--fg-dim        rgba(240, 240, 245, 0.18)

--pro-accent    #ff3da8   (magenta)
--pro-glow      rgba(255, 61, 168, 0.35)
--con-accent    #3da8ff   (cyan)
--con-glow      rgba(61, 168, 255, 0.35)
--judge-accent  #ffc94c   (gold)
--judge-glow    rgba(255, 201, 76, 0.30)
```

### 6.2 Typography

- **Display** (agent name): `Space Grotesk` (variable, weight 500), letter-spacing `+0.08em`, uppercase, 1.75rem mobile / 2.5rem desktop.
- **Body** (debate text): `Inter` (variable, weight 350), 1.5rem mobile / 2rem desktop, line-height 1.45, max-width 65ch.
- **Metadata** (role · ping · time): `JetBrains Mono`, weight 400, 0.7rem, uppercase, letter-spacing `+0.05em`, opacity 0.45.
- **Tally / counter**: `JetBrains Mono`, weight 500, 0.75rem.

All three fonts available via `next/font/google`. Variable weights to keep payload small.

### 6.3 Avatar

- 96px circle, agent-color fill at 12% opacity, 1px solid agent-color border, 24px outer glow halo (agent-color at 35%).
- Center glyph: `P`, `C`, `⚖` in agent-color at 100%, weight 500, 2rem.
- When this slide is the **latest live** slide: glow halo pulses (1.5s loop, opacity 0.35 ↔ 0.55). Otherwise static.

### 6.4 Background

- Base `--bg-base` with a soft radial vignette `--bg-vignette` from center.
- Very subtle film grain (16x16 SVG noise tiled, opacity 0.025, mix-blend-mode overlay).
- A single thin horizontal line at vertical center, 1px, `rgba(255,255,255,0.04)` — barely-there stage-line cue.
- **No** Aurora, WebGL shaders, glass effects, or other backgrounds. The focus is the speaker.

### 6.5 Transitions

| Element | Duration | Easing |
|---|---|---|
| Slide opacity (scroll-driven) | continuous | linear (driven by scroll) |
| Slide Y-translate (scroll-driven) | continuous | linear |
| Avatar enter scale | spring | damping 18, stiffness 220 |
| Body word stagger | 25ms per word | linear |
| Auto-scroll to latest | 700ms | easeOutCubic |
| Click-to-jump | 600ms | easeOutCubic |
| Landing → first slide | 800ms | easeInOutCubic |

All transitions respect `prefers-reduced-motion: reduce` — durations collapse to ~80ms, no scaling or Y-translate.

## 7. SSE handling

Reuses the proven pattern from earlier iterations (now wiped, but understood):

```ts
case "message": {
  const p = evt.payload as Record<string, unknown>;
  if (typeof p.msg_id !== "string") break;          // skip boot directive
  if (seenIds.has(p.msg_id as string)) break;       // dedupe
  if ((p.from === "pro" || p.from === "con") && p.to !== "judge") {
    seenIds.add(p.msg_id as string);                // skip judge-routed forward
    break;
  }
  appendSlide(p);
  if (followLive) lenis.scrollTo(latestSlideY, { duration: 0.7 });
  break;
}
```

Boot directive (no `msg_id`) → render as Judge intro slide using the `directive` field as body.
Verdict event → render Judge verdict slide with nested `verdict: { pro_total, con_total }` and `outcome`.

## 8. State model

Module-level pub-sub (no Zustand, no Context):

```ts
interface SlideState {
  slides: Slide[];          // ordered, including Judge intro and verdict
  currentIndex: number;     // which slide is currently visible (driven by scroll)
  followLive: boolean;
  status: "idle" | "live" | "done" | "error";
  proTotal: number;
  conTotal: number;
  pingCounter: { current: number; total: number };
}

interface Slide {
  id: string;               // msg_id, or "intro"/"verdict" for synthetic slides
  speaker: "pro" | "con" | "judge";
  variant: "intro" | "argument" | "counter" | "rebuttal" | "verdict";
  pingIndex: number;
  text: string;
  timestamp: string;
  // verdict-only fields:
  proScore?: number;
  conScore?: number;
  outcome?: "pro_wins" | "con_wins" | "debate_aborted" | "budget_exhausted";
}
```

## 9. File structure

```
frontend/
├── app/
│   ├── layout.tsx          # fonts, Lenis provider, global styles
│   ├── page.tsx            # the single presentation page
│   └── globals.css         # CSS variables, base styles
├── components/
│   ├── start-screen.tsx    # landing form with topic, pings, Live toggle
│   ├── stage.tsx           # the sticky viewport + slide list
│   ├── slide.tsx           # individual slide (avatar + body + metadata)
│   ├── avatar.tsx          # 96px disc with glyph and color glow
│   ├── bottom-strip.tsx    # tally + dot scrubber + counter + live badge
│   ├── lenis-provider.tsx  # smooth scroll setup
│   └── word-reveal.tsx     # word-by-word body text animation
├── lib/
│   ├── state.ts            # module-level pub-sub store
│   ├── sse.ts              # EventSource wrapper, message dedup
│   ├── types.ts            # Slide, SlideState, SSE payloads
│   └── api.ts              # POST /api/debate/start, POST /api/debate/{id}/stop
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── .env.local              # NEXT_PUBLIC_API_BASE=http://localhost:8000
```

Backend at `src/agent_debate/web/` is **untouched**.

## 10. Tech stack

- **Next.js 16.1.1** (App Router) — single static page
- **React 19**
- **TypeScript 5**
- **Tailwind v4** — utility-first styling
- **Framer Motion (motion)** — `useScroll`, `useTransform`, `useSpring`
- **Lenis 1.3** — smooth scroll inertia + programmatic `scrollTo`
- **next/font/google** — Space Grotesk, Inter, JetBrains Mono
- **EventSource** (native browser API) — SSE consumption
- **No React Bits Pro components** — none of them fit. Pure custom build.

## 11. Out of scope

- The previously-attempted "live vs replay split", glass effects, Apple Aurora, WebGL backgrounds, dashboard panels, chat threads.
- Mobile-specific gestures (swipe). Scroll wheel + trackpad cover mobile via natural touch-scroll.
- Multi-debate history view. Single debate at a time; refresh starts a new one.
- User authentication, debate saving, export.

## 12. Acceptance criteria

1. Run `npm run dev` in `frontend/`. Page loads at `localhost:3000` in <2s.
2. Landing screen visible, futuristic dark aesthetic, futuristic fonts loaded.
3. Click START with default options → backend debate kicks off, Judge intro slide fades in.
4. Each new message produces a new slide that auto-scrolls into view smoothly.
5. Pro slides anchor left, Con slides anchor right, Judge slides anchor center.
6. Scroll wheel up = previous slides fade back in; down = next slides advance.
7. While debate is live, scrolling back shows `JUMP TO LIVE` badge; clicking it resumes auto-follow.
8. After verdict, the full timeline is scrubbable indefinitely.
9. Dot scrubber at bottom: hover shows tooltip, click jumps.
10. Resize browser at any width 320px–4K: layout remains coherent, text remains readable.
11. `prefers-reduced-motion: reduce`: all transitions collapse to instant or ~80ms.
12. Lighthouse Performance ≥85 on the deployed build.

## 13. Open risks (none blocking)

- **Lenis + Next.js 16 compatibility**: the template already uses Lenis 1.3 successfully, so this is proven.
- **Scroll-driven re-renders performance**: at 22 slides, each opacity transform is GPU-accelerated. No re-renders during scroll — Framer Motion uses imperative style updates. Tested pattern.
- **Long body text overflow on small phones**: max-width 65ch + viewport-fluid font-size + line-height 1.45 keeps lines short. Tested in CSS but should re-check on real device.

---

End of spec. After user approval, the next step is `superpowers:writing-plans` to generate a step-by-step implementation plan.
