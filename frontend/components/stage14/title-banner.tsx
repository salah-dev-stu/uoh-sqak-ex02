"use client";
import * as React from "react";
import { useSyncExternalStore } from "react";
import { motion } from "motion/react";
import { getState, subscribe } from "@/lib/state";

const FALLBACK_TOPIC =
  "Can AI agents create genuinely original art, or only remix human work?";

function useStoreState() {
  return useSyncExternalStore(subscribe, getState, getState);
}

export function TitleBanner(): React.JSX.Element {
  const s = useStoreState();
  const isLive = s.status === "live";
  const topic = s.topic ?? FALLBACK_TOPIC;
  const statusLabel = isLive ? "On Air"
    : s.status === "done" ? "Recorded"
    : s.status === "error" ? "Off Air"
    : "Standby";

  return (
    <div style={{
      position: "fixed", top: 0, left: 0, right: 0,
      zIndex: 25, padding: "0.7rem 2rem 0.6rem",
      pointerEvents: "none",
      background: "linear-gradient(180deg, rgba(7,11,26,0.9) 0%, rgba(7,11,26,0.55) 70%, transparent 100%)",
    }}>
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "center",
        gap: "1.5rem", maxWidth: "1100px", margin: "0 auto",
      }}>
        <div style={{
          flex: 1, height: "1px",
          background: "linear-gradient(90deg, transparent, var(--color-judge-accent) 75%)",
          maxWidth: "220px", opacity: 0.7,
        }} />

        <motion.div
          initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ textAlign: "center", minWidth: "16rem", flexShrink: 1 }}>
          <div style={{
            fontFamily: "var(--font-display)",
            fontSize: "clamp(0.85rem, 0.6vw + 0.4rem, 1.2rem)",
            letterSpacing: "0.35em", fontWeight: 700,
            color: "var(--color-judge-accent)",
            textShadow: "0 0 22px rgba(255,201,76,0.45)",
            lineHeight: 1.1,
          }}>AGENT DEBATE</div>
          <div style={{
            display: "flex", justifyContent: "center", alignItems: "center", gap: "0.5rem",
            fontFamily: "var(--font-mono)", fontSize: "0.55rem",
            letterSpacing: "0.45em", color: "var(--color-fg-muted)",
            marginTop: "0.2rem", textTransform: "uppercase", lineHeight: 1,
          }}>
            <span>2026</span>
            <span style={{ opacity: 0.4 }}>·</span>
            <span style={{
              display: "inline-flex", alignItems: "center", gap: "0.3rem",
              color: isLive ? "var(--color-pro-accent)"
                : s.status === "error" ? "#ff6b6b"
                : "var(--color-fg-muted)",
            }}>
              {isLive && (
                <motion.span
                  animate={{ opacity: [1, 0.3, 1] }}
                  transition={{ duration: 1.4, repeat: Infinity, ease: "easeInOut" }}
                  style={{
                    width: "6px", height: "6px", borderRadius: "50%",
                    background: "var(--color-pro-accent)",
                    boxShadow: "0 0 8px var(--color-pro-glow)",
                  }}
                />
              )}
              {statusLabel}
            </span>
          </div>
          <div style={{
            fontFamily: "var(--font-display)",
            fontSize: "clamp(0.7rem, 0.4vw + 0.45rem, 0.85rem)",
            color: "var(--color-fg-primary)",
            opacity: 0.85, fontStyle: "italic", fontWeight: 400,
            marginTop: "0.35rem",
            maxWidth: "640px", lineHeight: 1.25,
            whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
          }}>
            <span style={{ color: "var(--color-fg-muted)", fontStyle: "normal" }}>Motion: </span>
            &ldquo;{topic}&rdquo;
          </div>
        </motion.div>

        <div style={{
          flex: 1, height: "1px",
          background: "linear-gradient(90deg, var(--color-judge-accent) 25%, transparent)",
          maxWidth: "220px", opacity: 0.7,
        }} />
      </div>
    </div>
  );
}
