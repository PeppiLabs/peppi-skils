#!/usr/bin/env python3
"""Generate social and Product Hunt banners at exact platform dimensions.

These surfaces crop responsively and unpredictably -- LinkedIn covers in
particular are extreme letterboxes (1128x191) that get overlaid with an avatar.
So everything is composed toward the centre with generous safe margins, and the
logo scales to the banner's height rather than to a fixed pixel size.

Requires Pillow (pip install Pillow).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install Pillow")

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]

# name -> (width, height, headline scale as fraction of height)
SURFACES = {
    "x-banner":          (1500, 500, 0.13),
    "linkedin-company":  (1128, 191, 0.26),
    "linkedin-personal": (1584, 396, 0.16),
    "og-image":          (1200, 630, 0.11),
    "gallery":           (1270, 760, 0.10),
    "thumbnail":         (240, 240, 0.0),   # logo only, no text at this size
}


def load_font(size: int):
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, max(8, size))
            except OSError:
                continue
    return ImageFont.load_default()


def wrap(draw, text, font, max_width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = f"{cur} {w}".strip()
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def build(name, spec, logo_path, headline, subhead, bg, fg, out_dir):
    w, h, head_scale = spec
    canvas = Image.new("RGB", (w, h), bg)
    draw = ImageDraw.Draw(canvas)

    logo = None
    if logo_path and Path(logo_path).exists():
        logo = Image.open(logo_path).convert("RGBA")
        target_h = int(h * (0.55 if name == "thumbnail" else 0.30))
        ratio = target_h / logo.height
        logo = logo.resize((max(1, int(logo.width * ratio)), target_h), Image.LANCZOS)

    if name == "thumbnail":
        if logo:
            canvas.paste(logo, ((w - logo.width) // 2, (h - logo.height) // 2), logo)
        dest = out_dir / f"{name}.png"
        canvas.save(dest, "PNG")
        return dest, canvas.size

    # Measure the stacked block first so the whole composition lands centred.
    margin = int(w * 0.06)
    head_font = load_font(int(h * head_scale))
    sub_font = load_font(int(h * head_scale * 0.52))
    head_lines = wrap(draw, headline, head_font, w - 2 * margin) if headline else []
    sub_lines = wrap(draw, subhead, sub_font, w - 2 * margin) if subhead else []

    head_lh = int(h * head_scale * 1.25)
    sub_lh = int(h * head_scale * 0.52 * 1.35)
    gap = int(h * 0.05)

    block = 0
    if logo:
        block += logo.height + gap
    block += head_lh * len(head_lines)
    if sub_lines:
        block += int(gap * 0.5) + sub_lh * len(sub_lines)

    y = max(int(h * 0.06), (h - block) // 2)

    if logo:
        canvas.paste(logo, ((w - logo.width) // 2, y), logo)
        y += logo.height + gap

    for line in head_lines:
        tw = draw.textlength(line, font=head_font)
        draw.text(((w - tw) / 2, y), line, font=head_font, fill=fg)
        y += head_lh

    if sub_lines:
        y += int(gap * 0.5)
        muted = tuple(int(c * 0.78 + 255 * 0.22) for c in Image.new("RGB", (1, 1), fg).getpixel((0, 0)))
        for line in sub_lines:
            tw = draw.textlength(line, font=sub_font)
            draw.text(((w - tw) / 2, y), line, font=sub_font, fill=muted)
            y += sub_lh

    dest = out_dir / f"{name}.png"
    canvas.save(dest, "PNG")
    return dest, canvas.size


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--logo", help="logo PNG (transparent background works best)")
    ap.add_argument("--headline", default="", help="main line; keep it short, these crop")
    ap.add_argument("--subhead", default="", help="optional second line")
    ap.add_argument("--bg", default="#000000")
    ap.add_argument("--fg", default="#FFFFFF")
    ap.add_argument("--only", nargs="*", choices=sorted(SURFACES), help="subset of surfaces (default: all)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    for name in (args.only or SURFACES):
        dest, size = build(name, SURFACES[name], args.logo, args.headline,
                           args.subhead, args.bg, args.fg, out_dir)
        print(f"  {dest}  {size[0]}x{size[1]}")

    print(f"\nWritten to {out_dir}. LinkedIn and X crop responsively -- open each one "
          f"and check nothing important sits near an edge.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
