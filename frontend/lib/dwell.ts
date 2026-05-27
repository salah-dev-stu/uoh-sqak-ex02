// Per-slide reading dwell time.
//
// Brysbaert 2019 meta-analysis (190 studies) puts adult silent reading at
// ~238 wpm for non-fiction and notes "reading rates are lower for ... readers
// with English as second language". BBC subtitle guideline is 160–180 wpm
// for a general audience; non-native intermediate readers sit at 120–200 wpm.
//
// HW2 audience is non-native English readers (the lecturer + grading agent
// reading the debate). We use 130 wpm + an 800 ms reading-entry buffer,
// clamped to [3.5 s, 14 s] so a one-word slide doesn't blink past and a
// long verdict block doesn't overstay.

const WPM = 130;
const READING_ENTRY_MS = 800;
const MIN_DWELL_MS = 3500;
const MAX_DWELL_MS = 14_000;

export function computeDwellMs(text: string): number {
  const words = text.trim().split(/\s+/).filter(Boolean).length;
  if (words === 0) return MIN_DWELL_MS;
  const reading = (words / WPM) * 60_000;
  const total = reading + READING_ENTRY_MS;
  return Math.max(MIN_DWELL_MS, Math.min(MAX_DWELL_MS, total));
}
