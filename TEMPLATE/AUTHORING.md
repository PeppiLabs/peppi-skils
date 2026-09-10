# Writing a Peppi Labs skill

Copy this folder to `skills/<skill-name>/`, then:

1. **Rename** the folder. `name` in SKILL.md must equal the folder name:
   lowercase `a-z`, `0-9`, `-` only; 1–64 chars; no leading, trailing or
   double hyphens.
2. **Write `description`** for triggering, not for marketing. It is the only
   text loaded at startup; the body loads only after activation. 1–1024 chars.
3. **Leave `license` and `metadata` as they are.** Bump `metadata.version`
   when behaviour changes. Update the year in `LICENSE.txt` and
   `metadata.copyright` at the first release of a new year.
4. **Keep the copyright notice out of the SKILL.md body.** Once a skill loads,
   every body line is a recurring token cost. The notice lives in
   `LICENSE.txt`, which is never loaded unless something reads it.
5. **Keep the body short.** Long reference material goes in `references/` and
   is pointed at from the reference index. Scripts go in `scripts/`. Anything
   the skill copies into a project goes in `assets/`.
6. **Delete this file** before publishing — or keep it, it is harmless; it is
   not read by the agent.

Frontmatter fields follow the Agent Skills specification
(https://agentskills.io/specification): `name`, `description`, `license`,
`compatibility`, `metadata`, `allowed-tools`. Nothing else is defined; put
extra facts under `metadata`.

Validate before committing:

    python3 scripts/validate.py skills/<skill-name>
