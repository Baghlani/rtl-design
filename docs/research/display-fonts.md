# Research: Persian display & expressive faces (phase 2)

> Verified 2026-07 by parsing font binaries (cmap + GSUB) and shaping Persian text with
> HarfBuzz — coverage of پ چ ژ گ / ی ک / ۰–۹ *and* correct initial/medial/final joining.
> **Not shipped in the skill.** v1 is a pain-fixer; aesthetic font direction is phase 2,
> pending a decision on how much taste the skill should carry. The correctness half of
> this research (the traps table, the vetting string) did ship, in typography.md §3.

Open question for phase 2: nastaliq is impractical on the web — browser shaping is weak,
it needs ~2.7 line-height, it is unreadable below ~24px, files are heavy, and the only
libre face (Gulzar) is single-weight. Treat it as out of scope for UI work.

## 3. Display & expressive faces — where Persian design gets its drama

Persian has no uppercase and no italic tradition, so **display type carries the visual
punch that Latin gets from case and slant**. Shipping a neutral UI sans at 3rem is the
single biggest reason generated Persian pages look flat. All faces below are OFL 1.1,
on Google Fonts, and were verified glyph-by-glyph for پ چ ژ گ / ی ک / ۰–۹ *and* for
correct initial/medial/final joining.

| Face | Style | Weights / axes | Use it for | Watch out |
|---|---|---|---|---|
| **Lalezar** | Persian titling | 1 static | The default display face — Persian-designed, unmistakable | Single weight: no hierarchy inside the family |
| **Jomhuria** | Ultra-condensed titling | 1 static | Posters, huge one-word heroes | Font metrics are exactly 1.0em — **clips unless you set line-height ≥1.6** |
| **Oi** | Ultra-fat display | 1 static | Maximum-impact single words | Counters fill in below ~32px |
| **Katibeh** / **Rakkas** | Decorative titling | 1 static | Headlines with character | Tight metrics; set leading manually |
| **Baloo Bhaijaan 2** | Chunky rounded | VF 400–800 | Friendly/informal brands; variable weight also serves sub-heads | Informal register — wrong for finance/gov |
| **Reem Kufi** | Geometric kufi | VF 400–700 | Formal, architectural, heritage-modern headings | Poor for long text |
| **Qahiri** | Geometric kufi | 1 static | Striking single-line statements | 548 glyphs only — headline use only |
| **Noto Kufi Arabic** | Kufi | VF 100–900 | The safe, complete kufi for mixed content | Neutral by design — less voice |
| **Gulzar** | **Nastaliq** | 1 static | The Persian signature: one hero line, poetry, heritage brands | Needs **line-height ≥2.7**, size ≥24px, never for UI text |
| **Amiri** | Classical naskh | 4 static + italic | Long-form editorial, literary, formal | Too calligraphic for UI chrome |
| **Markazi Text** | Persian-first serif | VF 400–700 | Editorial body under a display heading | — |
| **Scheherazade New** / **Lateef** | Naskh | 4 / 7 static | Traditional documents, Quranic/classical contexts | Scheherazade metrics are tall (2.0) |
| **Handjet** | Modular / pixel | VF wght + **ELGR** + **ELSH** | Genuinely novel Persian lettering — element grid and shape axes build dot/pixel/geometric type | Display only |
| **Playpen Sans Arabic** | Handwriting | VF 100–800 | The only credible libre Persian handwriting face | Informal only |
| **Cairo Play** | Playful sans-display | VF 200–1000 + slnt | Energetic product marketing; slnt adds motion | — |
| **Lemonada** | Rounded display | VF 300–700 | Soft consumer brands | Default metrics 2.0 — budget vertical space |


**Display-led recipes — reach for these when the design needs to make an impression:**

| Recipe | Display line | Body | Notes |
|---|---|---|---|
| **Poster** | `"Jomhuria"` at 5–9rem, `line-height: 1.6` | `"Vazirmatn"` w400, lh 1.9 | Extreme scale contrast is the whole effect — one short line only |
| **Heritage Modern** | `"Reem Kufi"` w700, generous tracking-free spacing | `"Noto Naskh Arabic"`, lh 2.0 | Kufi + naskh reads as authoritative and rooted |
| **Nastaliq Statement** | `"Gulzar"` for exactly one hero line, ≥40px, `line-height: 2.7` | `"Estedad"` w400, lh 1.9 | The most distinctly Persian thing you can do; never let nastaliq touch UI chrome |
| **Editorial Persian** | `"Amiri"` w700 or `"Markazi Text"` w700 | `"Markazi Text"` 18px, lh 2.0 | Serif-on-serif, Persian-first — the closest thing to a Persian magazine voice |
| **New Wave** | `"Handjet"` with `"ELGR" 2, "ELSH" 4` | `"Vazirmatn"` w400 | Modular/pixel Persian lettering — almost nobody has seen this |

