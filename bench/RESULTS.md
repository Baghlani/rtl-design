# Benchmark results

Does an AI agent actually produce these defects, and does the skill actually prevent them?
Measured, not asserted.

## Method

- **5 prompts** (`bench/prompts.md`) — realistic Persian UI briefs: profile page, sales
  dashboard, product detail, booking form, account settings. None of them mentions RTL,
  direction, digits, dates or fonts; hinting at a defect would teach the baseline the
  answer and void the comparison.
- **Two arms, one variable.** Identical prompt text in both. The skill arm is additionally
  told to read `skills/rtl-design/SKILL.md` and follow it. Nothing else differs.
- **Model: Claude Sonnet 5** — the tier most people actually run in Cursor and CLI agents.
- **Scoring:** `bench/score.py`, a deterministic checker independent of the skill's own
  detector, covering 18 of the 21 catalogued pain points (#12 is Flutter-only, #13 icon
  direction and #21 overflow need a human eye). Every finding carries the matching text so
  any number here can be audited from the committed run files.

Raw generated pages: `bench/runs/sonnet/`. Raw scores: `bench/results/*.json`.

## Result

| | defects per page |
|---|---|
| Sonnet 5, no skill | **2.0** |
| Sonnet 5 + rtl-design | **0.0** |

### What the baseline got wrong

| # | Defect | Rate |
|---|---|---|
| 11 | Physical CSS (`margin-left`, `left:`) instead of logical properties | **3/5** |
| 09 | ASCII decimal/thousands separator between Persian digits (`۴.۵`) | **2/5** |
| 15 | Phone/email input without `dir="ltr"` — caret jumps while typing | **2/5** |
| 17 | `letter-spacing` on Persian, which tears the joined script | **2/5** |
| 18 | Latin body line-height (1.6) on Persian text | **1/5** |

With the skill: **0/5 on every one of the 18 checks.**

## What this does not claim

Sonnet 5 is good at Persian *text* on its own: zero occurrences of Arabic ي/ك, Arabic-Indic
digits, Latin digits in prose, missing ZWNJ, Gregorian dates, or unisolated grouped numbers
across all five baseline pages. The story is not "the model can't write Persian."

The failures cluster in **CSS and form semantics** — the parts a language model treats as
styling boilerplate rather than as language. Those are exactly the defects that survive
review, because the page looks right in a screenshot and only misbehaves when a user types
into a phone field or when the design is read at full size.

Caveats stated plainly: n=5 per arm, one model, web only, and three catalogued defects are
not machine-checkable. The scorer was tightened twice *against* our own result — once for
Jalali date and quantity inputs wrongly counted as Latin fields, once for product model
designations (`X1`) wrongly counted as Latin digits — which removed two baseline hits.

## Reproducing

```bash
# generate: run each prompt in bench/prompts.md twice — once plain, once after reading
# skills/rtl-design/SKILL.md — writing to bench/runs/<model>/{baseline,skill}/pN.html
python3 bench/score.py bench/runs/<model>/baseline --summary
python3 bench/score.py bench/runs/<model>/skill --summary
```
