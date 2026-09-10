# Peppi Labs skills

Claude Code skills published by [Peppi Labs](https://www.peppilabs.net). Each
one was written from real work, including the failures, so the sharp edges in
them are ones that actually cost a rebuild rather than ones a doc warned about.

| Skill | What it does |
|---|---|
| [`launchkit`](skills/launchkit) | Builds a folder you drag into the App Store and Google Play consoles without making a single decision: every image already the exact size its slot wants, every text field already in a code block with its character count against the store's limit, and a README mapping each file to the console screen it belongs on. Also covers icons, Play feature graphics, social banners, and Product Hunt assets. |

## Installing

**As a plugin** (updates arrive by pulling the repo):

```
/plugin marketplace add PeppiLabs/peppi-skils
/plugin install peppi-skills@peppi-skills
```

**By hand:** copy the folders under `skills/` into `~/.claude/skills/`.

```bash
cp -R skills/* ~/.claude/skills/
```

## The format

Every skill here has the same shape. `TEMPLATE/` is the starting point and
`TEMPLATE/AUTHORING.md` is the checklist.

```
skills/<name>/
├── SKILL.md        frontmatter: name, description, license, metadata — then the body
├── LICENSE.txt     the copyright notice and the licence terms
├── references/     long material the body points at, loaded only when needed
├── scripts/        tools the skill runs
└── assets/         files the skill copies into a project
```

The copyright notice lives in `LICENSE.txt`, not in `SKILL.md`: once a skill
activates, its whole body sits in the model's context for the rest of the
session, so the notice would be a recurring cost for no benefit. Frontmatter
follows the [Agent Skills specification](https://agentskills.io/specification).

Validate a skill before committing it:

```bash
python3 scripts/validate.py skills/launchkit
```

## Licence

Apache License 2.0. © 2026 Peppi Labs. See [LICENSE](LICENSE) and each
skill's `LICENSE.txt`.
