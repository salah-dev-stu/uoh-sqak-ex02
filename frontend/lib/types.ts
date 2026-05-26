export type Speaker = "pro" | "con" | "judge";
export type SlideVariant = "intro" | "argument" | "counter" | "rebuttal" | "verdict";
export type Outcome = "pro_wins" | "con_wins" | "debate_aborted" | "budget_exhausted";

export interface Slide {
  id: string;
  speaker: Speaker;
  variant: SlideVariant;
  pingIndex: number;
  text: string;
  timestamp: string;
  proScore?: number;
  conScore?: number;
  outcome?: Outcome;
}

export interface SlideState {
  slides: Slide[];
  currentIndex: number;
  followLive: boolean;
  status: "idle" | "live" | "done" | "error";
  proTotal: number;
  conTotal: number;
  pingCounter: { current: number; total: number };
  error?: string;
}

export interface DebateMessage {
  msg_id: string;
  from: Speaker | "main";
  to: Speaker | "main";
  role: string;
  ping_index: number;
  text: string;
  timestamp: string;
  tokens_in?: number;
  tokens_out?: number;
}

export interface Verdict {
  pro_total: number;
  con_total: number;
  outcome: Outcome;
  rationale?: string;
}

export interface SseEvent {
  type:
    | "started" | "message" | "before_round" | "after_round"
    | "verdict" | "after_verdict" | "done" | "error" | "stop_requested";
  payload: unknown;
}

export interface StartDebateResponse { debate_id: string; }
