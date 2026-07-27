# rtl-design

[![ci](https://github.com/Baghlani/rtl-design/actions/workflows/ci.yml/badge.svg)](https://github.com/Baghlani/rtl-design/actions/workflows/ci.yml)

**Stop re-explaining Persian and RTL to your coding agent.**
An [Agent Skills](https://agentskills.io) skill for Claude Code, Cursor, Codex CLI, Gemini
CLI and 70+ other agents.

You know the loop. You ask for a Persian page, it comes back with `margin-left` everywhere,
a phone field where the caret jumps while you type, and `letter-spacing` quietly tearing the
script apart. You tell it. Next session, same thing.

## It is measured, not claimed

Five realistic Persian UI briefs, each generated twice — once plain, once after reading this
skill. Same prompt, same model, one variable. Scored by a checker independent of the skill's
own detector, across 18 machine-checkable defects.

| Model | no skill | + rtl-design | |
|---|---|---|---|
| **Claude Sonnet 5** | 2.0 defects/page | **0.0** | −100% |
| **Claude Haiku 4.5** | 3.0 defects/page | **0.8** | −73% |

What the unaided runs actually got wrong:

| Defect | Sonnet 5 | Haiku 4.5 |
|---|---|---|
| Physical CSS (`margin-left`, `left:`) instead of logical properties | 3/5 | 3/5 |
| Phone/email input without `dir="ltr"` — caret jumps while typing | 2/5 | 3/5 |  <!-- rtl-ignore -->
| ASCII separator between Persian digits (`۴.۵` instead of `۴٫۵`) | 2/5 | 3/5 |
| `letter-spacing` on Persian, which tears the joined script | 2/5 | 2/5 |
| Latin body line-height on Persian text | 1/5 | 3/5 |

**The honest half:** modern models write correct Persian *text* on their own — zero Arabic
ي/ك, zero wrong digits, zero missing ZWNJ, zero Gregorian dates across all baseline pages.  <!-- rtl-ignore -->
The failures cluster in **CSS and form semantics**, the parts a model treats as styling
boilerplate rather than as language. Those are exactly the defects that survive review,
because a screenshot looks fine and the bug only shows when a user types into a phone field.

Method, caveats, all 20 generated pages and raw scores: [`bench/RESULTS.md`](bench/RESULTS.md).

## See every defect live

[**`demo/index.html`**](demo/index.html) renders all 21 catalogued defects side by side with
their fixes — the reversed phone number, the drawer sliding in from the wrong side, a slider
that runs backwards, a real "Arabic" webfont with no Persian letters. Nothing is a
screenshot; every break happens in your browser.

## What it covers

[`docs/pain-points.md`](docs/pain-points.md) is the contract: **21 defects**, each with the
wrong output, the right output, why it matters, and an honest note on whether the bundled
detector catches it automatically (9), whether it needs the agent's judgment (9), or whether
it is still an open gap (3).

**Text & data** — Persian ی/ک vs Arabic ي/ك · Persian digits ۰–۹ and when Latin digits are  <!-- rtl-ignore -->
correct · ZWNJ (نیم‌فاصله) · Jalali dates with Persian month names · which mixed-text
patterns actually reorder (measured in a browser — the real rule is narrower than the
folklore) · Persian punctuation and separators.

**Layout & direction** — logical CSS properties · Flutter `Directional` widgets · which icons
mirror and which never do · drawer and slide direction · input field direction · pointer and
drag math, where logical APIs can't help you.

**Type rendering** — Persian line-height metrics · the letter-spacing ban · verifying a font
actually renders Persian before you ship it · font licensing traps.

Platform depth for **web** (CSS, React/Next, Tailwind) and **Flutter** — the two ecosystems
whose RTL rules genuinely differ, and Flutter is covered by no other design skill.

## Zero-dependency detector

Audit existing code deterministically — no LLM, no API key, no packages:

```bash
python3 skills/rtl-design/scripts/detect.py ./src --format text
```

Nine rules, JSON for agents, text for humans, exit codes for CI, `rtl-ignore` markers for
legitimate exceptions. It is a floor, not full coverage — the skill says so explicitly and
routes the judgment pass to the reference files.

## Install

```bash
npx skills add Baghlani/rtl-design        # this project only
npx skills add Baghlani/rtl-design -g     # all your projects
```

Or copy `skills/rtl-design/` into your agent's skills directory (`.claude/skills/`,
`.agents/skills/`, …). Two things worth knowing: the default install is **project-scoped**
(use `-g` for global), and agents discover skills at **session start** — restart after
installing.

## Composes with your design skill

Keep impeccable, taste or ui-ux-pro-max for general design intelligence. rtl-design is the
RTL/Persian layer on top, with explicit precedence rules for where Latin assumptions break
Persian. Worth knowing: a general design linter is calibrated for Latin, so a clean pass from
one says nothing about Persian correctness.

## Design & structure

Token-lean: a ~100-line dispatcher `SKILL.md` (~1k tokens on activation), deep knowledge in
`references/` loaded only on demand, and knowledge that costs no tokens at all living in the
detector.

```
skills/rtl-design/
├── SKILL.md                  # core rules + routing (loaded on activation)
├── references/
│   ├── web.md                # logical CSS, icons, bidi, forms, motion, pointer math
│   ├── flutter.md            # Directional widgets, Jalali, TextField, gesture math
│   └── typography.md         # metrics, font safety, licensing, digits, ZWNJ
└── scripts/detect.py         # zero-dependency deterministic detector
docs/pain-points.md           # the 21 defects — the contract every claim traces to
bench/                        # the benchmark: prompts, scorer, runs, results
demo/index.html               # all 21 defects rendered live
```

## Font stance

Free-first (Vazirmatn, Estedad — both OFL, both on Google Fonts). Commercial faces (Dana,
Morabba, IRANYekanX …) are named with official [fontiran.com](https://fontiran.com) links
only; no commercial font file is ever bundled or hotlinked. The skill also carries the traps,
verified by parsing font binaries and shaping Persian text: **Tajawal and Readex Pro have no
Persian letters at all**, Fandogh renders Persian disconnected, and Kalameh and IranNastaliq
ship commercial licenses inside binaries that circulate freely on GitHub.

## Roadmap

- **v1** — RTL core + Persian module, web + Flutter, detector, benchmark
- **next** — close the three detector gaps (ASCII punctuation, Persian separators, Latin
  line-height) and add a self-verification step, so the residual defects on smaller models go
  to zero too
- **v2** — Arabic deep module (contributions from Arabic-speaking designers very welcome),
  Hebrew notes, expressive Persian typography (parked in `docs/research/display-fonts.md`)

## Prior art

Structure openly inspired by [impeccable](https://github.com/pbakaus/impeccable),
[ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill),
[taste-skill](https://github.com/Leonxlnx/taste-skill) and Anthropic's
[frontend-design](https://github.com/anthropics/skills) — see [NOTICE.md](NOTICE.md). No
content was copied; every rule here comes from ~9 years of shipping Persian/RTL products on
web and Flutter.

## License

[Apache-2.0](LICENSE) © Abolfazl Baghlani
