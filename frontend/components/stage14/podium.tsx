"use client";
import * as React from "react";
import type { Speaker } from "@/lib/types";

const GLYPH: Record<Speaker, string> = { pro: "P", con: "C", judge: "⚖" };
const NAME: Record<Speaker, string> = { pro: "PRO", con: "CON", judge: "JUDGE" };

interface Props {
  speaker: Speaker;
  active: boolean;
}

export function Podium({ speaker, active }: Props): React.JSX.Element {
  const colour = `var(--color-${speaker}-accent)`;
  const glow = `var(--color-${speaker}-glow)`;
  const dim = active ? 1 : 0.3;
  return (
    <div style={{
      display: "flex", flexDirection: "column", alignItems: "center", gap: "0.5rem",
      opacity: dim, transition: "opacity 600ms ease-out",
    }}>
      <div style={{
        width: "clamp(48px, 5vw, 80px)", height: "clamp(48px, 5vw, 80px)", borderRadius: "50%",
        background: `radial-gradient(circle at 30% 25%, ${colour}33, transparent 60%)`,
        border: `1.5px solid ${colour}`,
        boxShadow: active ? `0 0 40px ${glow}, inset 0 0 12px ${glow}` : `0 0 8px ${glow}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        color: colour, fontFamily: "var(--font-display)", fontWeight: 600,
        fontSize: "clamp(1.2rem, 1.4vw, 1.8rem)",
        transition: "box-shadow 600ms ease-out",
      }}>{GLYPH[speaker]}</div>

      <svg viewBox="0 0 60 80" width="clamp(48px,5vw,80px)" height="clamp(64px,6.5vw,106px)">
        <path d="M 30 5 Q 24 5 22 14 Q 18 18 18 24 L 14 38 Q 12 50 18 56 L 20 60
                 L 16 78 L 44 78 L 40 60 L 42 56 Q 48 50 46 38 L 42 24 Q 42 18 38 14 Q 36 5 30 5 Z"
          fill={colour} fillOpacity="0.18" stroke={colour} strokeWidth="1" strokeLinejoin="round" />
      </svg>

      <div style={{ position: "relative", width: "clamp(80px,8vw,120px)" }}>
        <div style={{
          height: "clamp(34px,3.5vw,52px)",
          background: `linear-gradient(180deg, ${colour}22 0%, ${colour}11 50%, #0a1024 100%)`,
          border: `1px solid ${colour}55`, borderBottom: "none",
          borderRadius: "2px 2px 0 0",
        }} />
        <div style={{
          height: "1px", background: colour, opacity: 0.6,
          boxShadow: active ? `0 0 8px ${glow}` : "none",
        }} />
      </div>

      <div style={{
        fontFamily: "var(--font-mono)", fontSize: "0.62rem", letterSpacing: "0.15em",
        color: colour, textTransform: "uppercase",
        opacity: active ? 1 : 0.5,
      }}>{NAME[speaker]}</div>
    </div>
  );
}
