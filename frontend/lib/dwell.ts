// Per-slide reading dwell time.
//
// Brysbaert 2019 meta-analysis (190 studies) puts adult silent reading at
// ~238 wpm for non-fiction and notes "reading rates are lower for ... readers
// with English as second language". BBC subtitle guideline is 160-180 wpm
// for a general audience; non-native intermediate readers sit at 120-200 wpm.
//
// HW2 audience is non-native English readers (the lecturer + grading agent
// reading the debate).
//
// Two tunings — a standalone slide gets a generous 130 wpm + 0.8 s entry
// buffer + a 14 s cap, but a chunk (one sentence-bundle inside a multi-chunk
// Pro/Con turn) reads at 170 wpm with only a 0.3 s entry buffer and a 7.5 s
// cap. Without that separation, splitting one 80-word bubble into three
// 28-word chunks would balloon the per-turn dwell from 14 s to ~41 s because
// every chunk would near-saturate the 14 s cap.

const STANDALONE = { wpm: 130, entry: 800, min: 3500, max: 14_000 };
const CHUNK      = { wpm: 130, entry: 700, min: 4500, max: 11_000 };

export interface DwellOpts {
  isChunk?: boolean;
}

export function computeDwellMs(text: string, opts?: DwellOpts): number {
  const cfg = opts?.isChunk ? CHUNK : STANDALONE;
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  if (words === 0) return cfg.min;
  const total = (words / cfg.wpm) * 60_000 + cfg.entry;
  return Math.max(cfg.min, Math.min(cfg.max, total));
}
