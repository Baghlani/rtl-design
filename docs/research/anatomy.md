# Research: Agent Skills Standard & Prior-Art Dissection

> Verified 2026-07-25 via agentskills.io spec, GitHub API, and shallow clones of each repo.
> Purpose: understand the form factor deeply before writing a line of SKILL.md, and document
> exactly what we learn from prior art (structure only — never content).

## 1. The Agent Skills standard — what actually matters

Source of truth: https://agentskills.io/specification.md (spec repo: `agentskills/agentskills`,
Apache-2.0 code / CC-BY-4.0 docs).

### Anatomy

A skill = a directory with a `SKILL.md` (YAML frontmatter + Markdown body) plus optional
`references/`, `scripts/`, `assets/`.

Frontmatter fields:

| Field | Req | Rules |
|---|---|---|
| `name` | yes | ≤64 chars, `a-z0-9-`, no leading/trailing/double hyphen, **must equal the directory name** |
| `description` | yes | ≤1024 chars; what it does + when to use it + trigger keywords |
| `license` | no | short name or pointer to bundled file (spec example: `Apache-2.0`) |
| `compatibility` | no | ≤500 chars; most skills don't need it |
| `metadata` | no | free string map |
| `allowed-tools` | no | experimental; pre-approved tools (impeccable uses it to pre-authorize its scripts) |

### Progressive disclosure (the 3 tiers)

| Tier | What loads | When | Budget |
|---|---|---|---|
| 1 Catalog | name + description | every session, all skills | ~50–100 tokens |
| 2 Instructions | full SKILL.md body | on activation | **<5000 tokens, <500 lines (spec hard guidance)** |
| 3 Resources | references/, scripts/, assets/ | only when body points to them | as needed |

Key authoring rules from the spec/best-practices:
- References one level deep; give **explicit load triggers**: "Read `references/flutter.md` when the project is Flutter" beats "see references/".
- The description carries the entire triggering burden. Official style: imperative ("Use when…"),
  user-intent keywords, "err on the side of being pushy", explicit negative scope allowed.
- Scripts: non-interactive (hard requirement), `--help`, JSON on stdout / diagnostics on stderr,
  meaningful exit codes, bounded output, self-contained deps (PEP 723 / stdlib-only).
- Validation: `skills-ref validate ./skill-dir` (official reference tool) — run in CI.

### Distribution (ecosystem, not spec)

- `npx skills add owner/repo` (Vercel, skills.sh) — registry is just GitHub. Conventional
  multi-skill layout: `skills/<skill-name>/SKILL.md` (same as anthropics/skills). Installs to
  `.claude/skills/` for Claude Code, `.agents/skills/` for most others; 75+ agents supported.
- Claude plugin marketplace via `.claude-plugin/marketplace.json` is a second channel.
- **Decision for us: lay out the repo as `skills/<name>/SKILL.md` from day one** — discoverable by
  `npx skills add`, leaves room for sibling skills later.

## 2. Prior-art dissection (structure only)

| Repo | Stars | License | Flagship body | references/ | Scripts | RTL coverage |
|---|---|---|---|---|---|---|
| Leonxlnx/taste-skill | 67k | MIT | 1,206 ln / ~17k tok monolith | none (13 sibling variants) | no | **none** |
| nextlevelbuilder/ui-ux-pro-max-skill | 110k | MIT | 196 ln / ~2.3k tok router | 2 md + 35 CSVs (1.6 MB) | stdlib-Python search | 2 incidental font rows; no guidance, no Persian |
| pbakaus/impeccable | 50k | Apache-2.0 + NOTICE.md | 85 ln / ~1.8k tok dispatcher | 34–40 md, per-command | 58 no-LLM detector rules, hooks, CLI | one subsection in harden.md (Arabic/Hebrew edge case); **no Persian** |
| anthropics/skills frontend-design | official | Apache-2.0 | 55 ln prose | none | no | none |

### What each teaches us (form, not content)

- **taste-skill**: virality is personality-driven; but the 17k-token monolith is the anti-pattern
  our token-lean positioning sells against. Its "dials" idea (user-tunable intensity at top of
  file) is a genuinely good UX pattern.
- **ui-ux-pro-max**: the "zero-token database" pattern — 1.6 MB of CSV knowledge, ~2.3k tokens
  loaded, queried via a stdlib-only Python script invoked by path from the body. Body is a
  router that teaches *how to query*, not the knowledge itself.
- **impeccable**: the gold-standard form factor — 85-line dispatcher body, per-command
  references, deterministic detector (58 rules, "no LLM, no API key"), `allowed-tools`
  pre-authorization, PostToolUse/Stop hooks. Also the **prior-art crediting precedent**: it is
  openly derived from Anthropic's frontend-design, Apache-2.0 with a NOTICE.md crediting the
  origin. This is the ecosystem norm we follow.
- **anthropics/canvas-design**: bundles ~40 TTF fonts in-repo — official precedent that bundling
  OFL fonts inside a skill is acceptable (we still choose not to, to stay lean; we link instead).

### Market gap — verified

Across ~226k combined stars of design skills: total RTL content is **one checklist subsection**
(impeccable harden.md, Arabic/Hebrew as edge case) and **two CSV font rows** (ui-ux-pro-max).
Persian/Farsi: **zero mentions anywhere**. RTL is only ever framed as an edge case to survive,
never as a first-class design context. The gap claimed in BRIEF.md is real and bigger than stated.

## 3. Form-factor decisions this research locks

1. Repo layout: `skills/<name>/SKILL.md` + `references/` + `scripts/` + `docs/` (research, not shipped).
2. Body: dispatcher style, target <150 lines / <2k tokens — leaner than impeccable is the flex.
3. Description: impeccable-style trigger wall including Persian keywords (RTL, Persian, Farsi,
   Arabic, Hebrew, bidi, Jalali, فارسی, راست‌به‌چپ …) + negative scope.
4. Detector: stdlib-only Python, non-interactive, JSON stdout, exit codes; wired with explicit
   invocation commands in the body ("zero-token" selling point, impeccable-proven).
5. License: **Apache-2.0 + NOTICE.md** (matches spec example, Anthropic skills, and impeccable's
   crediting pattern; NOTICE.md names our structural inspirations explicitly).
6. Validate with `skills-ref validate` in CI before every release.

## 4. Anti-leak rule (personal workflow)

The skill ships **domain knowledge only**: RTL/Persian design rules. Nothing personal ever enters
`skills/`: no client names, repo paths, working conventions, decision rituals, or session habits.
Final pre-publish review includes a dedicated leak pass over every shipped file.
