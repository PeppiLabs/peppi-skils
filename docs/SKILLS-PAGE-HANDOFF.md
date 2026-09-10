# peppilabs.net/skills — build handoff

**For:** whoever builds the page. **From:** Peppi Labs. **Date:** 2026-09-10.
**Stack assumption:** the peppilabs.net site is Next.js (App Router). Nothing
below requires it, but the mechanics section is written for it.

## 1. What we are building

A public page at `https://www.peppilabs.net/skills` that lists the skills Peppi
Labs publishes for Claude Code (and any other Agent-Skills-compatible client),
lets a visitor understand what a skill is in one screen, copy the install
commands, and read each skill's details. Plus one detail page per skill at
`/skills/<name>`.

It is modelled on how Anthropic presents skills. We studied five surfaces —
`github.com/anthropics/skills`, `agentskills.io`, the Claude Code skills docs,
the plugin-marketplace docs, and `claude.com/plugins` — and copied the
structure that works at our size, and deliberately not the parts that only
work at theirs (see §7).

## 2. Source of truth — never hand-maintain skill data

Everything the page shows about a skill comes from one GitHub repository:

```
https://github.com/PeppiLabs/peppi-skils
```

| What the page needs | Where it lives in the repo |
|---|---|
| List of skills, category, version, keywords, install name | `.claude-plugin/marketplace.json` → `plugins[]` |
| Description, publisher, copyright, version | `skills/<name>/SKILL.md` YAML frontmatter |
| What the skill ships (scripts / references / assets) | directory listing of `skills/<name>/` |
| Licence text | `skills/<name>/LICENSE.txt` |
| Last updated | last commit touching `skills/<name>/` |
| Authoring guide + template | `TEMPLATE/AUTHORING.md`, `TEMPLATE/SKILL.md` |

If a fact is not in the repo, the page does not show it. Adding a skill to the
repo must be the only step needed to make it appear on the page.

> **Blocker to resolve before build:** the repo is currently **private**. A
> private repo means (a) the page cannot fetch from `raw.githubusercontent.com`
> without a token, and (b) more importantly, nobody can run the install
> command. The page only makes sense once the repo is public. Decision for
> Peppi Labs, not the developer.

## 3. Page anatomy, top to bottom

Copy the strings exactly; they were written to match the repo README and the
Peppi Labs site voice.

### 3.1 Header

- H1: **Skills**
- Sub: *Claude Code skills published by Peppi Labs. Each one was written from
  real work, including the failures.*

### 3.2 What a skill is (one screen — this is agentskills.io's pattern)

- H2: **What is a skill?**
- Body: *A skill is a folder with a `SKILL.md` file: a short description of
  what it does and when to use it, followed by instructions. When you ask
  Claude for something that matches the description, Claude reads the
  instructions and follows them. Skills can also carry scripts and reference
  files.*
- Then the folder diagram, monospace:

```
<skill-name>/
├── SKILL.md        what it does, when to use it, how
├── LICENSE.txt
├── references/     long material, read only when needed
├── scripts/        tools the skill runs
└── assets/         files it copies into your project
```

- Three-step strip (from agentskills.io "How do Agent Skills work"):
  **Discover** — Claude sees each skill's name and description at startup.
  **Activate** — when a request matches, it reads the full instructions.
  **Execute** — it follows them, running any bundled scripts.

### 3.3 Install (shown once, above the list — Anthropic's exact pattern)

- H2: **Install**
- *Add the marketplace once. Then install skills by name.*
- Two code blocks with a copy button each:

```
/plugin marketplace add PeppiLabs/peppi-skils
```
```
/plugin install <skill-name>@peppi-skills
```

- Small print: *Run these inside Claude Code. Installed skills are namespaced
  `/<skill-name>:<skill-name>`; type `/` to see them. To update later:
  `/plugin marketplace update peppi-skills`.*
- Secondary, collapsed by default: **Install by hand** — *Download the repo
  and copy `skills/<name>` into `~/.claude/skills/`.*

### 3.4 The skills (card grid)

One card per entry in `marketplace.json → plugins[]`. Fields, in this order:

| On the card | Source | Notes |
|---|---|---|
| Name | `plugins[].name` | Links to `/skills/<name>` |
| Description | `SKILL.md` frontmatter `description` | **Show it in full.** Anthropic does not, and it is the single most useful thing on the page: it is literally the text Claude reads to decide whether to use the skill. Render as plain text, preserve line breaks, no markdown. ≤1024 chars by spec |
| Install line | `/plugin install <name>@peppi-skills` | With copy button |
| Ships with | directory listing | e.g. `4 scripts · 3 references · 1 asset`. Counts, not filenames |
| Version | `plugins[].version` | small, monospace |
| Updated | git: last commit date under `skills/<name>/` | "Updated 10 Sep 2026" |
| Category | `plugins[].category` | small chip. Do not build category filtering (see §7) |
| Licence | only if `plugins[].license` ≠ `Apache-2.0` | Default is stated once at page bottom, so the chip appears only for exceptions |

### 3.5 Skill detail page — `/skills/<name>`

- Name, description (as above), install line with copy button.
- **What it ships** — the actual file tree of `skills/<name>/`, two levels deep.
- **How to write one like it** — link to `TEMPLATE/AUTHORING.md` on GitHub.
- **Source** — link to `https://github.com/PeppiLabs/peppi-skils/tree/main/skills/<name>`.
- **Licence** — first line of `LICENSE.txt` (the © line) + "Apache License 2.0"
  + link to the file. Do not render the full licence text on the page.
- Do **not** render the SKILL.md body. It is written for the model, not for
  people, and it changes often. The GitHub link covers anyone who wants it.

### 3.6 Write your own

- H2: **Write your own**
- *Every skill here has the same shape. Start from the template and follow
  the checklist.* → links to `TEMPLATE/SKILL.md` and `TEMPLATE/AUTHORING.md`.
- One sentence pointing at the spec: *Frontmatter follows the Agent Skills
  specification* → `https://agentskills.io/specification`.

### 3.7 Disclaimer + licence (page bottom)

- *These skills are provided as-is. Test them in your own environment before
  relying on them for a real submission.* (Anthropic's repo carries the same
  disclaimer; keep it.)
- *Apache License 2.0 unless a skill says otherwise. © 2026 Peppi Labs.*
- Site footer as everywhere else: `© 2026 Peppi Labs. All rights reserved.`

## 4. Data contract (what to parse, exactly)

**`marketplace.json`** — JSON. Use `plugins[]`. Each entry: `name` (the install
slug, kebab-case, immutable), `description`, `version`, `category`,
`keywords[]`, `license`, `skills[]` (paths like `./skills/launchkit`). The
skill folder is `skills[0]` — one skill per plugin by convention here.

**`SKILL.md`** — YAML frontmatter between the first two `---` lines, then a
markdown body you will not render. Fields you use: `name`, `description`,
`license`, `metadata.publisher`, `metadata.publisher-url`,
`metadata.copyright`, `metadata.version`. Parse with `gray-matter` (or any YAML
frontmatter parser). `description` may be a quoted multi-sentence string; keep
it as one paragraph. Everything in `metadata` is a string.

**`LICENSE.txt`** — plain text. Line 1 is `<name> — a Peppi Labs skill`, line
4 is the © line. Show line 4 only.

**Directory listing** — GitHub contents API:
`GET https://api.github.com/repos/PeppiLabs/peppi-skils/contents/skills/<name>`
(then one call per subfolder for counts). Unauthenticated limit is 60
requests/hour per IP; that is fine at build time with a handful of skills, but
send a token from an env var (`GITHUB_TOKEN`, read-only) so builds never fail
on the limit.

**Last updated** —
`GET /repos/PeppiLabs/peppi-skils/commits?path=skills/<name>&per_page=1` →
`commit.committer.date`.

## 5. Mechanics (Next.js)

- **Fetch at build time, revalidate on a timer.** `export const revalidate = 3600`
  on `/skills` and `/skills/[name]`. Skills change rarely; an hour is plenty.
- **On-demand revalidate on push.** Add `app/api/revalidate/route.ts` that
  checks a shared secret and calls `revalidatePath('/skills')`. Wire a GitHub
  webhook on the repo (push events) to it. Then a merged change is live in
  seconds, not an hour.
- **Fail safe.** Commit a snapshot `data/skills.snapshot.json` produced by the
  same fetch code. If GitHub is unreachable at build, render from the snapshot
  and log a warning. The page must never 500 because GitHub had a bad minute.
- **Copy buttons** on every command block; `navigator.clipboard.writeText`,
  with a 1.5s "Copied" state. No third-party library needed.
- **Static params** for `/skills/[name]` from `plugins[].name`;
  `dynamicParams = false` so unknown names 404 cleanly.
- **Design:** reuse the site's existing typography and components. This page
  should feel like the rest of peppilabs.net, not like GitHub. Code blocks in
  the site's monospace, cards in the site's card style.
- **No client-side data fetching** for the listing. Everything arrives
  server-rendered so the page is indexable and fast.

## 6. Acceptance checklist

- [ ] Adding a new folder under `skills/` and an entry in `marketplace.json`,
      then pushing, makes a new card appear with no site code change.
- [ ] Every card shows the full `description` from that skill's `SKILL.md`,
      verbatim.
- [ ] Both install commands copy correctly and match the README in the repo.
- [ ] `/skills/launchkit` shows the file tree with `references/`, `scripts/`,
      `assets/`, and links to the folder on GitHub.
- [ ] The © line on the detail page reads `© 2026 Peppi Labs. All rights reserved.`
- [ ] With network to GitHub blocked, `next build` still succeeds from the snapshot.
- [ ] Pushing to the repo triggers `/api/revalidate` and the page updates
      within a minute.
- [ ] Lighthouse: no client JS required to read the page; copy buttons are
      progressive enhancement.

## 7. Deliberately not building (Anthropic does these; we should not yet)

- **Install counts and "verified" badges** — need telemetry and a trust
  authority we do not have.
- **Search and filters** — pointless under ~8 skills. Revisit at 10.
- **Category navigation** — same. `claude.com/plugins` itself has none.
- **A submission pipeline** for third-party skills — a review process, not a
  web feature.
- **Context-cost / last-used stats** — those are computed inside Claude Code.
- **Rendering the SKILL.md body** — written for the model; link to it instead.
- **Multi-skill bundles** — we publish one plugin per skill precisely so each
  card gets its own install line. Keep it that way.

## 8. Open decisions for Peppi Labs (not the developer)

1. **Make the repo public.** Nothing on this page works while it is private.
2. **Repo name.** It is `peppi-skils` (one *l*). It appears in every install
   command and URL. If that is unintended, rename it on GitHub *before* the
   page ships — GitHub redirects the old name, but the commands people copy
   will not update themselves.
3. **Marketplace name** is `peppi-skills` (two *l*s). It is the part after
   `@` in the install command. Decide whether the repo and marketplace names
   should match; today they do not.
4. **URL** — `/skills` assumed. Confirm.

## 9. Reference: what we copied from Anthropic, and where

| Element | Copied from |
|---|---|
| One-screen "what is a skill" + folder diagram + three-step strip | agentskills.io home |
| Marketplace-once + install-per-plugin command pattern | anthropics/skills README, Claude Code plugin docs |
| One plugin per skill via `strict: false` + `skills: []` | anthropics/skills `.claude-plugin/marketplace.json` |
| Per-skill `LICENSE.txt` + one-line `license:` in frontmatter, © kept out of SKILL.md body | anthropics/skills (docx, frontend-design) |
| Disclaimer wording | anthropics/skills README |
| `template/SKILL.md` as the starting point for authors | anthropics/skills `template/` |
| Showing `description` on the card | our addition — Anthropic's README shows none |
