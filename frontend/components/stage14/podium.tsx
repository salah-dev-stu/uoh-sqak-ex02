"use client";
import * as React from "react";
import { motion } from "motion/react";
import type { Speaker } from "@/lib/types";

const GLYPH: Record<Speaker, string> = { pro: "P", con: "C", judge: "⚖" };
const NAME: Record<Speaker, string> = { pro: "PRO", con: "CON", judge: "JUDGE" };
const TILT: Record<Speaker, number> = { pro: 12, judge: 0, con: -12 };

interface Props {
  speaker: Speaker;
  active: boolean;
}

export function Podium({ speaker, active }: Props): React.JSX.Element {
  const colour = `var(--color-${speaker}-accent)`;
  const glow = `var(--color-${speaker}-glow)`;
  const opacity = active ? 1 : 0.55;
  const yawDeg = TILT[speaker];

  return (
    <motion.div
      animate={{ opacity, y: active ? 0 : 6 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      style={{
        display: "flex", flexDirection: "column", alignItems: "center",
        transform: `rotateY(${yawDeg}deg)`,
        transformStyle: "preserve-3d",
        transformOrigin: "bottom center",
      }}
    >
      <motion.svg
        viewBox="0 0 220 360"
        width="clamp(180px, 18vw, 300px)"
        height="clamp(295px, 29.5vw, 491px)"
        animate={active ? { y: [0, -1.5, 0] } : { y: 0 }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      >
        <defs>
          <radialGradient id={`head-${speaker}`} cx="0.5" cy="0.35" r="0.65">
            <stop offset="0" stopColor={colour} stopOpacity={active ? "0.55" : "0.28"} />
            <stop offset="0.55" stopColor={colour} stopOpacity={active ? "0.18" : "0.10"} />
            <stop offset="1" stopColor="#000" stopOpacity="0.95" />
          </radialGradient>
          <linearGradient id={`front-${speaker}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={colour} stopOpacity={active ? "0.45" : "0.30"} />
            <stop offset="0.3" stopColor={colour} stopOpacity={active ? "0.22" : "0.14"} />
            <stop offset="1" stopColor="#050a1c" stopOpacity="1" />
          </linearGradient>
          <linearGradient id={`top-${speaker}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={colour} stopOpacity={active ? "0.75" : "0.40"} />
            <stop offset="1" stopColor="#0a1024" stopOpacity="1" />
          </linearGradient>
          <linearGradient id={`side-${speaker}`} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#000" stopOpacity="0.7" />
            <stop offset="1" stopColor="#0a1024" stopOpacity="1" />
          </linearGradient>
          <filter id={`glowf-${speaker}`} x="-30%" y="-30%" width="160%" height="160%">
            <feGaussianBlur stdDeviation={active ? "2.5" : "1"} result="b" />
            <feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge>
          </filter>
        </defs>

        <ellipse cx="110" cy="350" rx="86" ry="6" fill="rgba(0,0,0,0.55)" />

        <path d="M 110 25
                 Q 86 25 80 55
                 Q 74 78 74 100
                 Q 74 112 80 120
                 L 68 132
                 Q 50 138 44 160
                 L 30 178
                 L 50 200
                 L 80 196
                 L 80 220
                 L 140 220
                 L 140 196
                 L 170 200
                 L 190 178
                 L 176 160
                 Q 170 138 152 132
                 L 140 120
                 Q 146 112 146 100
                 Q 146 78 140 55
                 Q 134 25 110 25 Z"
          fill={`url(#head-${speaker})`}
          stroke={colour}
          strokeOpacity={active ? "0.9" : "0.55"}
          strokeWidth="1.4"
          filter={`url(#glowf-${speaker})`} />

        <circle cx="110" cy="70" r="34"
          fill={colour} fillOpacity={active ? "0.20" : "0.10"}
          stroke={colour} strokeWidth="1.6"
          filter={`url(#glowf-${speaker})`} />
        <text x="110" y="70" textAnchor="middle" dominantBaseline="central"
          fontFamily="var(--font-display)" fontSize="32" fontWeight="600"
          fill={colour}
          style={{ filter: active ? `drop-shadow(0 0 6px ${glow})` : "none" }}>
          {GLYPH[speaker]}
        </text>

        {active && (
          <motion.circle cx="110" cy="70" r="38"
            fill="none" stroke={colour} strokeWidth="1.2"
            initial={{ opacity: 0.7, scale: 1 }}
            animate={{ opacity: 0, scale: 1.7 }}
            transition={{ duration: 1.8, repeat: Infinity, ease: "easeOut" }}
            style={{ transformOrigin: "110px 70px" }} />
        )}

        <polygon points="40,220 180,220 195,232 25,232" fill={`url(#top-${speaker})`}
          stroke={colour} strokeOpacity={active ? "0.7" : "0.4"} strokeWidth="0.8" />
        <polygon points="195,232 195,338 180,348 180,220"
          fill={`url(#side-${speaker})`} stroke={colour} strokeOpacity="0.25" strokeWidth="0.6" />
        <rect x="25" y="232" width="170" height="106"
          fill={`url(#front-${speaker})`}
          stroke={colour} strokeOpacity={active ? "0.7" : "0.4"} strokeWidth="0.8" />

        <circle cx="110" cy="280" r="18"
          fill={colour} fillOpacity="0.10" stroke={colour} strokeOpacity={active ? "0.8" : "0.5"} strokeWidth="1" />
        <text x="110" y="280" textAnchor="middle" dominantBaseline="central"
          fontFamily="var(--font-display)" fontSize="18" fontWeight="600"
          fill={colour} fillOpacity={active ? "0.95" : "0.65"}>
          {GLYPH[speaker]}
        </text>

        <line x1="80" y1="220" x2="80" y2="200" stroke={colour} strokeOpacity={active ? "0.85" : "0.5"} strokeWidth="1.6" />
        <line x1="80" y1="200" x2="92" y2="194" stroke={colour} strokeOpacity={active ? "0.85" : "0.5"} strokeWidth="1.6" />
        <ellipse cx="96" cy="192" rx="6" ry="4" fill="#1a1f2e" stroke={colour}
          strokeOpacity={active ? "0.95" : "0.6"} strokeWidth="1.2" />
      </motion.svg>

      <div style={{
        marginTop: "0.3rem",
        fontFamily: "var(--font-mono)", fontSize: "0.7rem", letterSpacing: "0.22em",
        color: colour, textTransform: "uppercase", fontWeight: 700,
        opacity: active ? 1 : 0.55,
        textShadow: active ? `0 0 14px ${glow}` : "none",
        transition: "all 600ms ease-out",
      }}>{NAME[speaker]}</div>
    </motion.div>
  );
}
