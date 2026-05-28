"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { Html } from "@react-three/drei";
import { motion, AnimatePresence } from "motion/react";
import { getState, subscribe } from "@/lib/state";
import type { Slide } from "@/lib/types";

// SpeechBubble is for Pro and Con only — Judge text goes through the
// bottom-screen JudgeChyron component. Anchor X values are pushed
// outward from each podium's X (±3) so the bubble sits well off to
// the side rather than crowding the centre stage. The tail bridges
// the gap back to the speaker.
type SideSpeaker = "pro" | "con";

const POSITION: Record<SideSpeaker, [number, number, number]> = {
  pro: [-3.8, 3.4, 0.2],
  con: [ 3.8, 3.4, 0.2],
};

const BUBBLE_TRANSFORM: Record<SideSpeaker, string> = {
  pro: "translate(-100%, 0)",  // right edge of bubble at anchor → extends LEFT
  con: "translate(0, 0)",      // left  edge of bubble at anchor → extends RIGHT
};

interface TailStyle { left?: string; right?: string; top: string; transform: string }
const TAIL: Record<SideSpeaker, TailStyle> = {
  // Pro bubble on the left — tail on bubble's right edge points right at Pro.
  pro: { right: "-14px", top: "42%", transform: "translateY(-50%) rotate(-90deg)" },
  // Con bubble on the right — tail on left edge points left at Con.
  con: { left:  "-14px", top: "42%", transform: "translateY(-50%) rotate(90deg)"  },
};

function useStoreState() {
  return useSyncExternalStore(subscribe, getState, getState);
}

function stripMarkdown(text: string): string {
  return text
    .replace(/```[\s\S]*?```/g, "")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^#+\s+/gm, "")
    .replace(/\*\*([^*]+)\*\*/g, "$1")
    .replace(/\*([^*]+)\*/g, "$1")
    .replace(/~~([^~]+)~~/g, "$1")
    .replace(/^[-*+]\s+/gm, "")
    .trim();
}

export function SpeechBubble(): React.JSX.Element | null {
  const s = useStoreState();
  if (s.slides.length === 0) return null;
  const idx = Math.min(s.slides.length - 1, Math.max(0, s.currentIndex));
  const slide: Slide | undefined = s.slides[idx];
  if (!slide) return null;
  // Judge text is rendered by <JudgeChyron /> at the bottom of the screen.
  if (slide.speaker !== "pro" && slide.speaker !== "con") return null;
  const side: SideSpeaker = slide.speaker;
  const body = stripMarkdown(slide.text);
  if (!body) return null;

  const colour = `var(--color-${side}-accent)`;
  const glow = `var(--color-${side}-glow)`;
  const tail = TAIL[side];

  return (
    <Html position={POSITION[side]} distanceFactor={6}
      style={{
        pointerEvents: "none", width: "400px",
        transform: BUBBLE_TRANSFORM[side],
      }}>
      <AnimatePresence mode="wait">
        <motion.div
          key={slide.id}
          initial={{ opacity: 0, y: 12, scale: 0.95 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -8, scale: 0.95 }}
          transition={{ duration: 0.4, ease: "easeOut" }}
          style={{
            position: "relative",
            background: "linear-gradient(180deg, rgba(10,14,30,0.93) 0%, rgba(10,14,30,0.97) 100%)",
            border: `1.5px solid ${colour}`,
            borderRadius: "20px",
            padding: "1rem 1.15rem 1.05rem",
            boxShadow: `0 0 38px ${glow}, 0 14px 32px rgba(0,0,0,0.6)`,
            backdropFilter: "blur(6px)",
            fontFamily: "var(--font-display)",
            color: "var(--color-fg-primary)",
          }}
        >
          <div style={{
            fontFamily: "var(--font-mono)", fontSize: "9px",
            color: colour, letterSpacing: "0.18em", fontWeight: 700,
            textTransform: "uppercase", marginBottom: "0.55rem",
          }}>
            {slide.variant} · ping {slide.pingIndex}
          </div>
          <div style={{
            fontFamily: "var(--font-display)",
            fontSize: "0.95rem", lineHeight: 1.55, fontWeight: 400,
            letterSpacing: "0.005em",
          }}>{body}</div>

          <svg width="36" height="22" viewBox="0 0 36 22"
            style={{
              position: "absolute",
              left: tail.left, right: tail.right, top: tail.top,
              transform: tail.transform,
              transformOrigin: "center",
              filter: `drop-shadow(0 4px 8px ${glow})`,
            }}>
            <path d="M 0 0 L 36 0 L 18 22 Z"
              fill="rgba(10,14,30,0.96)"
              stroke={colour} strokeWidth="1.5" strokeLinejoin="round" />
            <path d="M 1 0 L 35 0" stroke="rgba(10,14,30,0.96)" strokeWidth="2" />
          </svg>
        </motion.div>
      </AnimatePresence>
    </Html>
  );
}
