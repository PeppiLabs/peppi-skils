#!/usr/bin/env python3
"""Verify a launch kit before anyone opens a store console.

Every check here maps to a real console rejection: wrong pixel dimensions, an
alpha channel where the slot forbids one, a file over the size ceiling, or a
required asset simply missing. Consoles surface these one at a time, minutes
apart, after you have already started uploading. Checking locally takes about a
second and finds all of them at once.

Usage:
    python3 verify_kit.py kit/
    python3 verify_kit.py kit/ --manifest kit/manifest.json
    python3 verify_kit.py --write-manifest kit/manifest.json

Without a manifest the script infers the expected spec from each file's path
using the naming convention in the skill's output shape (app-store-iphone/,
play-store-feature.png, social/x-banner.png, ...). A manifest makes the contract
explicit and is worth writing for a kit you will regenerate.

Requires Pillow (pip install Pillow).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required:  python3 -m pip install Pillow")

# name fragment -> (accepted sizes, alpha allowed, max bytes or None)
# Multiple accepted sizes exist because consoles differ by record age; any one
# of them passes, but every file in a single folder should agree with the others.
RULES: list[tuple[str, list[tuple[int, int]], bool, int | None]] = [
    ("app-store-iphone",   [(1320, 2868), (1290, 2796), (1260, 2736), (1284, 2778), (1242, 2688)], False, None),
    ("app-store-ipad",     [(2064, 2752), (2048, 2732)], False, None),
    ("app-store-icon",     [(1024, 1024)], False, None),
    ("play-store-phone",   [(1080, 1920), (1080, 2160)], False, 8 * 1024 * 1024),
    ("play-store-tablet",  [(1200, 1920), (1600, 2560)], False, 8 * 1024 * 1024),
    ("play-store-feature", [(1024, 500)], False, None),
    ("play-store-icon",    [(512, 512)], True, 1024 * 1024),
    ("x-banner",           [(1500, 500)], True, None),
    ("linkedin-company",   [(1128, 191)], True, None),
    ("linkedin-personal",  [(1584, 396)], True, None),
    ("og-image",           [(1200, 630)], True, None),
    ("gallery",            [(1270, 760)], True, None),
    ("thumbnail",          [(240, 240)], True, None),
]

# Folders holding a numbered screenshot sequence, where every file must be the
# same size. Icons, feature graphics, social and Product Hunt assets live
# alongside each other at deliberately different sizes, so they're excluded.
SCREENSHOT_SLOTS = ("app-store-iphone", "app-store-ipad", "play-store-phone", "play-store-tablet")


def rule_for(path: Path):
    key = str(path).replace("\\", "/").lower()
    # Longest fragment wins so "play-store-icon" beats a hypothetical "icon".
    matches = [r for r in RULES if r[0] in key]
    return max(matches, key=lambda r: len(r[0])) if matches else None


def check(path: Path, sizes, alpha_ok, max_bytes) -> list[str]:
    problems = []
    try:
        with Image.open(path) as im:
            size, mode = im.size, im.mode
            has_alpha = mode in ("RGBA", "LA", "PA") or "transparency" in im.info
    except Exception as exc:  # noqa: BLE001 - report unreadable files rather than crashing
        return [f"unreadable ({exc})"]

    if sizes and size not in sizes:
        want = " or ".join(f"{w}x{h}" for w, h in sizes)
        problems.append(f"is {size[0]}x{size[1]}, slot wants {want}")
    if has_alpha and not alpha_ok:
        problems.append("has an alpha channel; this slot needs flat opaque RGB")
    if max_bytes:
        n = path.stat().st_size
        if n > max_bytes:
            problems.append(f"is {n / 1024 / 1024:.1f}MB, over the {max_bytes / 1024 / 1024:.0f}MB ceiling")
    return problems


def iter_images(root: Path):
    return sorted(p for p in root.rglob("*")
                  if p.suffix.lower() in {".png", ".jpg", ".jpeg"} and p.is_file())


def write_manifest(root: Path, dest: Path) -> int:
    entries = []
    for p in iter_images(root):
        with Image.open(p) as im:
            entries.append({
                "path": str(p.relative_to(root)),
                "size": list(im.size),
                "alpha": im.mode in ("RGBA", "LA", "PA"),
            })
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"files": entries}, indent=2) + "\n")
    print(f"wrote {dest} with {len(entries)} entries")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kit", nargs="?", default="kit", help="kit root directory")
    ap.add_argument("--manifest", help="JSON manifest of expected files and sizes")
    ap.add_argument("--write-manifest", metavar="DEST", help="record the current kit as a manifest and exit")
    args = ap.parse_args()

    root = Path(args.kit)
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    if args.write_manifest:
        return write_manifest(root, Path(args.write_manifest))

    failures, checked, unknown = [], 0, []

    if args.manifest:
        manifest = json.loads(Path(args.manifest).read_text())
        for entry in manifest["files"]:
            p = root / entry["path"]
            if not p.exists():
                failures.append(f"{entry['path']}: MISSING")
                continue
            checked += 1
            expect = tuple(entry["size"])
            for problem in check(p, [expect], entry.get("alpha", False), entry.get("max_bytes")):
                failures.append(f"{entry['path']}: {problem}")
    else:
        for p in iter_images(root):
            rule = rule_for(p.relative_to(root))
            if not rule:
                unknown.append(str(p.relative_to(root)))
                continue
            checked += 1
            _, sizes, alpha_ok, max_bytes = rule
            for problem in check(p, sizes, alpha_ok, max_bytes):
                failures.append(f"{p.relative_to(root)}: {problem}")

    # A slot accepts several sizes, but every shot inside one screenshot slot
    # must agree: Apple rejects a display class whose screenshots aren't all the
    # same size. This slips past the per-file checks because each file is
    # individually legal. Only screenshot sequences are checked -- folders like
    # social/ and product-hunt/ hold deliberately different-sized assets.
    screenshot_folders = {
        p.parent for p in iter_images(root)
        if any(frag in str(p.parent).replace("\\", "/").lower() for frag in SCREENSHOT_SLOTS)
    }
    for folder in sorted(screenshot_folders):
        by_size: dict[tuple[int, int], list[str]] = {}
        for p in sorted(folder.glob("*")):
            if p.suffix.lower() not in {".png", ".jpg", ".jpeg"} or not p.is_file():
                continue
            try:
                with Image.open(p) as im:
                    by_size.setdefault(im.size, []).append(p.name)
            except Exception:  # noqa: BLE001 - already reported above
                continue
        if len(by_size) > 1:
            rel = folder.relative_to(root) if folder != root else Path(".")
            detail = "; ".join(f"{w}x{h}: {', '.join(names)}" for (w, h), names in sorted(by_size.items()))
            failures.append(f"{rel}: mixed sizes in one slot ({detail})")

    print(f"checked {checked} image(s) in {root}")
    if unknown:
        print(f"\n{len(unknown)} file(s) matched no known slot (not an error, but unverified):")
        for u in unknown:
            print(f"  ? {u}")

    if failures:
        print(f"\nFAIL - {len(failures)} problem(s):")
        for f in failures:
            print(f"  x {f}")
        print("\nFix these before uploading; consoles reject on exactly this.")
        return 1

    print("\nPASS - every checked asset matches its slot.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
