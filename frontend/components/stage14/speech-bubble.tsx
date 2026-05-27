"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { Html } from "@react-three/drei";
import { motion, AnimatePresence } from "motion/react";
import { getState, subscribe } from "@/lib/state";
import type { Slide, Speaker } from "@/lib/types";

const POSITION: Record<Speaker, [number, number, number]> = {
  pro:   [-3, 4.0, 0.2],
  judge: [0,  4.0, 1.4],
  con:   [3,  4.0, 0.2],
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
  const body = stripMarkdown(slide.text);
  if (!body && slide.variant !== "verdict") return null;

  const colour = `var(--color-${slide.speaker}-accent)`;
  const glow = `var(--color-${slide.speaker}-glow)`;
  const tailLeft = slide.speaker === "pro" ? "30%"
    : slide.speaker === "con" ? "70%"
    : "50%";

  return (
    <Html position={POSITION[slide.speaker]} center distanceFactor={6}
      style={{ pointerEvents: "none", width: "400px" }}>
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
          {slide.variant === "verdict" ? (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "1.3rem", fontWeight: 600 }}>
                <span style={{ color: "var(--color-pro-accent)" }}>{slide.proScore ?? 0}</span>
                <span style={{ color: "var(--color-fg-muted)" }}> · </span>
                <span style={{ color: "var(--color-con-accent)" }}>{slide.conScore ?? 0}</span>
              </div>
              <div style={{
                fontFamily: "var(--font-display)", fontSize: "1.4rem",
                letterSpacing: "0.08em", fontWeight: 600,
              }}>{(slide.outcome ?? "").replace(/_/g, " ").toUpperCase()}</div>
            </div>
          ) : (
            <div style={{
              fontFamily: "var(--font-display)",
              fontSize: "0.95rem", lineHeight: 1.55, fontWeight: 400,
              letterSpacing: "0.005em",
            }}>{body}</div>
          )}

          <svg width="36" height="22" viewBox="0 0 36 22"
            style={{
              position: "absolute", left: tailLeft, top: "100%",
              transform: "translateX(-50%) translateY(-2px)",
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
