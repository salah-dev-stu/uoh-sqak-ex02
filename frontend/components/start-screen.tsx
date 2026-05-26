"use client";
import * as React from "react";
import { useState } from "react";
import { motion } from "motion/react";
import { startDebate } from "@/lib/api";
import { openStream } from "@/lib/sse";
import { setState } from "@/lib/state";
import { DEFAULT_N_PINGS } from "@/lib/config";

export function StartScreen(): React.JSX.Element {
  const [topic, setTopic] = useState("Can AI agents create truly original work, or is everything just recombination?");
  const [nPings, setNPings] = useState(DEFAULT_N_PINGS);
  const [live, setLive] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onStart(): Promise<void> {
    setBusy(true); setError(null);
    try {
      const r = await startDebate({ nPings, live });
      openStream(r.debate_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start");
      setState({ status: "error" }); setBusy(false);
    }
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.8 }}
      style={{
        minHeight: "100vh", display: "flex", flexDirection: "column",
        justifyContent: "center", alignItems: "center", padding: "5vh 6vw", gap: "3rem",
      }}>
      <h1 style={{
        fontFamily: "var(--font-display)", fontSize: "clamp(2rem, 5vw, 4rem)",
        letterSpacing: "0.1em", fontWeight: 500,
      }}>AGENT DEBATE</h1>
      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem", width: "min(560px, 90vw)" }}>
        <label style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--color-fg-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Topic
          <textarea value={topic} onChange={(e) => setTopic(e.target.value)} rows={2}
            style={{ display: "block", marginTop: 8, width: "100%", padding: "0.75rem",
              background: "transparent", border: "1px solid var(--color-fg-dim)",
              color: "var(--color-fg-primary)", fontFamily: "var(--font-body)", fontSize: "1rem", borderRadius: 4 }} />
        </label>
        <label style={{ fontFamily: "var(--font-mono)", fontSize: "0.7rem", color: "var(--color-fg-muted)", textTransform: "uppercase" }}>
          Pings per side
          <input type="number" min={1} max={20} value={nPings} onChange={(e) => setNPings(Number(e.target.value))}
            style={{ display: "block", marginTop: 8, padding: "0.5rem 0.75rem",
              background: "transparent", border: "1px solid var(--color-fg-dim)",
              color: "var(--color-fg-primary)", fontFamily: "var(--font-mono)", borderRadius: 4, width: 80 }} />
        </label>
        <label style={{ display: "flex", gap: "0.5rem", alignItems: "center", fontFamily: "var(--font-mono)", fontSize: "0.75rem", color: "var(--color-fg-primary)" }}>
          <input type="checkbox" checked={live} onChange={(e) => setLive(e.target.checked)} />
          <span>Live (real Claude — ~8 min)</span>
        </label>
        <button onClick={onStart} disabled={busy} style={{
          marginTop: "1rem", padding: "1rem 2rem", background: "var(--color-judge-accent)",
          color: "var(--color-bg-base)", border: "none", borderRadius: 4,
          fontFamily: "var(--font-display)", letterSpacing: "0.1em", fontWeight: 600,
          fontSize: "1rem", cursor: busy ? "wait" : "pointer", textTransform: "uppercase",
        }}>{busy ? "Starting…" : "▶ Start debate"}</button>
        {error && <p style={{ color: "var(--color-pro-accent)", fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>{error}</p>}
      </div>
    </motion.div>
  );
}
