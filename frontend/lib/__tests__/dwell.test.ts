import { describe, it, expect } from "vitest";
import { computeDwellMs } from "@/lib/dwell";

describe("computeDwellMs", () => {
  it("returns the minimum dwell for empty text", () => {
    expect(computeDwellMs("")).toBe(3500);
    expect(computeDwellMs("   ")).toBe(3500);
  });

  it("returns the minimum dwell for very short text", () => {
    // 1 word @ 130 wpm = ~462 ms + 800 ms = 1262 ms → clamped to 3500 ms.
    expect(computeDwellMs("Hello")).toBe(3500);
  });

  it("scales with word count between the bounds", () => {
    // 20 words @ 130 wpm = ~9230 ms + 800 ms = ~10030 ms, inside [3500, 14000].
    const text = Array.from({ length: 20 }, () => "word").join(" ");
    const ms = computeDwellMs(text);
    expect(ms).toBeGreaterThan(3500);
    expect(ms).toBeLessThan(14_000);
    expect(ms).toBeCloseTo(10_030, -2); // within 50 ms
  });

  it("caps at the maximum dwell for long text", () => {
    const text = Array.from({ length: 500 }, () => "word").join(" ");
    expect(computeDwellMs(text)).toBe(14_000);
  });

  it("ignores extra whitespace when counting words", () => {
    expect(computeDwellMs("a  b\tc\n  d")).toBe(computeDwellMs("a b c d"));
  });

  describe("chunk mode", () => {
    it("returns the chunk minimum (4500ms) for empty input", () => {
      expect(computeDwellMs("", { isChunk: true })).toBe(4500);
    });

    it("caps at the chunk maximum (11000ms) for long chunks", () => {
      const text = Array.from({ length: 200 }, () => "word").join(" ");
      expect(computeDwellMs(text, { isChunk: true })).toBe(11_000);
    });

    it("scales at the same wpm as standalone but with a tighter cap", () => {
      // Same wpm (130), so a small chunk reads at roughly the same speed
      // as a standalone slide. The chunk cap (11s) is lower than the
      // standalone cap (14s) so very long chunks don't overstay.
      const long = Array.from({ length: 80 }, () => "word").join(" ");
      const chunkCap = computeDwellMs(long, { isChunk: true });
      const standaloneCap = computeDwellMs(long);
      expect(chunkCap).toBeLessThanOrEqual(standaloneCap);
    });

    it("a typical 28-word chunk takes ~11s so the reader has time to absorb it", () => {
      // 28 words @ 130 wpm = ~12923 ms + 700 ms = ~13623 → clamped to 11000.
      const text = Array.from({ length: 28 }, () => "word").join(" ");
      const ms = computeDwellMs(text, { isChunk: true });
      expect(ms).toBeGreaterThanOrEqual(4500);
      expect(ms).toBeLessThanOrEqual(11_000);
      // 3 such chunks in a turn ≈ ≤ 33s — slow but comfortable for
      // non-native readers, which was the explicit user requirement.
    });
  });
});
