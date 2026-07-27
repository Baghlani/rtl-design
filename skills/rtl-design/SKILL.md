---
name: rtl-design
description: Use when designing, building, reviewing, or fixing any right-to-left (RTL) user interface — Persian/Farsi (فارسی), Arabic, Hebrew, Urdu — on web (React, Next.js, Vue, Tailwind, plain CSS) or Flutter, even if the user only says the app is Persian/Iranian without mentioning RTL. Covers layout direction and mirroring, which icons flip and which never do, bidirectional (bidi) text with LTR islands (URLs, emails, phone numbers, code), Persian vs Arabic-Indic vs Latin digits, Jalali (Shamsi) dates, Persian typography (font pairing, line-height, the letter-spacing trap, ZWNJ نیم‌فاصله), font licensing, logical CSS properties, form input direction, and long-text overflow. Also use when Persian/Arabic text renders wrong or "off", when localizing an LTR app to RTL, or to audit existing code for RTL violations with the bundled zero-dependency detector. Not for backend-only or non-UI tasks.
license: Apache-2.0
metadata:
  author: abolfazl-baghlani
  version: "0.1.0"
---

# RTL Design

Make RTL interfaces that are **correct** (direction, bidi, digits, calendar, Unicode)
and **beautiful** (Persian-tuned typography and pairing recipes) — never a mirrored
afterthought of an LTR design. Persian is the deep module; the direction layer applies
to Arabic and Hebrew too.

Two failure modes to prevent: LTR habits leaking in (physical CSS, unflipped icons,
Latin type metrics), and "technically RTL" slop (correct direction, cramped Latin
line-height, one default font everywhere).

## Core rules — always apply

**Direction & layout**
1. Set direction once at the root (`<html dir="rtl" lang="fa">` / Flutter locale
   `fa`). Never fake RTL with `text-align`/`float`/reversed rows.
2. Write logical, not physical: `margin-inline-start` not `margin-left`,
   `EdgeInsetsDirectional` not `EdgeInsets.only(left:)`, `start`/`end` not
   `left`/`right`. Physical values only for physically-anchored things (video
   controls, maps, code editors).
3. Mirror directional icons: chevrons, arrows, back/next, undo/redo, reply, send,
   pagination. **Never mirror:** play/pause, media seek/rewind, volume, phone, clocks,
   logos, checkmarks, search, refresh. Flip via `transform: scaleX(-1)` /
   `matchTextDirection`, not duplicate assets.

**Text & data**
4. Persian uses ی (U+06CC) and ک (U+06A9) — Arabic ي/ك in Persian text is a bug.
   Normalize at input boundaries.
5. Digits: Persian ۰–۹ in UI text; Latin digits for phone numbers, OTP/codes, card and
   technical IDs (as LTR islands); Arabic-Indic ٠–٩ never in Persian.
6. Dates for Persian users: Jalali calendar, Persian month names, Persian digits —
   «۵ مرداد ۱۴۰۵». Store ISO/Gregorian; convert at presentation.
7. Isolate LTR islands (emails, URLs, phones, code, Latin names) with
   `dir="auto"`/`<bdi>`/`unicode-bidi: isolate` — scrambled punctuation means a
   missing isolate.
8. Respect ZWNJ (نیم‌فاصله): می‌شود not «می شود»/«میشود». Preserve U+200C through
   storage, search, and truncation.

**Typography (minimum — full taste layer in references/typography.md)**
9. Persian body line-height 1.8–2.0 (Latin's 1.5 is cramped); headings 1.4.
10. **Never letter-spacing on Persian** — it tears the joined script and breaks PDF
    text layers. Zero out design-system defaults (Material 3 has them).
11. Verify the font actually renders Persian before using it — several popular
    "Arabic" faces have no پ چ ژ گ at all (typography.md §3). End every stack with
    a known-good fallback so a missing face degrades instead of showing tofu.
12. Test every constrained surface with real long Persian strings
    («استانداردسازی زیرساخت‌های بین‌المللی»), not «تست».

## Routing — read on demand

| Situation | Read |
|---|---|
| Building/reviewing **web** UI (CSS, React/Next, Tailwind, icons, bidi, forms, motion) | `references/web.md` |
| **Flutter** project (Directional widgets, icons, Jalali packages, TextField, testing) | `references/flutter.md` |
| **Fonts** (safety, licensing, pairing), type metrics, digits/ZWNJ detail, specimen page | `references/typography.md` |

## Audit mode — zero-token detector

For existing code, run the deterministic detector first (no LLM, no dependencies):

```bash
python3 scripts/detect.py <path>
```

JSON on stdout: findings with rule id, severity, file:line, snippet, and suggestion.
Exit 0 = clean, 1 = findings, 2 = usage error. `--format text` for humans. Output is
bounded (default 300 findings; `counts` always holds the full totals and `truncated`
flags the cap) — on a huge violation count, fix by rule or directory using `--rules`.

It catches the mechanical violations (Arabic ي/ك, wrong digits, ASCII separators between
Persian digits, physical CSS/Flutter props, letter-spacing on Persian, Latin body leading,
missing/hardcoded `dir`, Latin-data inputs without `dir="ltr"`, missing ZWNJ after می).
Fix every `error`; review each `warning` in context (some have legit exceptions —
the finding says which). Legit-by-design lines (e.g. digit/yeh normalization maps)
get an inline `rtl-ignore` comment, or `rtl-ignore-next` on the line above. The
detector is a floor, not coverage — always also review what no regex can see:
gesture/drag math and nested direction islands (flutter.md §10, web.md §6), visual
hierarchy, icon direction semantics, overflow behavior, recipe quality.

## Before you finish — verify your own output

Whenever you create or edit UI files under these rules, run the detector on what you
wrote and fix every finding before reporting the work as done:

```bash
python3 scripts/detect.py <the files you touched> --format text
```

This is not optional polish. Writing the rules down gets most of the way; running the
check is what closes the gap, because the defects that survive are precisely the ones
that look right in a screenshot — a phone field that scrambles as the user types, an
ASCII comma between Persian digits, Latin leading on Persian body text. Treat a
non-empty result as unfinished work, not as advice.

Claude Code users can make this automatic instead of remembered — see
`references/hooks.md`.

## Coexistence with other design skills

This skill composes with general design skills (taste, structure, color, motion stay
theirs). On conflict, RTL/Persian script needs win — general skills assume Latin
script: reject their letter-spacing on headings, Latin line-height (1.4–1.5), and
Latin font suggestions (Inter etc.) for Persian text; apply this skill's metrics,
font recipes, and icon-mirroring rules instead. Their quality checks are calibrated
for Latin, so a clean pass from a general design linter says nothing about Persian
correctness — run `scripts/detect.py` as well.

## Workflow

- **New UI:** confirm target platform and language(s) → apply core rules from the first
  line of code (retrofitting RTL costs 10×) → pick a typography recipe by mood, don't
  default → load the platform reference for specifics → stress-test with long strings
  and mixed bidi content.
- **Localizing LTR → RTL:** run the detector for the mechanical list → sweep icons
  against the mirror/never lists → replace physical props with logical → then re-design
  typography (metrics, not just fonts) — translation without Persian type metrics is
  where "technically RTL" slop comes from.
- **"Which font?":** never answer with one font. Use the ladder + recipes in
  typography.md, respect licensing (free-first, commercial by name with official links
  only, never bundle commercial files), and offer a specimen page (typography.md §10)
  when the user wants to see options.
