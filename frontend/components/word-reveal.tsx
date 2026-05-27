"use client";
import * as React from "react";
import { motion } from "motion/react";

interface Props { text: string; trigger: boolean; }

// Parse **bold** and *italic* into JSX; strip other markdown markers.
function renderMarkdown(text: string): React.ReactNode[] {
  // Strip common non-emphasis markdown noise: headings, code fences, lists.
  const cleaned = text
    .replace(/```[\s\S]*?```/g, "")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/^#+\s+/gm, "")
    .replace(/^[-*+]\s+/gm, "• ")
    .replace(/~~([^~]+)~~/g, "$1");

  const parts: React.ReactNode[] = [];
  const re = /\*\*([^*\n]+)\*\*|\*([^*\n]+)\*/g;
  let last = 0;
  let m: RegExpExecArray | null;
  let key = 0;
  while ((m = re.exec(cleaned)) !== null) {
    if (m.index > last) parts.push(cleaned.slice(last, m.index));
    if (m[1] !== undefined) {
      parts.push(<strong key={key++}>{m[1]}</strong>);
    } else if (m[2] !== undefined) {
      parts.push(<em key={key++}>{m[2]}</em>);
    }
    last = m.index + m[0].length;
  }
  if (last < cleaned.length) parts.push(cleaned.slice(last));
  return parts;
}

export function WordReveal({ text, trigger }: Props): React.JSX.Element {
  return (
    <motion.p
      initial={{ opacity: 0, y: 8 }}
      animate={trigger ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
      transition={{ duration: 0.55, ease: "easeOut" }}
      style={{
        fontFamily: "var(--font-body)",
        fontSize: "clamp(0.95rem, 0.7vw + 0.5rem, 1.25rem)",
        lineHeight: 1.55, maxWidth: "62ch", fontWeight: 300,
        overflow: "hidden",
      }}
    >
      {renderMarkdown(text)}
    </motion.p>
  );
}
