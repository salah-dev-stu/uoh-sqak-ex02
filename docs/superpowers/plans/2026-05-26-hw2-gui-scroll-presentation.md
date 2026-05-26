# Phase 13g — Scroll-Driven Debate Presentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a single-page Next.js 16 frontend at `frontend/` that renders a live debate as a scroll-driven presentation (Pro left, Con right, Judge center, smooth crossfades, futuristic aesthetic), reading from the existing FastAPI SSE backend at `src/agent_debate/web/`.

**Architecture:** Sticky-viewport stage with scroll-driven opacity transitions (Framer Motion `useScroll` + `useTransform`), smoothed by Lenis. Module-level pub-sub state store fed by an `EventSource` connection. Pro/Con/Judge slides are visually distinct variants of a single `<Slide>` component. No multi-panel layout; one speaker at a time.

**Tech Stack:** Next.js 16.1.1, React 19, TypeScript 5, Tailwind v4, Framer Motion (`motion`), Lenis 1.3, `next/font/google` (Space Grotesk + Inter + JetBrains Mono), native `EventSource`, Vitest + Testing Library.

**Spec reference:** [`../specs/2026-05-26-hw2-gui-scroll-presentation.md`](../specs/2026-05-26-hw2-gui-scroll-presentation.md)
**PRD reference:** [`../../PRD_gui.md`](../../PRD_gui.md)

---

## File structure

```
frontend/
├── app/
│   ├── layout.tsx          # fonts, Lenis provider, base shell
│   ├── page.tsx            # presentation page; conditionally renders StartScreen or Stage
│   └── globals.css         # CSS custom properties + Tailwind v4 directives
├── components/
│   ├── start-screen.tsx    # landing form
│   ├── stage.tsx           # sticky viewport + scroll-driven slide list
│   ├── slide.tsx           # one slide (avatar + name + metadata + body)
│   ├── avatar.tsx          # 96px disc with letter/glyph and glow
│   ├── word-reveal.tsx     # word-by-word body text animation
│   ├── bottom-strip.tsx    # tally + dot scrubber + counter + live badge
│   ├── lenis-provider.tsx  # smooth scroll setup with React context
│   └── __tests__/
│       ├── avatar.test.tsx
│       ├── slide.test.tsx
│       └── bottom-strip.test.tsx
├── lib/
│   ├── state.ts            # module-level pub-sub store + React hook
│   ├── sse.ts              # EventSource wrapper with dedup + filter
│   ├── api.ts              # POST /api/debate/start, /stop
│   ├── types.ts            # Slide, SlideState, SSE payload types
│   ├── config.ts           # NEXT_PUBLIC_API_BASE, N_SLIDES_DEFAULT
│   └── __tests__/
│       ├── state.test.ts
│       ├── sse.test.ts
│       └── api.test.ts
├── public/
│   └── (favicon, og image — optional)
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
├── vitest.config.ts
├── .env.local              # NEXT_PUBLIC_API_BASE=http://localhost:8000
└── .gitignore              # node_modules, .next, .env.local
```

Backend (`src/agent_debate/web/`) is unchanged.

---

### Task 1: Scaffold Next.js 16 frontend

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/next.config.ts`
- Create: `frontend/tailwind.config.ts`
- Create: `frontend/postcss.config.mjs`
- Create: `frontend/.gitignore`
- Create: `frontend/.env.local`

- [ ] **Step 1: Initialize project from scratch in `frontend/`**

```bash
cd /Users/salah/Projects/orch-ai-agents/hw2
mkdir frontend && cd frontend
```

Write `package.json`:

```json
{
  "name": "hw2-debate-gui",
  "version": "1.00",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "test": "vitest run",
    "test:watch": "vitest"
  },
  "dependencies": {
    "next": "16.1.1",
    "react": "19.2.3",
    "react-dom": "19.2.3",
    "motion": "12.23.26",
    "lenis": "1.3.17",
    "clsx": "2.1.1",
    "tailwind-merge": "3.4.1"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "4.1.16",
    "@testing-library/jest-dom": "6.10.0",
    "@testing-library/react": "17.0.0",
    "@types/node": "24.10.0",
    "@types/react": "19.2.5",
    "@types/react-dom": "19.2.3",
    "@vitejs/plugin-react": "5.0.7",
    "jsdom": "27.0.1",
    "tailwindcss": "4.1.16",
    "typescript": "5.9.4",
    "vitest": "3.6.4"
  }
}
```

- [ ] **Step 2: Write TypeScript and Next.js configs**

`tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": false,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

`next.config.ts`:

```ts
import type { NextConfig } from "next";

const config: NextConfig = {
  experimental: { typedRoutes: true },
};

export default config;
```

`tailwind.config.ts`:

```ts
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
};

export default config;
```

`postcss.config.mjs`:

```js
export default { plugins: { "@tailwindcss/postcss": {} } };
```

`.gitignore`:

```
node_modules/
.next/
.env.local
*.log
.vitest-cache/
```

`.env.local`:

```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

- [ ] **Step 3: Install and verify**

```bash
cd /Users/salah/Projects/orch-ai-agents/hw2/frontend
npm install
```

Expected: clean install, no peer-dep warnings beyond informational.

- [ ] **Step 4: Commit**

```bash
cd /Users/salah/Projects/orch-ai-agents/hw2
git add frontend/package.json frontend/tsconfig.json frontend/next.config.ts \
  frontend/tailwind.config.ts frontend/postcss.config.mjs frontend/.gitignore \
  frontend/.env.local
git commit -m "feat(13g): scaffold Next.js 16 frontend for scroll-driven presentation

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 2: Global styles, fonts, and design tokens

**Files:**
- Create: `frontend/app/globals.css`
- Create: `frontend/app/layout.tsx`

- [ ] **Step 1: Write globals.css with all color/typography tokens**

```css
@import "tailwindcss";

@theme {
  --color-bg-base: #07070a;
  --color-fg-primary: #f0f0f5;
  --color-fg-muted: rgb(240 240 245 / 0.45);
  --color-fg-dim: rgb(240 240 245 / 0.18);
  --color-pro-accent: #ff3da8;
  --color-pro-glow: rgb(255 61 168 / 0.35);
  --color-con-accent: #3da8ff;
  --color-con-glow: rgb(61 168 255 / 0.35);
  --color-judge-accent: #ffc94c;
  --color-judge-glow: rgb(255 201 76 / 0.30);
  --font-display: var(--font-space-grotesk);
  --font-body: var(--font-inter);
  --font-mono: var(--font-jetbrains-mono);
}

@layer base {
  html, body { background: var(--color-bg-base); color: var(--color-fg-primary); }
  body {
    background-image: radial-gradient(ellipse at center, #0f0f18 0%, #07070a 70%);
    min-height: 100vh;
    font-family: var(--font-body);
    -webkit-font-smoothing: antialiased;
    overflow-x: hidden;
  }
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.08s !important;
    transition-duration: 0.08s !important;
  }
}
```

- [ ] **Step 2: Write layout.tsx with font loading and base shell**

```tsx
import type { Metadata } from "next";
import { Space_Grotesk, Inter, JetBrains_Mono } from "next/font/google";
import { LenisProvider } from "@/components/lenis-provider";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  subsets: ["latin"], variable: "--font-space-grotesk", weight: ["400", "500", "600"],
});
const inter = Inter({
  subsets: ["latin"], variable: "--font-inter", weight: ["300", "400", "500"],
});
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"], variable: "--font-jetbrains-mono", weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Agent Debate · HW2",
  description: "Live scroll-driven debate between Pro and Con, moderated by a Judge.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${spaceGrotesk.variable} ${inter.variable} ${jetbrainsMono.variable}`}>
      <body><LenisProvider>{children}</LenisProvider></body>
    </html>
  );
}
```

- [ ] **Step 3: Commit**

```bash
git add frontend/app/globals.css frontend/app/layout.tsx
git commit -m "feat(13g): global styles + font loading + reduced-motion baseline

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 3: TypeScript types

**Files:**
- Create: `frontend/lib/types.ts`
- Create: `frontend/lib/config.ts`

- [ ] **Step 1: Write `lib/types.ts`**

```ts
export type Speaker = "pro" | "con" | "judge";
export type SlideVariant = "intro" | "argument" | "counter" | "rebuttal" | "verdict";
export type Outcome = "pro_wins" | "con_wins" | "debate_aborted" | "budget_exhausted";

export interface Slide {
  id: string;
  speaker: Speaker;
  variant: SlideVariant;
  pingIndex: number;
  text: string;
  timestamp: string;
  proScore?: number;
  conScore?: number;
  outcome?: Outcome;
}

export interface SlideState {
  slides: Slide[];
  currentIndex: number;
  followLive: boolean;
  status: "idle" | "live" | "done" | "error";
  proTotal: number;
  conTotal: number;
  pingCounter: { current: number; total: number };
  error?: string;
}

export interface DebateMessage {
  msg_id: string;
  from: Speaker | "main";
  to: Speaker | "main";
  role: string;
  ping_index: number;
  text: string;
  timestamp: string;
  tokens_in?: number;
  tokens_out?: number;
}

export interface Verdict {
  pro_total: number;
  con_total: number;
  outcome: Outcome;
  rationale?: string;
}

export interface SseEvent {
  type:
    | "started" | "message" | "before_round" | "after_round"
    | "verdict" | "after_verdict" | "done" | "error" | "stop_requested";
  payload: unknown;
}

export interface StartDebateResponse { debate_id: string; }
```

- [ ] **Step 2: Write `lib/config.ts`**

```ts
export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
export const DEFAULT_N_PINGS = 10;
export const SCROLL_FOLLOW_DURATION = 0.7;
export const SLIDE_CROSSFADE_MS = 700;
export const WORD_STAGGER_MS = 25;
export const WORD_FADE_MS = 220;
```

- [ ] **Step 3: Commit**

```bash
git add frontend/lib/types.ts frontend/lib/config.ts
git commit -m "feat(13g): TypeScript types + tunable config constants

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 4: Module-level state store

**Files:**
- Create: `frontend/lib/state.ts`
- Create: `frontend/lib/__tests__/state.test.ts`
- Create: `frontend/vitest.config.ts`

- [ ] **Step 1: Write vitest.config.ts**

```ts
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    globals: true,
    coverage: { provider: "v8", thresholds: { lines: 85 } },
  },
  resolve: { alias: { "@": "/Users/salah/Projects/orch-ai-agents/hw2/frontend" } },
});
```

- [ ] **Step 2: Write the failing test**

`frontend/lib/__tests__/state.test.ts`:

```ts
import { describe, it, expect, beforeEach } from "vitest";
import { getState, setState, subscribe, appendSlide, resetState } from "@/lib/state";

describe("state store", () => {
  beforeEach(() => resetState());

  it("starts with empty slides and idle status", () => {
    const s = getState();
    expect(s.slides).toEqual([]);
    expect(s.status).toBe("idle");
    expect(s.followLive).toBe(true);
  });

  it("appendSlide adds a slide and notifies subscribers", () => {
    let notified = 0;
    subscribe(() => notified++);
    appendSlide({
      id: "m1", speaker: "pro", variant: "argument", pingIndex: 1,
      text: "Hello world", timestamp: "2026-05-26T12:00:00Z",
    });
    expect(getState().slides).toHaveLength(1);
    expect(notified).toBe(1);
  });

  it("setState merges partial updates", () => {
    setState({ status: "live", proTotal: 5 });
    expect(getState().status).toBe("live");
    expect(getState().proTotal).toBe(5);
  });
});
```

- [ ] **Step 3: Verify the test fails**

```bash
cd frontend && npx vitest run lib/__tests__/state.test.ts
```

Expected: FAIL with "Cannot find module".

- [ ] **Step 4: Implement `lib/state.ts`**

```ts
import type { Slide, SlideState } from "./types";

const initial: SlideState = {
  slides: [],
  currentIndex: 0,
  followLive: true,
  status: "idle",
  proTotal: 0,
  conTotal: 0,
  pingCounter: { current: 0, total: 22 },
};

let state: SlideState = { ...initial };
const listeners = new Set<() => void>();

export function getState(): SlideState { return state; }

export function setState(patch: Partial<SlideState>): void {
  state = { ...state, ...patch };
  listeners.forEach((l) => l());
}

export function appendSlide(slide: Slide): void {
  state = { ...state, slides: [...state.slides, slide] };
  listeners.forEach((l) => l());
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function resetState(): void {
  state = { ...initial };
  listeners.forEach((l) => l());
}
```

- [ ] **Step 5: Verify the test passes**

```bash
npx vitest run lib/__tests__/state.test.ts
```

Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
cd /Users/salah/Projects/orch-ai-agents/hw2
git add frontend/lib/state.ts frontend/lib/__tests__/state.test.ts frontend/vitest.config.ts
git commit -m "feat(13g): module-level state store + first Vitest suite

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 5: API client and SSE consumer

**Files:**
- Create: `frontend/lib/api.ts`
- Create: `frontend/lib/sse.ts`
- Create: `frontend/lib/__tests__/sse.test.ts`

- [ ] **Step 1: Write `lib/api.ts`**

```ts
import { API_BASE } from "./config";
import type { StartDebateResponse } from "./types";

export async function startDebate(opts: { nPings: number; live: boolean }): Promise<StartDebateResponse> {
  const url = `${API_BASE}/api/debate/start?live=${opts.live ? 1 : 0}&n_pings=${opts.nPings}`;
  const r = await fetch(url, { method: "POST" });
  if (!r.ok) throw new Error(`startDebate failed: ${r.status}`);
  return r.json();
}

export async function stopDebate(id: string): Promise<void> {
  await fetch(`${API_BASE}/api/debate/${id}/stop`, { method: "POST" });
}

export function streamUrl(id: string): string {
  return `${API_BASE}/api/debate/${id}/stream`;
}
```

- [ ] **Step 2: Write the failing dedup test**

`frontend/lib/__tests__/sse.test.ts`:

```ts
import { describe, it, expect } from "vitest";
import { shouldSkip } from "@/lib/sse";

describe("SSE dedup logic", () => {
  it("skips messages with no msg_id (boot directive)", () => {
    expect(shouldSkip({ phase: "boot", directive: "setup" }, new Set())).toBe(true);
  });

  it("skips duplicate msg_ids", () => {
    const seen = new Set(["m1"]);
    expect(shouldSkip({ msg_id: "m1", from: "judge", to: "pro" }, seen)).toBe(true);
  });

  it("skips forwarded pro/con messages routed to opponent", () => {
    expect(shouldSkip({ msg_id: "m1", from: "pro", to: "con" }, new Set())).toBe(true);
    expect(shouldSkip({ msg_id: "m2", from: "con", to: "pro" }, new Set())).toBe(true);
  });

  it("keeps judge-originated and judge-targeted messages", () => {
    expect(shouldSkip({ msg_id: "m3", from: "pro", to: "judge" }, new Set())).toBe(false);
    expect(shouldSkip({ msg_id: "m4", from: "judge", to: "pro" }, new Set())).toBe(false);
  });
});
```

- [ ] **Step 3: Verify the test fails**

```bash
npx vitest run lib/__tests__/sse.test.ts
```

Expected: FAIL with "Cannot find module".

- [ ] **Step 4: Implement `lib/sse.ts`**

```ts
import type { SseEvent, DebateMessage } from "./types";
import { appendSlide, setState, getState } from "./state";
import { streamUrl } from "./api";

export function shouldSkip(payload: unknown, seen: Set<string>): boolean {
  if (!payload || typeof payload !== "object") return true;
  const p = payload as Record<string, unknown>;
  if (typeof p.msg_id !== "string") return true;
  if (seen.has(p.msg_id)) return true;
  if ((p.from === "pro" || p.from === "con") && p.to !== "judge") return true;
  return false;
}

export function openStream(debateId: string): () => void {
  const es = new EventSource(streamUrl(debateId));
  const seen = new Set<string>();
  setState({ status: "live" });

  es.onmessage = (e) => {
    const evt: SseEvent = JSON.parse(e.data);
    handleEvent(evt, seen);
  };
  es.onerror = () => setState({ status: "error", error: "SSE connection lost" });

  return () => es.close();
}

function handleEvent(evt: SseEvent, seen: Set<string>): void {
  switch (evt.type) {
    case "message": {
      if (shouldSkip(evt.payload, seen)) return;
      const m = evt.payload as DebateMessage;
      seen.add(m.msg_id);
      appendSlide({
        id: m.msg_id, speaker: m.from === "main" ? "judge" : m.from,
        variant: variantFromRole(m.role), pingIndex: m.ping_index,
        text: m.text, timestamp: m.timestamp,
      });
      break;
    }
    case "after_round": {
      const p = evt.payload as { pro_total: number; con_total: number };
      setState({ proTotal: p.pro_total, conTotal: p.con_total });
      break;
    }
    case "verdict": {
      const p = evt.payload as { verdict: { pro_total: number; con_total: number; outcome: string } };
      const v = p.verdict;
      appendSlide({
        id: "verdict", speaker: "judge", variant: "verdict",
        pingIndex: getState().slides.length, text: "", timestamp: new Date().toISOString(),
        proScore: v.pro_total, conScore: v.con_total, outcome: v.outcome as never,
      });
      break;
    }
    case "done": setState({ status: "done" }); break;
    case "error": setState({ status: "error", error: String(evt.payload) }); break;
  }
}

function variantFromRole(role: string): "intro" | "argument" | "counter" | "rebuttal" {
  if (role === "setup_directive" || role === "intro") return "intro";
  if (role === "counter") return "counter";
  if (role === "rebuttal") return "rebuttal";
  return "argument";
}
```

- [ ] **Step 5: Verify the test passes**

```bash
npx vitest run lib/__tests__/sse.test.ts
```

Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add frontend/lib/api.ts frontend/lib/sse.ts frontend/lib/__tests__/sse.test.ts
git commit -m "feat(13g): API client + SSE consumer with dedup + tests

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 6: LenisProvider

**Files:**
- Create: `frontend/components/lenis-provider.tsx`

- [ ] **Step 1: Write LenisProvider**

```tsx
"use client";
import { createContext, useContext, useEffect, useRef, useState } from "react";
import Lenis from "lenis";

const LenisContext = createContext<Lenis | null>(null);

export function useLenis(): Lenis | null { return useContext(LenisContext); }

export function LenisProvider({ children }: { children: React.ReactNode }): JSX.Element {
  const lenisRef = useRef<Lenis | null>(null);
  const [, force] = useState(0);

  useEffect(() => {
    const lenis = new Lenis({ duration: 1.1, smoothWheel: true });
    lenisRef.current = lenis;
    force((n) => n + 1);

    let raf = 0;
    const loop = (t: number) => { lenis.raf(t); raf = requestAnimationFrame(loop); };
    raf = requestAnimationFrame(loop);

    return () => { cancelAnimationFrame(raf); lenis.destroy(); lenisRef.current = null; };
  }, []);

  return <LenisContext.Provider value={lenisRef.current}>{children}</LenisContext.Provider>;
}
```

- [ ] **Step 2: Verify lint clean**

```bash
cd frontend && npx tsc --noEmit
```

Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add frontend/components/lenis-provider.tsx
git commit -m "feat(13g): Lenis smooth-scroll provider with React context

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 7: Avatar component

**Files:**
- Create: `frontend/components/avatar.tsx`
- Create: `frontend/components/__tests__/avatar.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Avatar } from "@/components/avatar";

describe("Avatar", () => {
  it("renders P glyph for Pro speaker", () => {
    render(<Avatar speaker="pro" pulse={false} />);
    expect(screen.getByText("P")).toBeInTheDocument();
  });

  it("renders C glyph for Con speaker", () => {
    render(<Avatar speaker="con" pulse={false} />);
    expect(screen.getByText("C")).toBeInTheDocument();
  });

  it("renders ⚖ glyph for Judge speaker", () => {
    render(<Avatar speaker="judge" pulse={false} />);
    expect(screen.getByText("⚖")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Verify the test fails**

Expected: "Cannot find module @/components/avatar".

- [ ] **Step 3: Implement avatar.tsx**

```tsx
"use client";
import { motion } from "motion/react";
import type { Speaker } from "@/lib/types";

const GLYPHS: Record<Speaker, string> = { pro: "P", con: "C", judge: "⚖" };
const COLORS: Record<Speaker, { fg: string; bg: string; glow: string }> = {
  pro:   { fg: "var(--color-pro-accent)",   bg: "rgb(255 61 168 / 0.12)",  glow: "var(--color-pro-glow)" },
  con:   { fg: "var(--color-con-accent)",   bg: "rgb(61 168 255 / 0.12)",  glow: "var(--color-con-glow)" },
  judge: { fg: "var(--color-judge-accent)", bg: "rgb(255 201 76 / 0.12)",  glow: "var(--color-judge-glow)" },
};

interface Props { speaker: Speaker; pulse: boolean; }

export function Avatar({ speaker, pulse }: Props): JSX.Element {
  const c = COLORS[speaker];
  return (
    <motion.div
      initial={{ scale: 0.92, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", damping: 18, stiffness: 220 }}
      style={{
        width: 96, height: 96, borderRadius: "50%",
        background: c.bg, border: `1px solid ${c.fg}`,
        boxShadow: `0 0 24px ${c.glow}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        color: c.fg, fontFamily: "var(--font-display)",
        fontSize: "2rem", fontWeight: 500,
      }}
      animate-pulse={pulse ? "" : undefined}
    >
      {pulse ? (
        <motion.span animate={{ opacity: [1, 0.6, 1] }} transition={{ duration: 1.5, repeat: Infinity }}>
          {GLYPHS[speaker]}
        </motion.span>
      ) : (
        <span>{GLYPHS[speaker]}</span>
      )}
    </motion.div>
  );
}
```

- [ ] **Step 4: Verify the test passes**

```bash
npx vitest run components/__tests__/avatar.test.tsx
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/components/avatar.tsx frontend/components/__tests__/avatar.test.tsx
git commit -m "feat(13g): Avatar component with per-speaker color + glow + pulse

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 8: WordReveal component

**Files:**
- Create: `frontend/components/word-reveal.tsx`

- [ ] **Step 1: Implement word-reveal.tsx**

```tsx
"use client";
import { motion } from "motion/react";
import { WORD_STAGGER_MS, WORD_FADE_MS } from "@/lib/config";

interface Props { text: string; trigger: boolean; }

export function WordReveal({ text, trigger }: Props): JSX.Element {
  const words = text.split(/(\s+)/);
  return (
    <p style={{
      fontFamily: "var(--font-body)", fontSize: "clamp(1.125rem, 1.5vw + 0.5rem, 2rem)",
      lineHeight: 1.45, maxWidth: "65ch", fontWeight: 300,
    }}>
      {words.map((w, i) => (
        <motion.span key={i} initial={{ opacity: 0 }}
          animate={trigger ? { opacity: 1 } : { opacity: 0 }}
          transition={{ duration: WORD_FADE_MS / 1000, delay: (i * WORD_STAGGER_MS) / 1000, ease: "easeOut" }}
        >{w}</motion.span>
      ))}
    </p>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/word-reveal.tsx
git commit -m "feat(13g): WordReveal — per-word fade with config-driven stagger

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 9: Slide component

**Files:**
- Create: `frontend/components/slide.tsx`
- Create: `frontend/components/__tests__/slide.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { Slide } from "@/components/slide";
import type { Slide as SlideT } from "@/lib/types";

const baseSlide = (overrides: Partial<SlideT> = {}): SlideT => ({
  id: "m1", speaker: "pro", variant: "argument", pingIndex: 1,
  text: "Hello", timestamp: "2026-05-26T12:00:00Z", ...overrides,
});

describe("Slide", () => {
  it("renders Pro slide with left anchor class", () => {
    const { container } = render(<Slide slide={baseSlide()} index={0} isLatest={false} />);
    expect(container.querySelector('[data-anchor="left"]')).not.toBeNull();
  });

  it("renders Con slide with right anchor class", () => {
    const { container } = render(<Slide slide={baseSlide({ speaker: "con" })} index={0} isLatest={false} />);
    expect(container.querySelector('[data-anchor="right"]')).not.toBeNull();
  });

  it("renders Judge slide with center anchor class", () => {
    const { container } = render(<Slide slide={baseSlide({ speaker: "judge" })} index={0} isLatest={false} />);
    expect(container.querySelector('[data-anchor="center"]')).not.toBeNull();
  });

  it("renders verdict tally for verdict variant", () => {
    render(<Slide slide={baseSlide({
      speaker: "judge", variant: "verdict", proScore: 67, conScore: 73, outcome: "con_wins",
    })} index={0} isLatest={false} />);
    expect(screen.getByText("67")).toBeInTheDocument();
    expect(screen.getByText("73")).toBeInTheDocument();
    expect(screen.getByText(/CON WINS/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Implement slide.tsx**

```tsx
"use client";
import { Avatar } from "./avatar";
import { WordReveal } from "./word-reveal";
import type { Slide as SlideT, Speaker } from "@/lib/types";

const ANCHOR: Record<Speaker, "left" | "right" | "center"> = {
  pro: "left", con: "right", judge: "center",
};

const NAME: Record<Speaker, string> = { pro: "PRO", con: "CON", judge: "JUDGE" };

interface Props { slide: SlideT; index: number; isLatest: boolean; }

export function Slide({ slide, isLatest }: Props): JSX.Element {
  const anchor = ANCHOR[slide.speaker];
  const justify = anchor === "left" ? "flex-start" : anchor === "right" ? "flex-end" : "center";
  const align = anchor === "left" ? "items-start" : anchor === "right" ? "items-end" : "items-center";
  const textAlign = anchor === "right" ? "right" : "left";

  return (
    <div data-anchor={anchor} style={{
      width: "100%", height: "100vh", display: "flex",
      justifyContent: justify, alignItems: "center", padding: "5vh 6vw",
    }}>
      <div className={`flex flex-col gap-6 ${align}`} style={{ maxWidth: "60ch", textAlign }}>
        <Avatar speaker={slide.speaker} pulse={isLatest} />
        <div style={{
          fontFamily: "var(--font-display)", fontSize: "clamp(1.5rem, 2vw + 0.5rem, 2.5rem)",
          letterSpacing: "0.08em", fontWeight: 500,
          color: `var(--color-${slide.speaker}-accent)`,
        }}>{NAME[slide.speaker]}</div>
        <div style={{
          fontFamily: "var(--font-mono)", fontSize: "0.7rem", letterSpacing: "0.05em",
          color: "var(--color-fg-muted)", textTransform: "uppercase",
        }}>{slide.variant} · ping {slide.pingIndex} · {new Date(slide.timestamp).toLocaleTimeString()}</div>
        {slide.variant === "verdict" ? (
          <div className="flex flex-col gap-4">
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "1.5rem" }}>
              <span style={{ color: "var(--color-pro-accent)" }}>{slide.proScore}</span>
              {" · "}
              <span style={{ color: "var(--color-con-accent)" }}>{slide.conScore}</span>
            </div>
            <div style={{
              fontFamily: "var(--font-display)", fontSize: "2rem", letterSpacing: "0.08em",
              color: "var(--color-fg-primary)",
            }}>{(slide.outcome ?? "").replace(/_/g, " ").toUpperCase()}</div>
          </div>
        ) : (
          <WordReveal text={slide.text} trigger={isLatest || slide.text.length > 0} />
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Verify tests pass**

```bash
npx vitest run components/__tests__/slide.test.tsx
```

Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/components/slide.tsx frontend/components/__tests__/slide.test.tsx
git commit -m "feat(13g): Slide component with left/right/center anchoring + verdict variant

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 10: Stage component (scroll-driven container)

**Files:**
- Create: `frontend/components/stage.tsx`

- [ ] **Step 1: Implement stage.tsx**

```tsx
"use client";
import { useEffect, useSyncExternalStore } from "react";
import { motion, useScroll, useTransform } from "motion/react";
import { Slide } from "./slide";
import { getState, subscribe, setState } from "@/lib/state";
import { useLenis } from "./lenis-provider";

function useStoreState() {
  return useSyncExternalStore(subscribe, getState, getState);
}

export function Stage(): JSX.Element {
  const state = useStoreState();
  const lenis = useLenis();
  const { scrollYProgress } = useScroll();
  const slidesCount = state.slides.length;

  useEffect(() => {
    if (slidesCount === 0 || !state.followLive || !lenis) return;
    const target = (slidesCount - 1) * window.innerHeight;
    lenis.scrollTo(target, { duration: 0.7 });
  }, [slidesCount, state.followLive, lenis]);

  useEffect(() => {
    if (!lenis) return;
    let lastY = 0;
    const onScroll = ({ scroll }: { scroll: number }) => {
      const userScrolledUp = scroll < lastY - 4;
      lastY = scroll;
      const idx = Math.round(scroll / window.innerHeight);
      const latest = state.slides.length - 1;
      if (userScrolledUp && idx < latest && state.followLive) setState({ followLive: false });
      if (state.currentIndex !== idx) setState({ currentIndex: idx });
    };
    lenis.on("scroll", onScroll);
    return () => lenis.off("scroll", onScroll);
  }, [lenis, state.followLive, state.currentIndex, state.slides.length]);

  if (slidesCount === 0) return <></>;

  return (
    <div style={{ height: `${slidesCount * 100}vh`, position: "relative" }}>
      <div style={{ position: "sticky", top: 0, height: "100vh", overflow: "hidden" }}>
        {state.slides.map((s, i) => {
          const startProgress = i / slidesCount;
          const endProgress = (i + 1) / slidesCount;
          const opacity = useTransform(scrollYProgress, [
            startProgress, startProgress + 0.3 / slidesCount,
            endProgress - 0.3 / slidesCount, endProgress,
          ], [0, 1, 1, 0]);
          const y = useTransform(scrollYProgress, [
            startProgress, startProgress + 0.3 / slidesCount,
            endProgress - 0.3 / slidesCount, endProgress,
          ], [24, 0, 0, -24]);
          return (
            <motion.div key={s.id} style={{
              position: "absolute", inset: 0, opacity, y,
            }}>
              <Slide slide={s} index={i} isLatest={i === slidesCount - 1} />
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/stage.tsx
git commit -m "feat(13g): Stage container — sticky viewport + scroll-driven crossfades + auto-follow

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 11: StartScreen component

**Files:**
- Create: `frontend/components/start-screen.tsx`

- [ ] **Step 1: Implement start-screen.tsx**

```tsx
"use client";
import { useState } from "react";
import { motion } from "motion/react";
import { startDebate } from "@/lib/api";
import { openStream } from "@/lib/sse";
import { setState } from "@/lib/state";
import { DEFAULT_N_PINGS } from "@/lib/config";

export function StartScreen(): JSX.Element {
  const [topic, setTopic] = useState("Can AI agents create truly original work, or is everything just recombination?");
  const [nPings, setNPings] = useState(DEFAULT_N_PINGS);
  const [live, setLive] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onStart(): Promise<void> {
    setBusy(true); setError(null);
    try {
      const r = await startDebate({ nPings, live });
      openStream(r.debate_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start");
      setState({ status: "error" }); setBusy(false);
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}
      style={{
        minHeight: "100vh", display: "flex", flexDirection: "column",
        justifyContent: "center", alignItems: "center", padding: "5vh 6vw", gap: "3rem",
      }}>
      <h1 style={{
        fontFamily: "var(--font-display)", fontSize: "clamp(2rem, 5vw, 4rem)",
        letterSpacing: "0.1em", fontWeight: 500,
      }}>AGENT DEBATE</h1>
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", width: "min(560px, 90vw)" }}>
        <label style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--color-fg-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Topic
          <textarea value={topic} onChange={(e) => setTopic(e.target.value)} rows={2}
            style={{ display: "block", marginTop: 8, width: "100%", padding: "0.75rem",
              background: "transparent", border: "1px solid var(--color-fg-dim)",
              color: "var(--color-fg-primary)", fontFamily: "var(--font-body)", fontSize: "1rem", borderRadius: 4 }} />
        </label>
        <label style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--color-fg-muted)", textTransform: "uppercase" }}>
          Pings per side
          <input type="number" min={1} max={20} value={nPings} onChange={(e) => setNPings(Number(e.target.value))}
            style={{ display: "block", marginTop: 8, padding: "0.5rem 0.75rem",
              background: "transparent", border: "1px solid var(--color-fg-dim)",
              color: "var(--color-fg-primary)", fontFamily: "var(--font-mono)", borderRadius: 4, width: 80 }} />
        </label>
        <label style={{ display: "flex", gap: "0.5rem", alignItems: "center", fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--color-fg-primary)" }}>
          <input type="checkbox" checked={live} onChange={(e) => setLive(e.target.checked)} />
          <span>Live (real Claude — ~8 min)</span>
        </label>
        <button onClick={onStart} disabled={busy} style={{
          marginTop: "1rem", padding: "1rem 2rem", background: "var(--color-judge-accent)",
          color: "var(--color-bg-base)", border: "none", borderRadius: 4,
          fontFamily: "var(--font-display)", letterSpacing: "0.1em", fontWeight: 600,
          fontSize: "1rem", cursor: busy ? "wait" : "pointer", textTransform: "uppercase",
        }}>{busy ? "Starting…" : "▶ Start debate"}</button>
        {error && <p style={{ color: "var(--color-pro-accent)", fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{error}</p>}
      </div>
    </motion.div>
  );
}
```

- [ ] **Step 2: Commit**

```bash
git add frontend/components/start-screen.tsx
git commit -m "feat(13g): StartScreen landing with topic + pings + live toggle

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 12: BottomStrip (tally + dot scrubber + counter + live badge)

**Files:**
- Create: `frontend/components/bottom-strip.tsx`
- Create: `frontend/components/__tests__/bottom-strip.test.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
import { render, screen } from "@testing-library/react";
import { describe, it, expect, beforeEach } from "vitest";
import { BottomStrip } from "@/components/bottom-strip";
import { setState, resetState, appendSlide } from "@/lib/state";

describe("BottomStrip", () => {
  beforeEach(() => resetState());

  it("shows running tally", () => {
    setState({ proTotal: 12, conTotal: 8, status: "live" });
    appendSlide({ id: "m1", speaker: "pro", variant: "argument", pingIndex: 1, text: "x", timestamp: "" });
    render(<BottomStrip />);
    expect(screen.getByText(/Pro 12/)).toBeInTheDocument();
    expect(screen.getByText(/Con 8/)).toBeInTheDocument();
  });

  it("renders LIVE badge when status is live and followLive", () => {
    setState({ status: "live", followLive: true });
    appendSlide({ id: "m1", speaker: "pro", variant: "argument", pingIndex: 1, text: "x", timestamp: "" });
    render(<BottomStrip />);
    expect(screen.getByText(/LIVE/i)).toBeInTheDocument();
  });

  it("renders JUMP TO LIVE when scrolled away from latest", () => {
    setState({ status: "live", followLive: false });
    appendSlide({ id: "m1", speaker: "pro", variant: "argument", pingIndex: 1, text: "x", timestamp: "" });
    render(<BottomStrip />);
    expect(screen.getByText(/JUMP TO LIVE/i)).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Implement bottom-strip.tsx**

```tsx
"use client";
import { useSyncExternalStore } from "react";
import { getState, subscribe, setState } from "@/lib/state";
import { useLenis } from "./lenis-provider";

function useStoreState() { return useSyncExternalStore(subscribe, getState, getState); }

export function BottomStrip(): JSX.Element {
  const s = useStoreState();
  const lenis = useLenis();
  if (s.slides.length === 0) return <></>;

  function jumpToLive(): void {
    if (!lenis) return;
    lenis.scrollTo((s.slides.length - 1) * window.innerHeight, { duration: 0.6 });
    setState({ followLive: true });
  }
  function jumpTo(i: number): void {
    if (!lenis) return;
    lenis.scrollTo(i * window.innerHeight, { duration: 0.6 });
    setState({ followLive: false });
  }

  return (
    <div style={{
      position: "fixed", bottom: 0, left: 0, right: 0, padding: "1rem 1.5rem",
      display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem",
      fontFamily: "var(--font-mono)", fontSize: "0.7rem", letterSpacing: "0.05em",
      color: "var(--color-fg-muted)", background: "linear-gradient(to top, rgb(7 7 10 / 0.95), transparent)",
      pointerEvents: "auto", zIndex: 50,
    }}>
      <div>
        <span style={{ color: "var(--color-pro-accent)" }}>Pro {s.proTotal}</span>
        {" · "}
        <span style={{ color: "var(--color-con-accent)" }}>Con {s.conTotal}</span>
      </div>
      <div style={{ display: "flex", gap: 4 }}>
        {s.slides.map((slide, i) => {
          const color = `var(--color-${slide.speaker}-accent)`;
          const active = i === s.currentIndex;
          return (
            <button key={slide.id} onClick={() => jumpTo(i)} title={`${slide.speaker} · ${slide.variant} · ping ${slide.pingIndex}`}
              style={{
                width: active ? 12 : 8, height: active ? 12 : 8, borderRadius: "50%",
                background: color, border: "none", padding: 0, cursor: "pointer",
                opacity: active ? 1 : 0.55, transition: "all 0.2s",
              }} />
          );
        })}
      </div>
      <div style={{ display: "flex", gap: "1rem", alignItems: "center" }}>
        <span>ping {s.currentIndex + 1}/{s.slides.length}</span>
        {s.status === "live" && (
          s.followLive ? (
            <span style={{ color: "var(--color-pro-accent)" }}>◉ LIVE</span>
          ) : (
            <button onClick={jumpToLive} style={{
              background: "transparent", border: "1px solid var(--color-pro-accent)",
              color: "var(--color-pro-accent)", padding: "0.25rem 0.5rem", borderRadius: 4,
              fontFamily: "var(--font-mono)", fontSize: "0.7rem", cursor: "pointer",
              letterSpacing: "0.05em", textTransform: "uppercase",
            }}>◉ Jump to live</button>
          )
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 3: Verify tests pass**

```bash
npx vitest run components/__tests__/bottom-strip.test.tsx
```

Expected: 3 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/components/bottom-strip.tsx frontend/components/__tests__/bottom-strip.test.tsx
git commit -m "feat(13g): BottomStrip — tally + dot scrubber + JUMP TO LIVE badge

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 13: Main page composition

**Files:**
- Create: `frontend/app/page.tsx`

- [ ] **Step 1: Implement page.tsx**

```tsx
"use client";
import { useSyncExternalStore } from "react";
import { StartScreen } from "@/components/start-screen";
import { Stage } from "@/components/stage";
import { BottomStrip } from "@/components/bottom-strip";
import { getState, subscribe } from "@/lib/state";

function useStoreState() { return useSyncExternalStore(subscribe, getState, getState); }

export default function Page(): JSX.Element {
  const s = useStoreState();
  return (
    <main style={{ position: "relative" }}>
      {s.status === "idle" ? <StartScreen /> : <Stage />}
      {s.slides.length > 0 && <BottomStrip />}
    </main>
  );
}
```

- [ ] **Step 2: Build and run dev server**

```bash
cd frontend && npm run build
```

Expected: build succeeds with no TS errors.

```bash
npm run dev
```

Expected: Ready in ~1s. Open `http://localhost:3000` — landing screen visible.

- [ ] **Step 3: Commit**

```bash
git add frontend/app/page.tsx
git commit -m "feat(13g): main presentation page composition (StartScreen | Stage + BottomStrip)

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 14: End-to-end visual verification (mock LLM)

**Files:**
- Create: `assets/13g-empty.png`
- Create: `assets/13g-pro-turn.png`
- Create: `assets/13g-con-turn.png`
- Create: `assets/13g-verdict.png`

- [ ] **Step 1: Start backend and frontend**

```bash
# Terminal 1
cd /Users/salah/Projects/orch-ai-agents/hw2 && uv run agent-debate-web
# Terminal 2
cd /Users/salah/Projects/orch-ai-agents/hw2/frontend && npm run dev
```

- [ ] **Step 2: Drive the UI via Playwright MCP and capture screenshots**

Use the `mcp__playwright-orch__browser_*` tools to:
1. Navigate to `http://localhost:3000`.
2. Take screenshot → save to `assets/13g-empty.png`.
3. Click START.
4. Wait until first Pro slide visible (`browser_wait_for` text "PRO" with isLatest).
5. Screenshot → `assets/13g-pro-turn.png`.
6. Wait until next Con slide visible.
7. Screenshot → `assets/13g-con-turn.png`.
8. Wait until verdict slide visible.
9. Screenshot → `assets/13g-verdict.png`.

- [ ] **Step 3: Verify screenshots manually for**
- Dark futuristic aesthetic
- Pro slides anchored left, Con anchored right, Judge centered
- Smooth crossfades between slides
- Bottom strip with dots, tally, LIVE badge

- [ ] **Step 4: Commit**

```bash
git add assets/13g-*.png
git commit -m "test(13g): visual verification screenshots — empty, pro, con, verdict

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

### Task 15: Backend regression + closure docs

- [ ] **Step 1: Run full Python regression**

```bash
cd /Users/salah/Projects/orch-ai-agents/hw2 && uv run pytest
```

Expected: 164 tests pass, no regressions.

- [ ] **Step 2: Run full frontend test suite**

```bash
cd /Users/salah/Projects/orch-ai-agents/hw2/frontend && npx vitest run --coverage
```

Expected: all tests pass, line coverage ≥ 85%.

- [ ] **Step 3: Update README with Web GUI section**

Edit `/Users/salah/Projects/orch-ai-agents/hw2/README.md` and add a "Web GUI" section pointing at `cd frontend && npm run dev`, with embedded screenshots from `assets/13g-*.png`.

- [ ] **Step 4: Append Phase 13g block to `docs/PROMPTS.md`** with the brainstorm dialogue + spec + plan references.

- [ ] **Step 5: Final commit**

```bash
git add README.md docs/PROMPTS.md
git commit -m "docs(13g): README Web GUI section + PROMPTS Phase 13g brainstorm record

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

---

## Self-review checklist

After plan written, verify:

- ✅ Spec coverage: every acceptance criterion in `PRD_gui.md` §8 maps to a task above (1–14 covered; 15 is closure).
- ✅ No placeholders (TBD/TODO/etc.) — all code shown inline.
- ✅ Type consistency — `Slide`, `Speaker`, `SlideVariant` used identically across all tasks.
- ✅ File paths absolute or relative-to-frontend, consistent.
- ✅ Each task has a single concrete commit.

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-26-hw2-gui-scroll-presentation.md`. Two execution options:

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks, fast iteration
2. **Inline Execution** — tasks executed in this session with checkpoints

Which approach?
