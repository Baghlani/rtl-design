# Research: Persian Font Licensing Audit

> Verified 2026-07-25 against official sources (GitHub LICENSE files / API metadata, Google Fonts,
> fontiran.com product pages). Feeds `references/typography.md`. Not legal advice.

## Ground rules (what is and isn't a violation)

- **Naming/recommending a commercial font with a link to the official seller is fine** —
  nominative fair use; FontIran's own messaging encourages pointing to official pages.
- **Violations to avoid:** bundling or hotlinking commercial font *files*, linking "free
  download" mirrors (all are piracy), implying foundry endorsement.
- Bundling OFL fonts would be legal (anthropics/canvas-design ships TTFs) — we link instead to
  stay lean.

## Audit table

| Font | License | Free commercial use | Embedding | Official source | Maintained |
|---|---|---|---|---|---|
| **Vazirmatn** | OFL 1.1 | yes | yes | github.com/rastikerdar/vazirmatn + Google Fonts | stable (2023, not archived) |
| **Estedad** | OFL 1.1 | yes | yes | github.com/aminabedi68/Estedad + Google Fonts | **active (2026)**, variable + kashida axis |
| Shabnam | OFL 1.1 | yes | yes | github.com/rastikerdar/shabnam-font | archived 2022 |
| Sahel | OFL 1.1 (Latin: Apache-2.0 via Open Sans) | yes | yes | github.com/rastikerdar/sahel-font | dormant since 2021 |
| Samim | OFL 1.1 | yes | yes | github.com/rastikerdar/samim-font | archived 2022 |
| Gandom | OFL 1.1 | yes | yes | github.com/rastikerdar/gandom-font | archived 2022 |
| Tanha | **Bitstream Vera** (NOT OFL) + Apache-2.0 parts | yes (rename if modified) | yes | github.com/rastikerdar/tanha-font | archived 2022 |
| Noto Sans Arabic | OFL 1.1 | yes | yes | Google Fonts | active (Google) |
| Noto Naskh Arabic | OFL 1.1 | yes | yes | Google Fonts | active (Google) |
| IBM Plex Sans Arabic | OFL 1.1 | yes | yes | github.com/IBM/plex | active — Persian glyph coverage UNCERTAIN, test first |
| **Peyda** | **Proprietary (fontiran)** — widely mislabeled as free | **no** | paid tier only | fontiran.com/fonts/peyda | commercial |
| Dana | Proprietary EULA | no | paid tier only | fontiran.com/fonts/dana | commercial |
| Morabba | Proprietary EULA | no | paid tier only | fontiran.com/fonts/morabba | commercial |
| IRANYekan / IRANYekanX | Proprietary EULA (FontIran trademark) | no | paid tier only | fontiran.com/fonts/iranyekan | commercial |
| IRANSans | Proprietary EULA | no | paid tier only | fontiran.com/fonts/iransans | commercial |
| Yekan Bakh | Proprietary EULA | no | paid tier only | fontiran.com/fonts/yekan-bakh | commercial |

## Gotchas worth teaching in the skill itself

1. **Peyda is not free.** GitHub/free-font-site copies are unlicensed mirrors; the official
   fontiran page says there is no free version. This is the single most common licensing trap in
   Persian web dev right now — the skill should warn about it explicitly.
2. **Tanha is not OFL** (Bitstream Vera lineage) — usable, but must not be labeled OFL.
3. The classic rastikerdar family (Shabnam/Sahel/Samim/Gandom/Tanha) is archived/unmaintained —
   fine to use, but no future fixes; prefer Vazirmatn/Estedad for new projects.
4. All "IRANSansWeb free download" copies circulating on CDNs are unlicensed.

## Recommendation ladder (for references/typography.md)

1. **Default: Vazirmatn** — OFL, on Google Fonts (Google's legal review passed it), stable.
2. **Second: Estedad** — OFL, on Google Fonts, actively maintained, variable weight + kashida.
3. Fallback stack / non-Persian-designed: Noto Sans Arabic (covers Persian), IBM Plex Sans
   Arabic (test Persian glyphs first).
4. Commercial tier (flagged `license required`, official links only): Dana, Morabba,
   IRANYekanX, IRANSans, Yekan Bakh, Peyda.
