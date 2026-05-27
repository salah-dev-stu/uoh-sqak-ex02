import type { SseEvent, DebateMessage } from "./types";
import { appendSlide, resetState, setState, getState } from "./state";
import { streamUrl } from "./api";
import { splitIntoChunks } from "./chunks";

export function shouldSkip(payload: unknown, seen: Set<string>): boolean {
  if (!payload || typeof payload !== "object") return true;
  const p = payload as Record<string, unknown>;
  if (typeof p.msg_id !== "string") return true;
  if (seen.has(p.msg_id)) return true;
  if ((p.from === "pro" || p.from === "con") && p.to !== "judge") return true;
  return false;
}

export function openStream(debateId: string, topic?: string): () => void {
  resetState();
  const es = new EventSource(streamUrl(debateId));
  const seen = new Set<string>();
  setState({ status: "live", currentIndex: 0, followLive: true, topic });

  appendSlide({
    id: "synthetic-judge-intro",
    speaker: "judge",
    variant: "intro",
    pingIndex: 0,
    text:
      `Welcome to today's debate. Tonight's motion: "${topic ?? "Can AI agents create genuinely original art?"}". ` +
      "Pro will argue the affirmative; Con will argue the negative. Each side has ten pings. " +
      "I will moderate and score. Let the debate begin.",
    timestamp: new Date().toISOString(),
  });

  es.onmessage = (e) => {
    const evt: SseEvent = JSON.parse(e.data);
    handleEvent(evt, seen);
  };
  es.onerror = () => setState({ status: "error", error: "SSE connection lost" });

  return () => es.close();
}

function handleEvent(evt: SseEvent, seen: Set<string>): void {
  switch (evt.type) {
    case "message": {
      if (shouldSkip(evt.payload, seen)) return;
      const m = evt.payload as DebateMessage;
      seen.add(m.msg_id);
      // Skip setup-phase plumbing (directives + acks) — show only real debate content.
      if (m.role === "setup_directive" || m.role === "ack") return;
      // Skip judge re-broadcasts of the other side's text (forwarding plumbing).
      if (m.from === "judge" && (m.role === "counter" || m.role === "rebuttal")) return;
      const speaker = m.from === "main" ? "judge" : m.from;
      const variant = variantFromRole(m.role);
      // Split Pro/Con responses into sentence-bundled chunks so the stage
      // cycles through smaller bubbles instead of one wall of text. Judge
      // text goes straight to the chyron as a single slide.
      const chunks = speaker === "judge" ? [m.text] : splitIntoChunks(m.text);
      chunks.forEach((chunk, i) => {
        appendSlide({
          id: chunks.length === 1 ? m.msg_id : `${m.msg_id}-c${i}`,
          speaker, variant, pingIndex: m.ping_index,
          text: chunk, timestamp: m.timestamp,
        });
      });
      break;
    }
    case "after_round": {
      const p = evt.payload as { pro_total: number; con_total: number };
      setState({ proTotal: p.pro_total, conTotal: p.con_total });
      break;
    }
    case "verdict": {
      const p = evt.payload as {
        verdict: { pro_total?: number; con_total?: number; reason?: string };
        outcome?: string;
      };
      const v = p.verdict ?? {};
      const aborted = v.reason === "setup_phase_timeout" || p.outcome === "debate_aborted";
      appendSlide({
        id: "verdict", speaker: "judge", variant: "verdict",
        pingIndex: getState().slides.length,
        text: aborted
          ? "Debate aborted: setup phase timed out. The Pro/Con agents did not respond — Claude CLI may be busy with another session. Try refreshing in a moment."
          : "",
        timestamp: new Date().toISOString(),
        proScore: v.pro_total ?? 0,
        conScore: v.con_total ?? 0,
        outcome: (aborted ? "debate_aborted" : p.outcome) as never,
      });
      break;
    }
    case "done": setState({ status: "done" }); break;
    case "error": setState({ status: "error", error: String(evt.payload) }); break;
  }
}

function variantFromRole(role: string): "intro" | "argument" | "counter" | "rebuttal" {
  if (role === "setup_directive" || role === "intro") return "intro";
  if (role === "counter") return "counter";
  if (role === "rebuttal") return "rebuttal";
  return "argument";
}
