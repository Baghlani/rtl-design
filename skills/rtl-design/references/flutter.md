# RTL in Flutter

Load this when the project is Flutter. Core rules live in SKILL.md; this is the full
playbook. Flutter has first-class RTL support — most bugs come from bypassing it with
physical values.

## 1. Direction setup

- Direction comes from the locale, not from you: set `locale: Locale('fa')` (plus
  `supportedLocales` and `GlobalMaterialLocalizations.delegate` /
  `GlobalWidgetsLocalizations.delegate` from `flutter_localizations`) and the whole tree
  becomes RTL.
- `Directionality(textDirection: TextDirection.rtl, ...)` is for scoped exceptions
  (an LTR island like a code block or phone field), previews, and tests — not the app root.
- Never set `textDirection` manually on every widget; that's the Flutter equivalent of
  sprinkling `dir` attributes.

## 2. Directional widgets — the default dialect

Physical left/right APIs are latent RTL bugs. Use the `Directional` twin:

| Physical (avoid) | Directional (use) |
|---|---|
| `EdgeInsets.only(left: …, right: …)` | `EdgeInsetsDirectional.only(start: …, end: …)` |
| `EdgeInsets.fromLTRB(a, b, c, d)` | `EdgeInsetsDirectional.fromSTEB(a, b, c, d)` |
| `Alignment.centerLeft` / `centerRight` | `AlignmentDirectional.centerStart` / `centerEnd` |
| `Positioned(left: …)` | `PositionedDirectional(start: …)` |
| `BorderRadius.only(topLeft: …)` | `BorderRadiusDirectional.only(topStart: …)` |
| `Border(left: …)` | `BorderDirectional(start: …)` |
| `TextAlign.left` / `right` | `TextAlign.start` / `end` |

`EdgeInsets.symmetric` and `EdgeInsets.all` are direction-safe — no need to convert.

Row, ListView(horizontal), Wrap, Stepper etc. follow ambient direction automatically —
do not reverse children lists "for RTL".

## 3. Icons

- Many Material glyphs already auto-mirror: their `IconData` is defined with
  `matchTextDirection: true` (e.g. `Icons.arrow_back`, `Icons.send`, `Icons.reply`),
  so they flip in any RTL `Directionality` context with no work from you. Check the
  glyph's API page before adding manual flips — double-mirroring is a real bug.
- For glyphs that should mirror but don't, or custom icon fonts:

```dart
IconData(0xe800, fontFamily: 'MyIcons', matchTextDirection: true) // at the source
Transform.flip(flipX: isRtl, child: Icon(MyIcons.reply))          // at the usage
```

- To pin a direction-aware glyph as an LTR island (e.g. a media-timeline arrow that
  must not flip), wrap it: `Icon(Icons.fast_forward, textDirection: TextDirection.ltr)`.
- `Image` accepts `matchTextDirection: true` — use it for directional raster/SVG
  assets instead of shipping flipped duplicates. (`Icon` has no such parameter — the
  flag lives on `IconData`.)
- Apply the same mirror/never-mirror lists as web (SKILL.md core rules): chevrons,
  arrows, reply, undo mirror; play, phone, clock, logos, refresh never do.
- `CupertinoPageRoute`/`MaterialPageRoute` transitions already flip; custom
  `SlideTransition`s must use `AlignmentDirectional`/`Offset` derived from
  `Directionality.of(context)`.

## 4. Text fields

- Persian fields: nothing special — ambient RTL handles it. Set
  `textAlign: TextAlign.start`.
- LTR-data fields (phone, email, OTP, card number):

```dart
TextField(
  textDirection: TextDirection.ltr,
  textAlign: TextAlign.end, // visually right inside the RTL form
  keyboardType: TextInputType.phone,
)
```

- Persian placeholder + LTR field: give `hintTextDirection: TextDirection.rtl` (via
  `InputDecoration`) so the hint reads correctly while input stays LTR.
- If users type Persian digits, normalize at the model layer (see §6), don't block input.

## 5. Dates — Jalali

- Use a maintained Jalali package (`shamsi_date` for conversion/formatting,
  `persian_datetime_picker` for pickers). Do not hand-roll Jalali math — leap years will
  burn you.
- Display: Jalali with Persian month names and Persian digits — «۵ مرداد ۱۴۰۵».
  Store/transport: ISO-8601 Gregorian UTC. Convert at the presentation edge only.
- Relative time in Persian: «۳ روز پیش»، «لحظاتی پیش» — with Persian digits.

## 6. Digits

Persian digits in UI text; Latin for phone numbers, codes, and technical IDs (full rules
in `typography.md` §5). Conversion is presentation-layer:

```dart
String toPersianDigits(String s) {
  const en = ['0','1','2','3','4','5','6','7','8','9'];
  const fa = ['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹'];
  for (var i = 0; i < 10; i++) { s = s.replaceAll(en[i], fa[i]); }
  return s;
}
```

Normalize the reverse direction (and Arabic-Indic ٠-٩ from Arabic keyboards) before
validation and storage.

## 7. Typography in Flutter

- Bundle OFL fonts as assets (legal — see `typography.md` licensing table): Vazirmatn or
  Estedad. `google_fonts` also ships Vazirmatn (`GoogleFonts.vazirmatn()`), but bundled
  assets avoid runtime fetching and work offline.
- Always define `fontFamilyFallback` ending in a broad Arabic-script font so missing
  glyphs don't tofu:

```dart
TextStyle(fontFamily: 'Estedad', fontFamilyFallback: ['Vazirmatn', 'Noto Sans Arabic'])
```

- Persian needs taller lines: `height: 1.8` for body, `1.4` for headings (Flutter's
  `height` is the line-height multiplier). Material defaults are Latin-tuned and feel
  cramped in Persian.
- Never set `letterSpacing` on Persian text — it visually breaks the joined script.
  Material 3's default `TextTheme` carries nonzero `letterSpacing` on several styles
  (labelLarge, bodySmall…): zero them out in your Persian `TextTheme`.
- ZWNJ is a real character in string literals: `'می‌شود'` — or keep proper «می‌شود»
  in .arb files and render as-is. Never "fix" ZWNJ by removing it.

## 8. Overflow and long text

Persian labels outgrow English mockups. Defensive defaults:

- Every `Text` in a constrained row: wrap in `Flexible`/`Expanded`, set
  `overflow: TextOverflow.ellipsis` deliberately, and test with stress strings:
  «مسئولیت‌پذیری» — «شخصی‌سازی‌شده‌ترین» — «استانداردسازی زیرساخت‌های بین‌المللی».
- `FittedBox` for numeric/stat displays that must not wrap.
- Buttons: never fixed-width from a design tool measured on English text.

## 9. Testing direction

- Widget tests: pump under both directions —
  `Directionality(textDirection: TextDirection.rtl, child: …)` and `.ltr` — and golden-test
  the RTL variant; most direction bugs are visible in one golden.
- Manual pass: switch device locale to fa-IR; check chevrons, back gestures, drawer side,
  slider direction, TabBar order, `ListTile` leading/trailing.

## 10. Gesture & drag math — where logical APIs can't save you

Directional widgets fix layout; raw pointer math is direction-blind. No static rule
can catch these — reason about them explicitly:

- `details.localPosition.dx / width` measures from the **visual left** — under RTL
  that's the *end* of your track. Resolve once, at the gesture site, from the
  ambient direction:

```dart
final visual = details.localPosition.dx / box.size.width;
final progress =
    Directionality.of(context) == TextDirection.rtl ? 1 - visual : visual;
```

- Key the inversion to `Directionality.of(context)` — **never a global "app is
  RTL" flag**. Inside an LTR island (a `Directionality(TextDirection.ltr)` subtree,
  e.g. a media player), a globally-keyed `1 - dx` correction silently
  double-inverts. This nested-island trap survives every audit that only greps.
- Centralize the conversion in one helper; scattered `1 - x` fixes are how double
  inversions are born.
- Media seek bars stay LTR (core rule): wrap the whole bar in
  `Directionality(textDirection: TextDirection.ltr, …)` and keep its math plain —
  cleaner than inverting under RTL.
- Widgets that already resolve direction (`PageView`, `Dismissible`,
  `ReorderableListView`, `TabBarView`) need **no** manual inversion — adding one
  flips them back.
