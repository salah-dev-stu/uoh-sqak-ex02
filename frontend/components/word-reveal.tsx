"use client";
import * as React from "react";
import { motion } from "motion/react";
import { WORD_STAGGER_MS, WORD_FADE_MS } from "@/lib/config";

interface Props { text: string; trigger: boolean; }

export function WordReveal({ text, trigger }: Props): React.JSX.Element {
  const words = text.split(/(\s+)/);
  return (
    <p style={{
      fontFamily: "var(--font-body)", fontSize: "clamp(0.95rem, 0.7vw + 0.5rem, 1.25rem)",
      lineHeight: 1.55, maxWidth: "62ch", fontWeight: 300, overflow: "hidden",
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
