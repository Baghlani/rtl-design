# Persian Typography — Fonts, Recipes, Digits, ZWNJ

Load this when choosing fonts, building a type scale, writing Persian copy into UI, or
answering "which font should this project use?". This file carries both layers: the
correctness rules and the taste recipes.

## 1. What Persian script needs (and Latin defaults get wrong)

- **Line-height:** Persian has ascenders/descenders and dot stacks in both vertical
  directions plus vowel marks. Latin-tuned `1.5` feels cramped. Use **1.8–2.0 for body**,
  1.4–1.5 for headings, and up to 2.1 for dense reading surfaces (articles, terms pages).
- **Optical size:** at equal px, Persian text reads smaller than Latin. Bump body one
  step (e.g. 15–16px where Latin uses 14px) or use a font with a generous x-height
  (Vazirmatn, Estedad) at the same size.
- **Letter-spacing: never.** Persian is a joined script — tracking visibly tears the
  joins. It also breaks PDF text extraction/search for Persian (empirically verified:
  PDF generators emit per-glyph positioning that destroys the text layer). If a design
  system applies default tracking to headings/labels (Material 3 does), zero it for
  Persian. For "airy" display text, use kashida (§2) or weight/size contrast instead.
- **No text-transform equivalents:** no uppercase, no small-caps. Hierarchy must come
  from weight, size, and color — this is why variable-weight fonts matter more in
  Persian than in Latin.
- **Justification:** naive `text-align: justify` creates rivers in Persian. Only justify
  long-form reading text, and prefer engines/fonts with kashida-aware justification;
  UI copy is always `start`-aligned.

## 2. The free font ladder (licensing verified 2026-07)

| Font | License | Best role | Notes |
|---|---|---|---|
| **Vazirmatn** | OFL 1.1, on Google Fonts | Default UI body | Neutral, huge weight range, the safe pick |
| **Estedad** | OFL 1.1, on Google Fonts | Headings + expressive UI | Variable, weight 100–900. Older v7.x releases also carry a **kashida (`KSHD`) axis** — dropped in v8+ and absent from the Google Fonts build; self-host a pinned v7.x if you want it |
| Noto Naskh Arabic | OFL 1.1 (Google) | Editorial/traditional body | Naskh flavor ≈ "serif" role; full Persian coverage |
| Noto Sans Arabic | OFL 1.1 (Google) | Fallback terminator | Broad coverage; put last in every stack |
| Shabnam / Sahel / Samim / Gandom | OFL 1.1 | Legacy projects | Shabnam/Samim/Gandom archived upstream (2022), Sahel dormant since 2021 — fine to use, no future fixes; prefer Vazirmatn/Estedad for new work |
| Tanha | Bitstream Vera license (NOT OFL) | Display accents | Free to use; don't label it OFL |
| IBM Plex Sans Arabic | OFL 1.1 | Corporate alt | Test Persian-specific glyphs before committing |

**Licensing gotchas to warn users about:**
- **Peyda is NOT free.** It is a commercial FontIran typeface; every "free Peyda"
  download is an unlicensed copy. This is currently the most common Persian font
  licensing trap.
- All "IRANSans free download" CDN copies are unlicensed. Commercial fonts (Dana,
  Morabba, IRANYekanX, IRANSans, Yekan Bakh, Peyda) require a paid license from
  fontiran.com. Recommending them by name is fine; bundling or hotlinking files is not.

## 3. Pairing recipes (the taste layer)

Stack-first pattern: the first family is the aspirational (often commercial) face; the
fallbacks are free and legal, so the design works for everyone and upgrades instantly
when a license exists. Never output a single-font stack.

| Recipe | Mood / use | Headings | Body | Numerals & Latin |
|---|---|---|---|---|
| **Product Default** | SaaS, dashboards, apps | `"IRANYekanX", "Estedad", "Vazirmatn", sans-serif` w700 | `"Vazirmatn", "Noto Sans Arabic", sans-serif` w400/500 | Persian digits; Latin islands inherit (Vazirmatn Latin is fine) |
| **Editorial** | Magazines, blogs, news | `"Morabba", "Estedad", sans-serif` w800, tight leading 1.3 | `"Noto Naskh Arabic", "Vazirmatn", serif` 17–18px, lh 2.0 | Persian digits everywhere incl. dates |
| **Bold Statement** | Landing heroes, campaigns | `"Estedad"` w900, size ≥ 3rem; optionally kashida-stretched display lines (`"KSHD" 130`–`160`, self-hosted Estedad v7.x only) | `"Estedad"` w300–400, lh 1.9 | Persian digits, oversized stat numerals w800 |
| **Calm / Minimal** | Portfolios, docs, reading apps | `"Vazirmatn"` w300 at large sizes (hierarchy from size, not weight) | `"Vazirmatn"` w400, lh 2.0, muted contrast | Persian digits, generous whitespace |
| **Corporate / Fintech** | Banking, gov, enterprise | `"Dana", "IRANSans", "Vazirmatn", sans-serif` w700 | `"Dana", "Vazirmatn", sans-serif` w400 | **Latin digits for account/card numbers (LTR-isolated), Persian elsewhere** |
| **Cultural / Traditional** | Art, heritage, food, poetry | `"Noto Naskh Arabic"` w700 or Tanha for accents | `"Noto Naskh Arabic"` lh 2.1 | Persian digits; consider ornamental dividers over hairlines |

Recipe mechanics:
- Weight jumps in Persian need to be bigger than Latin to register: pair 400 body with
  700+ headings (500/600 midweights read as "same but muddy" at small sizes).
- Kashida axis: `font-variation-settings: "KSHD" 140` (tag is case-sensitive and
  uppercase; range 100–200, 100 = none). Only in self-hosted Estedad v7.x — v8+ and
  the Google Fonts build dropped the axis. Short display lines only — never body text.
- One family can carry a whole app (Estedad or Vazirmatn variable) — vary weight/size.
  Two families max; the second earns its place by contrast (naskh vs geometric).

## 4. Digits

- UI text, counts, dates, prices: **Persian digits ۰۱۲۳۴۵۶۷۸۹ (U+06F0–U+06F9)**.
- Keep **Latin digits** for: phone numbers, verification codes/OTP, postal/national/card
  numbers, version strings, technical IDs, code. These are LTR islands — isolate them
  (web.md §4 / flutter.md §4).
- **Never Arabic-Indic digits ٠١٢٣٤٥٦٧٨٩ (U+0660–U+0669) in Persian text** — they arrive
  via Arabic keyboards and copy-paste; ۴/٤ and ۶/٦ differ visibly. Normalize on input.
- Convert at the presentation layer; store canonical Latin digits in data.
- Price formatting: «۲٬۵۰۰٬۰۰۰ تومان» — Persian digits, ٬ (U+066C) as thousands
  separator, currency word after the number. Decimal separator is the momayyez
  ٫ (U+066B): «۲٫۵ مگابایت» — not the ASCII period.

## 5. ی / ک and Unicode hygiene

- Persian ی (U+06CC) and ک (U+06A9) — **never** Arabic ي (U+064A) / ك (U+0643) in
  Persian text. They render with wrong dots/forms and break search, sorting, and dedup.
  Sources of contamination: Arabic keyboard layouts, legacy Windows-1256 data, LLM
  output. Normalize at every input boundary.
- Other lookalikes to normalize: ە (U+06D5) vs ه (U+0647); أ/إ/ٱ variants when users
  mean plain ا (context-dependent — normalize for search keys, preserve for Arabic
  loan-spellings in display).
- Persian question mark ؟ (U+061F), comma ، (U+060C), semicolon ؛ (U+061B) — not ASCII
  `?,;` in Persian copy. Quotes: «گیومه» — not Latin quotes, straight `"…"` or curly “…”.

## 6. ZWNJ (نیم‌فاصله, U+200C)

The signature of professional Persian text. It joins words semantically while breaking
the letterform connection:

- Verb prefixes: می‌شود، نمی‌دانم (never «می شود» with a full space, never «میشود» fused)
- Plural/suffixes: کتاب‌ها، بزرگ‌تر، مهم‌ترین
- Compounds: بین‌المللی، صرفه‌جویی، به‌عنوان

Rules for UI work:
- Preserve ZWNJ through the whole pipeline: string files, DB, search indexing (index
  both with and without), truncation logic (never break inside a ZWNJ-joined word).
- `word-spacing` affects spaces, not ZWNJ — safe. `letter-spacing` destroys ZWNJ joins —
  another reason for §1's ban.
- LLM-generated Persian frequently omits ZWNJ or uses full spaces — copyedit generated
  copy against the patterns above.

## 7. Persian AI-tells (the slop list)

Generated Persian UI has recognizable tells. Ban them:

1. Latin-tuned line-height (1.4–1.5) on Persian body text.
2. `letter-spacing` on Persian headings (often inherited from a Latin design system).
3. Latin digits scattered mid-sentence in Persian copy.
4. Arabic ي/ك in Persian strings.
5. Full spaces or fused forms where ZWNJ belongs («می شود» / «میشود»).
6. Single default font at default weights everywhere — no pairing, no scale contrast.
7. English-length placeholder copy («لورم ایپسوم» counts) — use real Persian strings
   with real lengths.
8. Gregorian dates or English month names in a Persian-facing UI.
9. ASCII punctuation ? , ; and "quotes" in Persian sentences.
10. Center-aligned long Persian paragraphs.

## 8. Webfont mechanics

- Load from Google Fonts (Vazirmatn, Estedad, Noto) or self-host the OFL files —
  self-hosting is legal for OFL and faster inside Iran where Google CDN can be slow;
  for Iran-market products prefer self-hosted with `font-display: swap`.
- Subset: `arabic` + `latin` unicode-ranges; Persian needs the Arabic subset (it covers
  U+06CC/U+06A9 and Persian digits — verify ۰–۹ render in the chosen subset).
- Variable fonts (Estedad, Vazirmatn variable builds) beat 4 static weights on payload.
- `size-adjust`/fallback metrics: match the fallback (Noto Sans Arabic) to the primary
  to kill CLS on slow loads.

## 9. Specimen page (see-it-before-you-commit)

When the user wants to compare directions/recipes, generate a single-file
`specimen.html` in their project (they open it locally; nothing is published):

- `<html dir="rtl" lang="fa">`, Google Fonts links for Vazirmatn + Estedad + Noto Naskh
  Arabic only (OFL — embedding is legal). Commercial faces appear stack-first
  (`"Dana", "Vazirmatn"…`) so license owners see the real thing and others see the
  fallback — label each block with the active recipe name.
- Include per recipe: H1/H2/body/caption scale, a stat row with Persian digits, a mixed
  bidi paragraph containing an email + a price, a form row (Persian field + LTR phone
  field), and one long-string overflow card (stress strings in web.md §8).
- End with a licensing note: which faces are free, which need a fontiran.com license.
