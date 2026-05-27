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
    it("returns the chunk minimum (2500ms) for empty input", () => {
      expect(computeDwellMs("", { isChunk: true })).toBe(2500);
    });

    it("caps at the chunk maximum (7500ms) for long chunks", () => {
      const text = Array.from({ length: 200 }, () => "word").join(" ");
      expect(computeDwellMs(text, { isChunk: true })).toBe(7500);
    });

    it("scales faster than standalone (170 wpm vs 130)", () => {
      const text = Array.from({ length: 25 }, () => "word").join(" ");
      const chunk = computeDwellMs(text, { isChunk: true });
      const standalone = computeDwellMs(text);
      expect(chunk).toBeLessThan(standalone);
    });

    it("a typical 28-word chunk takes ~7s, not 14s", () => {
      // 28 words @ 170 wpm = ~9882 ms + 300 ms = ~10182 → clamped to 7500.
      const text = Array.from({ length: 28 }, () => "word").join(" ");
      const ms = computeDwellMs(text, { isChunk: true });
      expect(ms).toBeGreaterThanOrEqual(2500);
      expect(ms).toBeLessThanOrEqual(7500);
      // 3 such chunks in a turn ≈ ≤ 22.5s; standalone would be 14s × 1 = 14s
      // so the chunked total stays roughly in the same order of magnitude.
      expect(ms * 3).toBeLessThan(25_000);
    });
  });
});
