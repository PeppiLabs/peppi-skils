#!/usr/bin/env python3
"""Check a skill folder against the Agent Skills spec + the Peppi Labs format."""
import re, sys, pathlib

REQ_META = {"publisher": "Peppi Labs", "publisher-url": "https://www.peppilabs.net"}

def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m: return None
    fm, cur = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z_-]+:", line):
            k, _, v = line.partition(":"); cur = k.strip(); fm[cur] = v.strip().strip('"')
        elif line.startswith("  ") and cur == "metadata":
            k, _, v = line.strip().partition(":"); fm.setdefault("_meta", {})[k.strip()] = v.strip().strip('"')
    return fm

def main(path):
    p = pathlib.Path(path); errs = []
    sk = p / "SKILL.md"; lic = p / "LICENSE.txt"
    if not sk.exists(): return [f"missing {sk}"]
    fm = frontmatter(sk.read_text())
    if fm is None: return ["no YAML frontmatter"]
    name = fm.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or not (1 <= len(name) <= 64):
        errs.append(f"name '{name}' violates spec (lowercase a-z0-9, single hyphens, 1-64 chars)")
    if name != p.name: errs.append(f"name '{name}' != folder '{p.name}'")
    d = fm.get("description", "")
    if not (1 <= len(d) <= 1024): errs.append(f"description length {len(d)} not in 1..1024")
    if "license" not in fm: errs.append("missing license: field")
    if not lic.exists(): errs.append("missing LICENSE.txt")
    elif "Peppi Labs" not in lic.read_text(): errs.append("LICENSE.txt lacks Peppi Labs notice")
    meta = fm.get("_meta", {})
    for k, v in REQ_META.items():
        if meta.get(k) != v: errs.append(f"metadata.{k} should be '{v}', got '{meta.get(k)}'")
    if not re.fullmatch(r"\d+\.\d+\.\d+", meta.get("version", "")): errs.append("metadata.version must be semver x.y.z")
    if "©" not in meta.get("copyright", ""): errs.append("metadata.copyright missing © notice")
    body = sk.read_text().split("\n---\n", 1)[-1]
    if re.search(r"©|all rights reserved", body, re.I): errs.append("copyright text found in SKILL.md body — move it to LICENSE.txt")
    extra = set(fm) - {"name","description","license","compatibility","metadata","allowed-tools","_meta"}
    if extra: errs.append(f"non-spec frontmatter fields: {sorted(extra)} (put them under metadata)")
    return errs

if __name__ == "__main__":
    bad = 0
    for arg in sys.argv[1:] or ["."]:
        e = main(arg)
        print(f"{'FAIL' if e else 'OK  '} {arg}"); [print("   -", x) for x in e]; bad += bool(e)
    sys.exit(1 if bad else 0)
