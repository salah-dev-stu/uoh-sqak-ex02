"use client";
import * as React from "react";
import { motion } from "motion/react";
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
  const opacity = active ? 1 : 0.55;

  return (
    <motion.div
      animate={{ opacity, y: active ? 0 : 6 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.4rem" }}
    >
      <motion.svg
        viewBox="0 0 200 240" width="clamp(160px, 16vw, 260px)" height="clamp(192px, 19vw, 312px)"
        animate={active ? { y: [0, -1.5, 0] } : { y: 0 }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      >
        <defs>
          <radialGradient id={`rim-${speaker}`} cx="0.5" cy="0.3" r="0.6">
            <stop offset="0" stopColor={colour} stopOpacity={active ? "0.55" : "0.25"} />
            <stop offset="0.6" stopColor={colour} stopOpacity={active ? "0.18" : "0.08"} />
            <stop offset="1" stopColor="#000" stopOpacity="0.95" />
          </radialGradient>
          <filter id={`glow-${speaker}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation={active ? "3" : "1"} result="b" />
            <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        <ellipse cx="100" cy="220" rx="56" ry="6" fill="rgba(0,0,0,0.6)" />

        <path d="M 100 22
                 Q 76 22 70 50
                 Q 64 70 64 92
                 Q 64 102 70 108
                 L 60 118
                 Q 30 130 20 168
                 Q 14 200 22 230
                 L 178 230
                 Q 186 200 180 168
                 Q 170 130 140 118
                 L 130 108
                 Q 136 102 136 92
                 Q 136 70 130 50
                 Q 124 22 100 22 Z"
          fill={`url(#rim-${speaker})`} stroke={colour} strokeOpacity={active ? "0.85" : "0.5"} strokeWidth="1.2"
          filter={`url(#glow-${speaker})`} />

        <circle cx="100" cy="62" r="46"
          fill={colour} fillOpacity={active ? "0.18" : "0.10"}
          stroke={colour} strokeWidth="1.6"
          filter={`url(#glow-${speaker})`} />
        <text x="100" y="62" textAnchor="middle" dominantBaseline="central"
          fontFamily="var(--font-display)" fontSize="42" fontWeight="600"
          fill={colour} style={{ filter: active ? `drop-shadow(0 0 8px ${glow})` : "none" }}>
          {GLYPH[speaker]}
        </text>

        {active && (
          <motion.circle cx="100" cy="62" r="50"
            fill="none" stroke={colour} strokeWidth="1.2"
            initial={{ opacity: 0.7, scale: 1 }}
            animate={{ opacity: 0, scale: 1.6 }}
            transition={{ duration: 1.8, repeat: Infinity, ease: "easeOut" }} />
        )}
      </motion.svg>

      <div style={{ position: "relative", width: "clamp(140px, 14vw, 230px)" }}>
        <div style={{
          height: "clamp(60px, 6vw, 100px)",
          background: `linear-gradient(180deg, ${colour}22 0%, ${colour}10 30%, #0a1024 90%)`,
          border: `1px solid ${colour}55`, borderBottom: "none",
          borderRadius: "3px 3px 0 0",
          boxShadow: active ? `0 0 30px ${glow}, inset 0 -10px 20px rgba(0,0,0,0.4)` : "inset 0 -10px 20px rgba(0,0,0,0.4)",
          transition: "box-shadow 600ms ease-out",
        }} />
        <div style={{
          height: "1.5px", background: colour, opacity: active ? 0.9 : 0.4,
          boxShadow: active ? `0 0 14px ${glow}` : "none",
          transition: "all 600ms ease-out",
        }} />
        <div style={{
          position: "absolute", top: "30%", left: "50%", transform: "translate(-50%, 0)",
          width: "30%", height: "1.5px",
          background: colour, opacity: active ? 0.6 : 0.2,
        }} />
      </div>

      <div style={{
        fontFamily: "var(--font-mono)", fontSize: "0.7rem", letterSpacing: "0.2em",
        color: colour, textTransform: "uppercase", fontWeight: 600,
        opacity: active ? 1 : 0.55,
        textShadow: active ? `0 0 12px ${glow}` : "none",
        transition: "all 600ms ease-out",
      }}>{NAME[speaker]}</div>
    </motion.div>
  );
}
