# What this skill actually fixes

The definitive list of RTL/Persian defects an AI coding agent produces by default, and
what this skill does about each one. This is the spec: the proof-of-concept page must
exercise every row, the README claims must map to rows here, and no marketing claim may
exist without a row.

**Detector column:** `auto` = `scripts/detect.py` finds it deterministically, no LLM.
`judgment` = the agent must reason about it; no regex can decide it.

## Text & data

| # | What the agent writes by default | Correct output | Why it matters | Detector |
|---|---|---|---|---|
| 1 | `كتاب هاي من` — Arabic ي/ك inside Persian | `کتاب‌های من` (ی U+06CC, ک U+06A9) | Wrong letterforms; breaks search, sort and dedup against real Persian data | `auto` R001 |
| 2 | `3 محصول`, `1404` | `۳ محصول`, `۱۴۰۴` | Latin digits in Persian UI text read as machine output | `auto` R003 |
| 3 | `٣ محصول` — Arabic-Indic digits | `۳ محصول` (U+06F3) | ۴/٤ and ۶/٦ are visibly different glyphs; a Persian reader sees Arabic | `auto` R002 |
| 4 | `می شود`, `میشود`, `کتاب ها` | `می‌شود`, `کتاب‌ها` (ZWNJ U+200C) | The single clearest marker of amateur Persian text | `auto` R008 |
| 5 | `27 July 2026`, `2026/07/27` | `۵ مرداد ۱۴۰۵` | Persian users do not read Gregorian dates; wrong calendar makes a product feel foreign | `judgment` |
| 6 | `صفحات 12-15`, `دورهٔ 2024-2026`, `تخفیف 10-20%` all render reversed | Wrap the range in `<bdi dir="ltr">` | Any number split into groups by a space or hyphen reverses under RTL — measured in a real browser, not assumed (web.md §4) | `judgment` |
| 7 | `+98 21 9123 4567` → `4567 9123 21 98+`; `قیمت $1,200` → `1,200$` | `<bdi dir="ltr">` around the number | Grouped phone numbers reverse and a leading currency sign jumps sides. Emails, URLs, `2.1.0`, `4.9/5` are safe — the real rule is narrower than the folklore | `judgment` (R007 assists) |
| 8 | `آیا مطمئنید?` with ASCII `? , ;` | `آیا مطمئنید؟` (؟ U+061F, ، U+060C, ؛ U+061B) | Wrong punctuation shapes; the mirror-image glyph is jarring in Persian | not yet — detector gap |
| 9 | `۲.۵ مگابایت`, `2,500,000` | `۲٫۵` (momayyez U+066B), `۲٬۵۰۰٬۰۰۰` (U+066C) | Persian uses its own decimal and thousands separators | not yet — detector gap |

## Layout & direction

| # | What the agent writes by default | Correct output | Why it matters | Detector |
|---|---|---|---|---|
| 10 | `<html lang="fa">` with no `dir` | `<html dir="rtl" lang="fa">` | The whole page lays out left-to-right; everything downstream is wrong | `auto` R009 |
| 11 | `margin-left`, `padding-right`, `left: 0` | `margin-inline-start`, `padding-inline-end`, `inset-inline-start` | Physical values are silent RTL bugs — correct in English, mirrored wrong in Persian | `auto` R004 |
| 12 | `EdgeInsets.only(left: 8)`, `Alignment.centerLeft` | `EdgeInsetsDirectional.only(start: 8)`, `AlignmentDirectional.centerStart` | Same defect class in Flutter; no design skill covers Flutter at all | `auto` R006 |
| 13 | Chevrons, back/next arrows, reply and send icons pointing the Latin way | Mirror them; never mirror play/pause, seek, volume, phone, clocks, logos, search, refresh | The most recurring RTL bug class, and the one users notice first | `judgment` |
| 14 | Drawer anchored `left: 0` with `translateX(-100%)` | `inset-inline-start: 0` + direction-aware transform | The mobile menu slides in from the wrong side of the screen | `auto` R004 |
| 15 | Phone/email inputs inheriting RTL | `dir="ltr"` on the input, label and container stay RTL | The caret jumps and typed digits land out of order | `judgment` |
| 16 | Drag/seek math as `dx / width` | Invert against `Directionality.of(context)` / the element's own direction | Sliders and swipes run backwards; nested LTR islands double-invert | `judgment` |

## Type rendering

| # | What the agent writes by default | Correct output | Why it matters | Detector |
|---|---|---|---|---|
| 17 | `letter-spacing: .05em` / `letterSpacing: 0.5` on Persian | `0` — always | Tracking tears a joined script apart, and destroys the text layer in generated PDFs. Material 3's default TextTheme ships nonzero values | `auto` R005 |
| 18 | `line-height: 1.4–1.5` (Latin metrics) | 1.8–2.0 body, 1.4 headings | Persian stacks dots above and below; Latin leading looks cramped and clips descenders | not yet — detector gap |
| 19 | A font with no Persian coverage (Tajawal, Readex Pro) or no joining rules (Fandogh) | A verified face + a known-good fallback ending the stack | Letters render as boxes or stand disconnected — the page looks broken, not styled | `judgment` |
| 20 | A commercial font pulled from a "free" GitHub mirror (Kalameh, IranNastaliq, Peyda) | Name it, link the official seller, ship a free fallback | Shipping it is a license violation; the trap is that the download looks legitimate | `judgment` |
| 21 | Buttons and cards sized to English copy | Test with real long Persian strings, allow wrapping | Persian compounds run long; labels clip on the first real string | `judgment` |

## Coverage summary

21 defects: **9 caught deterministically** by the bundled detector (no LLM, no API key),
**9 handled by judgment** with explicit rules in the references, and **3 open detector
gaps** (#8 ASCII punctuation, #9 Persian separators, #18 Latin line-height) — candidates
for the next detector release.

## Rules for using this document

- Every claim in the README, the launch post, or a demo must trace to a row here.
- A new rule earns a row before it ships, with an honest Detector value.
- If a row cannot be demonstrated in the proof-of-concept page, it is not provable —
  either make it demonstrable or drop the claim.
