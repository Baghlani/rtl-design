# rtl-design

[![ci](https://github.com/Baghlani/rtl-design/actions/workflows/ci.yml/badge.svg)](https://github.com/Baghlani/rtl-design/actions/workflows/ci.yml)

**The first serious RTL/Persian UI design skill for AI coding agents.**
Works in Claude Code, Cursor, Codex CLI, Gemini CLI, and 70+ other agents via the
[Agent Skills](https://agentskills.io) open standard.

> 500M+ people read right-to-left. Across the most popular design skills (~226k
> combined GitHub stars), the sum total of RTL guidance is one checklist subsection —
> and the word *Persian* appears exactly zero times. Your agent designs beautiful UI
> in English and broken UI in فارسی. This skill fixes that.

## What it does

Two layers, applied whenever your agent designs, builds, reviews, or localizes UI:

**Correctness** — the rules that make RTL interfaces *right*:
- Direction set at the root, logical CSS / `Directional` Flutter widgets, never physical `left`/`right`
- Which icons mirror (chevrons, arrows, back) and which never do (play, phone, clocks, logos)
- Bidi handling: LTR islands (emails, URLs, phone numbers, code) that don't scramble
- Persian ی/ک vs Arabic ي/ك, Persian digits ۰–۹ (and when Latin digits are correct)
- Jalali (Shamsi) dates with Persian month names — «۵ مرداد ۱۴۰۵», not "July 27"
- ZWNJ (نیم‌فاصله): می‌شود, not «می شود» — preserved through storage, search, truncation

**Taste** — the rules that make Persian interfaces *good*:
- Persian type metrics (body line-height 1.8–2.0 — Latin's 1.5 is cramped in Persian)
- The letter-spacing ban (it tears joined script *and* silently breaks PDF text layers)
- Six font-pairing recipes by mood, stack-first with licensed-fallback stacks
- A Persian "AI-tells" list — the recognizable slop patterns of generated Persian UI

Platform depth for **web** (CSS, React/Next, Tailwind) and **Flutter** — the two
ecosystems whose RTL rules genuinely differ.

**Composes with your favorite design skill.** Keep impeccable/taste/ui-ux-pro-max for
general design intelligence — rtl-design is the RTL/Persian layer on top, and it has
explicit precedence rules for where general skills' Latin assumptions break Persian
(letter-spacing, line-height, font choices, icon direction).

## Zero-token detector

Deterministic audit of existing code — no LLM, no API key, no dependencies
(Python stdlib only):

```bash
python3 skills/rtl-design/scripts/detect.py ./src --format text
```

9 rules: Arabic ي/ك in Persian text, Arabic-Indic ٠-٩, Latin digits in Persian copy,
physical CSS properties, letter-spacing on Persian, physical Flutter APIs, hardcoded
`dir="ltr"`, missing ZWNJ after می/نمی, missing `dir` on `<html>`. JSON output for
agents, text for humans, exit codes for CI.

## Install

```bash
npx skills add Baghlani/rtl-design        # this project only
npx skills add Baghlani/rtl-design -g     # all your projects
```

Or copy `skills/rtl-design/` into your agent's skills directory
(`.claude/skills/`, `.agents/skills/`, …).

Two things worth knowing: the default install is **project-scoped** (it lands in the
directory you run it from — use `-g` for global), and agents discover skills at
**session start** — restart your session after installing.

## Design & structure

Token-lean by design: a <100-line dispatcher `SKILL.md` (~1k tokens loaded on
activation), deep knowledge in `references/` loaded only on demand, and knowledge
that needs no tokens at all living in the detector script.

```
skills/rtl-design/
├── SKILL.md                  # core rules + routing (loaded on activation)
├── references/
│   ├── web.md                # CSS/React/Tailwind: logical props, icons, bidi, forms, motion
│   ├── flutter.md            # Directional widgets, Jalali packages, TextField, testing
│   └── typography.md         # fonts & licensing, pairing recipes, digits, ZWNJ, slop list
└── scripts/
    └── detect.py             # zero-dependency deterministic detector
```

## Font licensing stance

This skill recommends fonts honestly: free-first (Vazirmatn, Estedad — both OFL, both
on Google Fonts), commercial faces (Dana, Morabba, IRANYekanX, …) named with official
[fontiran.com](https://fontiran.com) links only. It never bundles or links commercial
font files, and it warns about the ecosystem's licensing traps (Peyda is not free;
"free IRANSans" CDNs are unlicensed). Recipes are written stack-first so designs work
for everyone and upgrade instantly when a license exists.

## Roadmap

- **v1** — RTL core + Persian deep module, web + Flutter, detector
- **v2** — Arabic deep module (contributions from Arabic-speaking designers welcome),
  Hebrew notes, more recipes, detector rules for Vue/Svelte templates

## Prior art

Structure openly inspired by [impeccable](https://github.com/pbakaus/impeccable),
[ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill),
[taste-skill](https://github.com/Leonxlnx/taste-skill), and Anthropic's
[frontend-design](https://github.com/anthropics/skills) — see [NOTICE.md](NOTICE.md).
No content was copied; every rule and value here is derived from ~9 years of shipping
Persian/RTL products on web and Flutter.

## License

[Apache-2.0](LICENSE) © Abolfazl Baghlani
