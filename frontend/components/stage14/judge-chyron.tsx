"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { motion, AnimatePresence } from "motion/react";
import { getState, subscribe } from "@/lib/state";
import type { Slide } from "@/lib/types";

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

export function JudgeChyron(): React.JSX.Element | null {
  const s = useStoreState();
  if (s.slides.length === 0) return null;
  const idx = Math.min(s.slides.length - 1, Math.max(0, s.currentIndex));
  const slide: Slide | undefined = s.slides[idx];
  if (!slide || slide.speaker !== "judge") return null;

  const body = stripMarkdown(slide.text);
  if (!body && slide.variant !== "verdict") return null;

  const colour = "var(--color-judge-accent)";
  const glow = "var(--color-judge-glow)";
  const isVerdict = slide.variant === "verdict";

  return (
    <div style={{
      position: "fixed", left: 0, right: 0, bottom: "4.5rem",
      zIndex: 30, pointerEvents: "none",
      display: "flex", justifyContent: "center", padding: "0 2rem",
    }}>
      <AnimatePresence mode="wait">
        <motion.div
          key={slide.id}
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
          transition={{ duration: 0.45, ease: "easeOut" }}
          style={{
            maxWidth: "900px", width: "100%",
            background: "linear-gradient(180deg, rgba(10,14,30,0.94) 0%, rgba(10,14,30,0.98) 100%)",
            border: `1.5px solid ${colour}`, borderRadius: "12px",
            padding: "1rem 1.4rem 1.05rem",
            boxShadow: `0 0 36px ${glow}, 0 14px 28px rgba(0,0,0,0.6)`,
            backdropFilter: "blur(8px)",
            fontFamily: "var(--font-display)", color: "var(--color-fg-primary)",
          }}
        >
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            marginBottom: "0.5rem",
          }}>
            <div style={{
              fontFamily: "var(--font-mono)", fontSize: "9px",
              color: colour, letterSpacing: "0.22em", fontWeight: 700,
              textTransform: "uppercase",
            }}>JUDGE · {slide.variant} · PING {slide.pingIndex}</div>
            {isVerdict && (
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "1.1rem", fontWeight: 600 }}>
                <span style={{ color: "var(--color-pro-accent)" }}>{slide.proScore ?? 0}</span>
                <span style={{ color: "var(--color-fg-muted)" }}> · </span>
                <span style={{ color: "var(--color-con-accent)" }}>{slide.conScore ?? 0}</span>
              </div>
            )}
          </div>
          {isVerdict ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.35rem",
              textAlign: "center", paddingTop: "0.3rem" }}>
              <div style={{
                fontFamily: "var(--font-display)", fontSize: "1.5rem",
                letterSpacing: "0.08em", fontWeight: 600,
                color: slide.outcome === "debate_aborted" ? "#ff8a5c" : "inherit",
              }}>{(slide.outcome ?? "").replace(/_/g, " ").toUpperCase()}</div>
              {slide.text && (
                <div style={{
                  fontFamily: "var(--font-display)", fontSize: "0.85rem",
                  lineHeight: 1.5, fontWeight: 400, opacity: 0.85,
                  textAlign: "center",
                }}>{slide.text}</div>
              )}
            </div>
          ) : (
            <div style={{
              fontFamily: "var(--font-display)",
              fontSize: "1rem", lineHeight: 1.55, fontWeight: 400,
              letterSpacing: "0.005em",
            }}>{body}</div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
