"""Compose two terminal PNGs side-by-side, mimicking the lecturer's
two-terminal manual-Phase-1 evidence pattern (lec05 L1896-1909).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

GAP = 24
LABEL_HEIGHT = 36
BG = (24, 26, 30)
LABEL_FG = (220, 220, 220)


def main() -> None:
    if len(sys.argv) < 4:
        print("usage: compose_side_by_side.py LEFT.png RIGHT.png OUTPUT.png [LABEL]")
        sys.exit(2)
    left = Image.open(sys.argv[1])
    right = Image.open(sys.argv[2])
    out_path = Path(sys.argv[3])
    label = sys.argv[4] if len(sys.argv) > 4 else "Manual Phase 1 — two-terminal debate"

    h = max(left.height, right.height)
    w = left.width + right.width + GAP
    canvas = Image.new("RGB", (w, h + LABEL_HEIGHT), BG)
    draw = ImageDraw.Draw(canvas)

    font_path = "/System/Library/Fonts/Menlo.ttc"
    if Path(font_path).exists():
        font = ImageFont.truetype(font_path, 16)
    else:
        font = ImageFont.load_default()

    draw.text((20, 10), label, fill=LABEL_FG, font=font)
    canvas.paste(left, (0, LABEL_HEIGHT))
    canvas.paste(right, (left.width + GAP, LABEL_HEIGHT))
    canvas.save(out_path)
    print(f"wrote {out_path} ({w}x{h + LABEL_HEIGHT})")


if __name__ == "__main__":
    main()
