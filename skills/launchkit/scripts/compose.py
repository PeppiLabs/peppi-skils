#!/usr/bin/env python3
"""Compose raw captures into exact-size, flat, store-ready screenshots.

Two jobs, both about not shipping a broken kit:

1. Put an optional caption bar above the shot and scale the shot beneath it.
2. Guarantee the output is EXACTLY the target slot size, in opaque RGB.

The guarantee is the point. Store consoles reject on exact dimensions, and the
expensive failure is a silent rescale that nobody notices until upload. So a
raw capture whose size doesn't match the expected native size is a hard error
here, not something to quietly fix -- a wrong input size almost always means
the wrong simulator was booted, and you want to know that immediately.

Requires Pillow (pip install Pillow).
"""
from __future__ import annotations

import argparse
import json
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


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


def parse_size(text: str) -> tuple[int, int]:
    try:
        w, h = text.lower().split("x")
        return int(w), int(h)
    except ValueError:
        raise argparse.ArgumentTypeError(f"size must look like 1320x2868, got {text!r}")


def wrap(draw, text, font, max_width):
    words, lines, cur = text.split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def compose_one(src, target, caption, bg, fg, caption_ratio, pad_mode):
    tw, th = target
    shot = Image.open(src).convert("RGB")
    canvas = Image.new("RGB", target, bg)

    if caption:
        cap_h = int(th * caption_ratio)
        font = load_font(max(24, int(cap_h * 0.20)))
        draw = ImageDraw.Draw(canvas)
        margin = int(tw * 0.08)
        lines = wrap(draw, caption, font, tw - 2 * margin)
        try:
            ascent, descent = font.getmetrics()
            line_h = int((ascent + descent) * 1.22)
        except AttributeError:
            line_h = int(cap_h * 0.26)
        block_h = line_h * len(lines)
        y = max(int(cap_h * 0.12), (cap_h - block_h) // 2)
        for line in lines:
            w = draw.textlength(line, font=font)
            draw.text(((tw - w) / 2, y), line, font=font, fill=fg)
            y += line_h
    else:
        cap_h = 0

    avail_h = th - cap_h
    scale = min(tw / shot.width, avail_h / shot.height) if pad_mode == "fit" else tw / shot.width
    new = shot.resize((max(1, round(shot.width * scale)), max(1, round(shot.height * scale))), Image.LANCZOS)
    canvas.paste(new, ((tw - new.width) // 2, cap_h + max(0, (avail_h - new.height) // 2)))

    if canvas.size != target:  # belt and braces; paste cannot change it, but assert anyway
        raise RuntimeError(f"composed size {canvas.size} != target {target}")
    return canvas


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--in", dest="src", required=True, help="directory of raw captures (sorted by name)")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--size", required=True, type=parse_size, help="exact target, e.g. 1320x2868")
    p.add_argument("--captions", help="JSON: list of strings, or {\"01\": \"caption\"}")
    p.add_argument("--bg", default="#000000", help="caption bar / letterbox colour")
    p.add_argument("--fg", default="#FFFFFF", help="caption text colour")
    p.add_argument("--caption-ratio", type=float, default=0.15, help="caption bar height as a fraction (default 0.15)")
    p.add_argument("--pad-mode", choices=["fit", "fill"], default="fit",
                   help="fit = letterbox whole shot (Android 9:16 safe); fill = match width, may crop")
    p.add_argument("--expect-raw", type=parse_size,
                   help="assert every raw capture is this size; a mismatch means the wrong device was booted")
    args = p.parse_args()

    src_dir, out_dir = Path(args.src), Path(args.out)
    if not src_dir.is_dir():
        return print(f"error: {src_dir} is not a directory", file=sys.stderr) or 1
    shots = sorted([q for q in src_dir.iterdir() if q.suffix.lower() in {".png", ".jpg", ".jpeg"}])
    if not shots:
        return print(f"error: no images in {src_dir}", file=sys.stderr) or 1

    captions: dict[str, str] = {}
    if args.captions:
        data = json.loads(Path(args.captions).read_text())
        if isinstance(data, list):
            captions = {f"{i + 1:02d}": c for i, c in enumerate(data)}
        else:
            captions = {str(k).zfill(2): v for k, v in data.items()}

    if args.expect_raw:
        bad = []
        for s in shots:
            with Image.open(s) as im:
                if im.size != args.expect_raw:
                    bad.append(f"  {s.name}: {im.size[0]}x{im.size[1]}")
        if bad:
            print(f"error: raw captures are not {args.expect_raw[0]}x{args.expect_raw[1]} "
                  f"-- wrong simulator device?", file=sys.stderr)
            print("\n".join(bad), file=sys.stderr)
            return 1

    out_dir.mkdir(parents=True, exist_ok=True)
    for i, s in enumerate(shots, start=1):
        key = f"{i:02d}"
        img = compose_one(s, args.size, captions.get(key, ""), args.bg, args.fg,
                          args.caption_ratio, args.pad_mode)
        dest = out_dir / f"{key}.png"
        img.save(dest, "PNG")  # RGB mode already, so no alpha channel is written
        print(f"  {dest}  {img.width}x{img.height}"
              + (f'  "{captions[key]}"' if key in captions else ""))

    print(f"\n{len(shots)} composed into {out_dir} at {args.size[0]}x{args.size[1]}, opaque RGB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
