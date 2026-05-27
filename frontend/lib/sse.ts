import type { SseEvent, DebateMessage } from "./types";
import { appendSlide, resetState, setState, getState } from "./state";
import { streamUrl } from "./api";

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
  setState({ status: "live", currentIndex: 0, followLive: true });

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
      appendSlide({
        id: m.msg_id, speaker: m.from === "main" ? "judge" : m.from,
        variant: variantFromRole(m.role), pingIndex: m.ping_index,
        text: m.text, timestamp: m.timestamp,
      });
      break;
    }
    case "after_round": {
      const p = evt.payload as { pro_total: number; con_total: number };
      setState({ proTotal: p.pro_total, conTotal: p.con_total });
      break;
    }
    case "verdict": {
      const p = evt.payload as { verdict: { pro_total: number; con_total: number; outcome: string } };
      const v = p.verdict;
      appendSlide({
        id: "verdict", speaker: "judge", variant: "verdict",
        pingIndex: getState().slides.length, text: "", timestamp: new Date().toISOString(),
        proScore: v.pro_total, conScore: v.con_total, outcome: v.outcome as never,
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
