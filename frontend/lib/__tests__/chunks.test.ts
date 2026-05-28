import { describe, it, expect } from "vitest";
import { splitIntoChunks } from "@/lib/chunks";

describe("splitIntoChunks", () => {
  it("returns empty array for empty input", () => {
    expect(splitIntoChunks("")).toEqual([]);
    expect(splitIntoChunks("   ")).toEqual([]);
  });

  it("returns text as a single chunk when no sentence boundary is found", () => {
    expect(splitIntoChunks("just a phrase no terminator")).toEqual([
      "just a phrase no terminator",
    ]);
  });

  it("bundles short consecutive sentences into one chunk under maxWords", () => {
    const text = "Yes. Of course. We agree.";
    expect(splitIntoChunks(text, 28)).toEqual(["Yes. Of course. We agree."]);
  });

  it("splits a typical Pro response into ~3 chunks", () => {
    const text =
      "Originality has never meant ex nihilo. Picasso absorbed African masks, " +
      "Bach studied Vivaldi, every human artist remixes priors. The honest test " +
      "is whether outputs combine influences in ways the training set never " +
      "instantiated, and modern systems clearly pass it. AlphaGo's Move 37 was " +
      "statistically improbable, yet professionals called it creative.";
    const chunks = splitIntoChunks(text, 28);
    expect(chunks.length).toBeGreaterThanOrEqual(2);
    expect(chunks.length).toBeLessThanOrEqual(5);
    // No chunk should be empty.
    for (const c of chunks) expect(c.length).toBeGreaterThan(0);
    // Concatenation should equal the original (modulo whitespace).
    expect(chunks.join(" ").replace(/\s+/g, " ").trim()).toBe(
      text.replace(/\s+/g, " ").trim(),
    );
  });

  it("each chunk respects maxWords as a soft cap (a single long sentence still becomes one chunk)", () => {
    const text =
      "This is one extremely long sentence that has many many words and " +
      "definitely exceeds the soft cap of twenty-eight words on its own " +
      "without any internal punctuation to split on at all here.";
    const chunks = splitIntoChunks(text, 28);
    expect(chunks).toEqual([text]);
  });

  it("preserves terminal punctuation on each chunk", () => {
    const text = "First sentence here. Second one is short. Third closes it.";
    const chunks = splitIntoChunks(text, 28);
    for (const c of chunks) expect(c.trim()).toMatch(/[.!?]$/);
  });

  it("preserves decimal points inside numbers (regression: '0.002%' -> '0002%')", () => {
    const text = "0.002% measures verbatim pixel matches, not stylistic borrowing.";
    const chunks = splitIntoChunks(text, 50);
    expect(chunks.join(" ")).toContain("0.002%");
  });

  it("preserves decimals across multiple sentences", () => {
    const text = "Somepalli 2023 found 0.002% verbatim matches. But 3.14 is pi.";
    const chunks = splitIntoChunks(text, 50);
    const joined = chunks.join(" ");
    expect(joined).toContain("0.002%");
    expect(joined).toContain("3.14");
  });
});
