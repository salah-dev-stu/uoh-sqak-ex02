"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { motion, AnimatePresence } from "motion/react";
import { getState, subscribe } from "@/lib/state";
import type { Slide } from "@/lib/types";

const NAME: Record<Slide["speaker"], string> = {
  pro: "PRO", con: "CON", judge: "JUDGE",
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

export function Chyron(): React.JSX.Element | null {
  const s = useStoreState();
  if (s.slides.length === 0) return null;
  const idx = Math.min(s.slides.length - 1, Math.max(0, s.currentIndex));
  const slide = s.slides[idx];
  if (!slide) return null;

  const colour = `var(--color-${slide.speaker}-accent)`;
  const glow = `var(--color-${slide.speaker}-glow)`;
  const body = stripMarkdown(slide.text);
  if (!body) return null;

  return (
    <div style={{
      position: "fixed", left: 0, right: 0, bottom: "4rem",
      display: "flex", justifyContent: "center", pointerEvents: "none",
      zIndex: 30, padding: "0 4vw",
    }}>
      <AnimatePresence mode="wait">
        <motion.div
          key={slide.id}
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -10, opacity: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          style={{
            maxWidth: "min(900px, 92vw)", width: "100%",
            background: "linear-gradient(180deg, rgba(7,11,26,0.55) 0%, rgba(7,11,26,0.92) 100%)",
            border: `1px solid ${colour}55`,
            borderLeft: `3px solid ${colour}`,
            borderRadius: "6px",
            padding: "1rem 1.25rem 1.1rem",
            boxShadow: `0 0 36px ${glow}, 0 8px 28px rgba(0,0,0,0.55)`,
            backdropFilter: "blur(8px)",
          }}
        >
          <div style={{
            display: "flex", gap: "0.7rem", alignItems: "center",
            fontFamily: "var(--font-mono)", fontSize: "0.65rem",
            letterSpacing: "0.18em", textTransform: "uppercase",
            marginBottom: "0.55rem",
          }}>
            <span style={{ color: colour, fontWeight: 700 }}>{NAME[slide.speaker]}</span>
            <span style={{ color: "var(--color-fg-muted)" }}>·</span>
            <span style={{ color: "var(--color-fg-muted)" }}>{slide.variant}</span>
            <span style={{ color: "var(--color-fg-muted)" }}>·</span>
            <span style={{ color: "var(--color-fg-muted)" }}>ping {slide.pingIndex}</span>
          </div>
          {slide.variant === "verdict" ? (
            <div style={{
              display: "flex", alignItems: "center", gap: "1.5rem",
              fontFamily: "var(--font-display)",
            }}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "1.5rem", fontWeight: 600 }}>
                <span style={{ color: "var(--color-pro-accent)" }}>{slide.proScore ?? 0}</span>
                <span style={{ color: "var(--color-fg-muted)" }}> · </span>
                <span style={{ color: "var(--color-con-accent)" }}>{slide.conScore ?? 0}</span>
              </div>
              <div style={{
                fontSize: "1.6rem", letterSpacing: "0.1em", fontWeight: 600,
                color: "var(--color-fg-primary)",
              }}>{(slide.outcome ?? "").replace(/_/g, " ").toUpperCase()}</div>
            </div>
          ) : (
            <div style={{
              fontFamily: "var(--font-body)", fontWeight: 300,
              fontSize: "clamp(0.9rem, 0.5vw + 0.6rem, 1.1rem)",
              lineHeight: 1.55, color: "var(--color-fg-primary)",
              maxHeight: "30vh", overflowY: "auto",
            }}>{body}</div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
