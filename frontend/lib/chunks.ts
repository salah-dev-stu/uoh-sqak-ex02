// Split a Pro/Con turn into sentence-bundled chunks so the stage cycles
// through 3-4 smaller bubbles per turn instead of one large block of text.
// Sentences are bundled greedily until the running word count would exceed
// `maxWords`, so very short sentences ride with the next one and very long
// sentences become their own chunk. Returns the original text as a single
// chunk when no sentence boundaries are found.

const SENT_RE = /[^.!?]+[.!?]+(?=\s|$)/g;

export function splitIntoChunks(text: string, maxWords = 28): string[] {
  const trimmed = text.trim();
  if (!trimmed) return [];
  const sentences = trimmed.match(SENT_RE)?.map((s) => s.trim()).filter(Boolean) ?? [];
  if (sentences.length === 0) return [trimmed];

  const chunks: string[] = [];
  let current = "";
  let count = 0;
  for (const sentence of sentences) {
    const w = sentence.split(/\s+/).length;
    if (current && count + w > maxWords) {
      chunks.push(current);
      current = sentence;
      count = w;
    } else {
      current = current ? `${current} ${sentence}` : sentence;
      count += w;
    }
  }
  if (current) chunks.push(current);
  return chunks.length > 0 ? chunks : [trimmed];
}
