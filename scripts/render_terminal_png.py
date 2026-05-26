"""Render a plain-text file as a terminal-style PNG.

Used to generate visual screenshots from captured CLI output for the README
and for the H22 manual-Phase-1 evidence. Renders a dark-mode 'terminal' frame
with monospaced text. Pure-Python; no headless browser.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = (24, 26, 30)
FG = (220, 220, 220)
TITLE_BG = (50, 52, 58)
TITLE_FG = (180, 180, 180)
PADDING = 18
LINE_HEIGHT = 18
CHAR_WIDTH = 8


def _load_font() -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.dfont",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, 14)
    return ImageFont.load_default()


def _wrap_lines(text: str, max_chars: int = 90) -> list[str]:
    out: list[str] = []
    for raw in text.splitlines() or [""]:
        if len(raw) <= max_chars:
            out.append(raw)
            continue
        words = raw.split(" ")
        cur = ""
        for w in words:
            if len(cur) + 1 + len(w) > max_chars:
                out.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur:
            out.append(cur)
    return out


def render(input_text: Path, output_png: Path, title: str) -> None:
    text = input_text.read_text(encoding="utf-8")
    lines = _wrap_lines(text, max_chars=90)
    width = max(len(line) for line in lines) * CHAR_WIDTH + PADDING * 2
    width = max(width, 800)
    height = len(lines) * LINE_HEIGHT + PADDING * 2 + 28
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 28), fill=TITLE_BG)
    for i, (color, x) in enumerate([((255, 95, 86), 14), ((255, 189, 46), 32), ((39, 201, 63), 50)]):
        draw.ellipse((x, 8, x + 12, 20), fill=color)
        del i
    font = _load_font()
    draw.text((width // 2 - len(title) * 3, 7), title, fill=TITLE_FG, font=font)
    for idx, line in enumerate(lines):
        draw.text((PADDING, 28 + PADDING + idx * LINE_HEIGHT), line, fill=FG, font=font)
    img.save(output_png)
    print(f"wrote {output_png} ({width}x{height})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage: render_terminal_png.py INPUT.txt OUTPUT.png [TITLE]")
        sys.exit(2)
    render(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "terminal")
