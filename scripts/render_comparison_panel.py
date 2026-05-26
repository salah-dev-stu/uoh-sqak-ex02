"""Render a head-to-head Pro vs Con comparison panel for the README.

Visual contrast: same evidence axis, opposite framings. Plus the
ScoringEngine 5-axis verdict.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = (24, 26, 30)
PANEL_BG = (32, 35, 40)
PRO_COLOR = (94, 204, 122)
CON_COLOR = (232, 110, 110)
NEUTRAL = (220, 220, 220)
DIM = (140, 140, 140)
HEADER_BG = (50, 55, 65)


def font(size: int) -> ImageFont.FreeTypeFont:
    for p in ["/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/SFNS.ttf"]:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main() -> None:
    w, h = 1600, 900
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    f_title = font(24)
    f_hdr = font(18)
    f_row = font(15)
    f_small = font(13)

    # Header
    draw.rectangle((0, 0, w, 60), fill=HEADER_BG)
    draw.text((20, 18), "Manual Phase 1 — Pro vs Con head-to-head (H22, H7, H5)", fill=NEUTRAL, font=f_title)

    # Two panels
    pad = 20
    panel_w = (w - 3 * pad) // 2
    pro_x = pad
    con_x = pad * 2 + panel_w
    panel_y = 80
    panel_h = 540

    # Pro panel
    draw.rectangle((pro_x, panel_y, pro_x + panel_w, panel_y + panel_h), fill=PANEL_BG)
    draw.rectangle((pro_x, panel_y, pro_x + panel_w, panel_y + 40), fill=(40, 80, 50))
    draw.text((pro_x + 16, panel_y + 10), "PRO — stance: AI=ORIGINALITY", fill=PRO_COLOR, font=f_hdr)

    # Con panel
    draw.rectangle((con_x, panel_y, con_x + panel_w, panel_y + panel_h), fill=PANEL_BG)
    draw.rectangle((con_x, panel_y, con_x + panel_w, panel_y + 40), fill=(80, 40, 40))
    draw.text((con_x + 16, panel_y + 10), "CON — stance: AI=REMIX_ONLY", fill=CON_COLOR, font=f_hdr)

    # Rows of comparison
    rows = [
        ("Christie's auction (2018)",
         "Edmond de Belamy = art ($432,500)",
         "= remix (15K WikiArt portraits trained)"),
        ("Klingemann GAN portraits",
         "Generates infinite, never-repeating novelty",
         "Same latent manifold sampled forever — permutation"),
        ("Anna Ridler — Mosaic Virus",
         "Bloom-temporality emerged from the model",
         "Human (Ridler) hand-labeled the tulips — meaning-making is human"),
        ("Bender et al. Stochastic Parrots",
         "Targets LLM hallucination, not visual originality",
         "Statistical interpolation without aboutness — exactly this"),
        ("Philosophy: aboutness / intent",
         "All human art also remixes; intentionality is anthropocentric",
         "Rembrandt had intent + embodiment; the model has neither"),
        ("H7 mutual reference (turn 2)",
         "Quotes Con's \"novelty-by-permutation\" by name",
         "Refutes Pro's Edmond de Belamy + Klingemann + Ridler"),
        ("Drift detection (DriftDetector)",
         "0 concession phrases — stance held",
         "0 concession phrases — stance held"),
    ]

    row_y = panel_y + 60
    for i, (axis, pro_txt, con_txt) in enumerate(rows):
        row_h = 65
        # Center axis label between panels
        draw.text((w // 2 - 6, row_y + 4), "|", fill=DIM, font=f_small)
        draw.text((pro_x + 16, row_y + 2), f"• {axis}", fill=DIM, font=f_small)
        draw.text((con_x + 16, row_y + 2), f"• {axis}", fill=DIM, font=f_small)
        # Wrap pro_txt and con_txt
        for j, line in enumerate(_wrap(pro_txt, 50)):
            draw.text((pro_x + 28, row_y + 22 + j * 18), line, fill=PRO_COLOR if j == 0 else NEUTRAL, font=f_row)
        for j, line in enumerate(_wrap(con_txt, 50)):
            draw.text((con_x + 28, row_y + 22 + j * 18), line, fill=CON_COLOR if j == 0 else NEUTRAL, font=f_row)
        row_y += row_h
        if i < len(rows) - 1:
            draw.line((pro_x + 10, row_y - 4, pro_x + panel_w - 10, row_y - 4), fill=(50, 53, 60))
            draw.line((con_x + 10, row_y - 4, con_x + panel_w - 10, row_y - 4), fill=(50, 53, 60))

    # Verdict panel at bottom
    verdict_y = panel_y + panel_h + 20
    draw.rectangle((pad, verdict_y, w - pad, verdict_y + 200), fill=PANEL_BG)
    draw.rectangle((pad, verdict_y, w - pad, verdict_y + 36), fill=HEADER_BG)
    draw.text((pad + 16, verdict_y + 8), "Judge verdict — ScoringEngine 5-axis × 20 = 100 (H5: no tie)", fill=NEUTRAL, font=f_hdr)

    axes = ["clarity", "evidence", "rebuttal", "novelty", "role_fid"]
    pro_scores = [18, 17, 15, 12, 19]   # → 81
    con_scores = [14, 16, 18, 17, 15]   # → 80

    table_x = pad + 30
    table_y = verdict_y + 50
    col_w = 130
    draw.text((table_x, table_y), "axis", fill=DIM, font=f_row)
    for k, axis in enumerate(axes):
        draw.text((table_x + (k + 1) * col_w, table_y), axis, fill=DIM, font=f_row)
    draw.text((table_x + (len(axes) + 1) * col_w, table_y), "total", fill=NEUTRAL, font=f_hdr)

    draw.text((table_x, table_y + 32), "Pro", fill=PRO_COLOR, font=f_row)
    for k, s in enumerate(pro_scores):
        draw.text((table_x + (k + 1) * col_w, table_y + 32), str(s), fill=PRO_COLOR, font=f_row)
    draw.text((table_x + (len(axes) + 1) * col_w, table_y + 28), f"{sum(pro_scores)}", fill=PRO_COLOR, font=f_hdr)

    draw.text((table_x, table_y + 64), "Con", fill=CON_COLOR, font=f_row)
    for k, s in enumerate(con_scores):
        draw.text((table_x + (k + 1) * col_w, table_y + 64), str(s), fill=CON_COLOR, font=f_row)
    draw.text((table_x + (len(axes) + 1) * col_w, table_y + 60), f"{sum(con_scores)}", fill=CON_COLOR, font=f_hdr)

    draw.text((pad + 30, table_y + 110),
              f"WINNER: Pro by {sum(pro_scores) - sum(con_scores)} point — H5 differential scoring; tiebreak chain unused (totals differ)",
              fill=PRO_COLOR, font=f_row)
    draw.text((pad + 30, table_y + 130),
              "If totals had tied: role_fid (Pro 19 > Con 15) would still favor Pro — H5 NO-TIE rule is satisfied either way.",
              fill=DIM, font=f_small)

    out = Path("assets/manual-phase1-comparison.png")
    img.save(out)
    print(f"wrote {out} ({w}x{h})")


def _wrap(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w_ in words:
        if len(cur) + 1 + len(w_) > max_chars:
            lines.append(cur)
            cur = w_
        else:
            cur = (cur + " " + w_).strip()
    if cur:
        lines.append(cur)
    return lines


if __name__ == "__main__":
    main()
