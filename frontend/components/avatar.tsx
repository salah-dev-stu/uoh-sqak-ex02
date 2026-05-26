"use client";
import * as React from "react";
import { motion } from "motion/react";
import type { Speaker } from "@/lib/types";

const GLYPHS: Record<Speaker, string> = { pro: "P", con: "C", judge: "⚖" };
const COLORS: Record<Speaker, { fg: string; bg: string; glow: string }> = {
  pro:   { fg: "var(--color-pro-accent)",   bg: "rgb(255 61 168 / 0.12)",  glow: "var(--color-pro-glow)" },
  con:   { fg: "var(--color-con-accent)",   bg: "rgb(61 168 255 / 0.12)",  glow: "var(--color-con-glow)" },
  judge: { fg: "var(--color-judge-accent)", bg: "rgb(255 201 76 / 0.12)",  glow: "var(--color-judge-glow)" },
};

interface Props { speaker: Speaker; pulse: boolean; }

export function Avatar({ speaker, pulse }: Props): React.JSX.Element {
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
