# RTL on the Web — CSS, React/Next, Tailwind

Load this when building or reviewing web UI. Core rules live in SKILL.md; this file is the
full playbook with values and code.

## 1. Direction setup

- Set direction once, at the root: `<html dir="rtl" lang="fa">`. Never simulate RTL with
  `text-align: right` or per-element `float` — that styles text, not layout, and breaks
  flex/grid order, scroll direction, and bidi resolution.
- In Next.js App Router set it in the root layout: `<html lang="fa" dir="rtl">`. For
  bilingual apps derive both from the active locale — never hardcode one and patch the other.
- Style per-direction with `:dir(rtl)` (modern) or `[dir="rtl"]` (universal). Keep these
  overrides rare: if you write logical CSS, you barely need them.

## 2. Logical properties — the default dialect

Physical `left`/`right` CSS is a latent RTL bug. Write logical from the start:

| Physical (avoid) | Logical (use) |
|---|---|
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `left: 0` / `right: 0` | `inset-inline-start: 0` / `inset-inline-end: 0` |
| `border-left` | `border-inline-start` |
| `border-top-left-radius` | `border-start-start-radius` |
| `text-align: left` / `right` | `text-align: start` / `end` |
| `float: left` | `float: inline-start` |

Physical values are correct only when the thing is physically anchored regardless of
language: media controls overlaying video, map compass, code editors (always LTR).

### Tailwind

Use the logical utilities — they exist for exactly this: `ms-*`/`me-*` (margin),
`ps-*`/`pe-*` (padding), `start-*`/`end-*` (inset), `text-start`/`text-end`,
`rounded-s-*`/`rounded-e-*`, `border-s`/`border-e`. Reach for `rtl:`/`ltr:` variants only
when behavior genuinely differs by direction (e.g. an asymmetric illustration), not as a
substitute for logical utilities. Legacy `space-x-*` needs `space-x-reverse` under RTL;
prefer `gap` in flex/grid instead — it is direction-safe by nature.

## 3. Icon mirroring

The single most recurring RTL bug class. Decide per icon, not per icon-set.

**Mirror (directional meaning follows reading order):**
back/forward arrows, chevrons (navigation, accordions, breadcrumbs), "continue"/"next",
undo/redo, reply/forward (mail), list-indent/outdent, login/logout arrows, pagination
arrows, sidebar collapse, "send" (paper plane), progress chevrons, first/last track skip.

**Never mirror (physical or universal meaning):**
play/pause/stop (media time is LTR by convention), volume, phone handset, clocks and
watches, logos and brand marks, checkmarks, search magnifier, refresh/sync circular
arrows, media rewind/fast-forward (tied to the LTR timeline), sliders' handles, numbers.

**Judgment calls:** question-mark, half-star ratings (mirror the fill direction), speech
bubbles (mirror if the tail implies reading direction).

Mechanism — flip with CSS, don't ship duplicate assets:

```css
[dir="rtl"] .icon-directional { transform: scaleX(-1); }
```

With icon fonts/SVG sprite systems, tag directional icons with a class at the source so
the rule above is one line, not a per-usage hunt.

## 4. Bidi: mixed text and LTR islands

Persian/Arabic UI is never 100% RTL text. Emails, URLs, phone numbers, code, Latin brand
names are LTR islands and will scramble punctuation and ordering if not isolated.

- User-generated or unknown-direction content: `dir="auto"` on the element, or wrap in
  `<bdi>`. This is the default for chat bubbles, comments, usernames, search results.
- Inline LTR data inside Persian text: wrap in an element with `dir="ltr"` and
  `unicode-bidi: isolate` (browsers default to isolate for elements with `dir`, but be
  explicit in components).
- Correct rendering test — this sentence must show the number and unit in the right
  visual order: «حجم فایل ۲٫۵ مگابایت است» and this one must not swap the parentheses:
  «نسخهٔ جدید (v2.1.0) منتشر شد».
- Plain strings passed to non-HTML sinks (title attribute, `document.title`, push
  notifications, canvas): use Unicode isolates in the string itself — U+2066 (LRI) /
  U+2067 (RLI) … U+2069 (PDI). Avoid legacy LRM/RLM sprinkling except as a last resort.
- Punctuation at direction boundaries is the tell: if you see «سلام dear!» rendering as
  «!سلام dear» the island isn't isolated.

## 5. Forms and inputs

- Text inputs for Persian content: inherit RTL, `text-align: start`.
- Inputs for inherently LTR data — phone, email, URL, national ID, card number, OTP:
  force `dir="ltr"` on the input but keep the *label and container* RTL. Align the LTR
  input's text to the visual right (`text-align: right` here is correct — the field sits
  in an RTL form) or keep `start` per your form system; be consistent.
- Placeholders in Persian render RTL automatically only if the input is RTL — a common
  bug is `dir="ltr"` phone inputs with Persian placeholders; give the placeholder its own
  direction via `::placeholder { direction: rtl; }` when needed, or use a Persian-digit
  mask.
- Never rely on `input[type=number]` for phone/ID — it strips leading zeros and mangles
  long values; use `inputmode="numeric"` with a text input.

## 6. Layout, scroll, motion

- Flex/grid follow `dir` automatically — do not add `flex-direction: row-reverse` "for
  RTL"; doubling direction logic is how layouts end up LTR again under RTL.
- Horizontal scroll starts from the right in RTL; carousels, tab strips and stepper
  overflows must advance right-to-left. Test `scrollLeft` logic — it is negative or
  reversed across engines; use `scrollIntoView` or logical `scroll-margin-inline` instead
  of hand-computed offsets.
- Slide/entrance animations that encode direction (drawer from the side, next-page slide,
  swipe-to-dismiss) must flip. Implement with logical transforms: animate
  `translateX(calc(var(--flow) * 100%))` where `--flow: 1` and `[dir="rtl"] { --flow: -1; }`,
  or scope keyframes under `[dir]`.
- Box shadows and asymmetric gradients don't auto-flip. Prefer symmetric shadows; if a
  shadow/gradient encodes direction, flip it under `[dir="rtl"]`.
- Progress bars fill start→end (right-to-left in RTL). Media seek bars stay LTR.
- Pointer/drag math is direction-blind: `(e.clientX - rect.left) / rect.width`
  measures from the visual left. For RTL-aware controls compute
  `isRtl ? 1 - visual : visual` once, in one shared helper, keyed to the control's
  own resolved direction — and skip the inversion inside LTR islands (seek bars).
- Charts: keep the time axis LTR (time convention), but RTL-localize labels, legends,
  tooltips, and put the value axis on the visual right. Bar/category charts may fully
  mirror; time series should not.

## 7. React/Next specifics

- One source of truth for direction: derive `dir` from locale in the root layout and read
  it via context/`document.dir` — never per-component `dir` props scattered around.
- CSS-in-JS: use logical properties directly (they're plain CSS now); avoid `rtl-css-js`
  style flippers unless stuck with a legacy physical codebase.
- `next/font` works with local OFL Persian fonts (see `typography.md` for the ladder and
  licensing); subset to `arabic` + `latin`.
- Libraries with known RTL props: MUI (`direction` in theme + stylis-plugin-rtl), Radix /
  shadcn-ui (most primitives accept `dir`), Embla (`direction: 'rtl'`), Swiper
  (`dir="rtl"` on the container element — its `direction` option only means
  horizontal/vertical). Set the
  library's own RTL switch — wrapping an LTR-configured library in `dir="rtl"` gives
  half-flipped UI.

## 8. Overflow and long text

Persian words and compounds run long, and UI text has no hyphenation culture. Test every
truncating surface with real long strings, not «تست»:

- Sample stress strings: «پیشرفته‌ترین قابلیت‌های شخصی‌سازی‌شده» — «مسئولیت‌پذیری»
  — «استانداردسازی زیرساخت‌های بین‌المللی».
- `overflow-wrap: anywhere` for user content containers; `text-overflow: ellipsis` works
  in RTL (ellipsis renders on the visual left) but verify with mixed bidi content.
- Buttons sized on English mockups clip Persian labels — allow wrapping or min-width in
  `ch` of the Persian copy, not the English one.
