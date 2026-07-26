#!/usr/bin/env python3
"""Benchmark scorer — measures which pain-point defects appear in generated HTML.

Unlike scripts/detect.py (which advises a developer on their own codebase), this
scores model output for the benchmark: one row per defect from docs/pain-points.md,
present/absent, with the matching evidence so every number can be audited.

Stdlib only. Usage:
    python3 bench/score.py <file.html> [--format json|text]
    python3 bench/score.py <dir> --summary        # aggregate across a run set
"""

import argparse
import json
import re
import sys
from pathlib import Path

# --- text extraction -------------------------------------------------------

RE_TAG = re.compile(r"<[^>]+>")
RE_STYLE_BLOCK = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
RE_SCRIPT_BLOCK = re.compile(r"<script[^>]*>(.*?)</script>", re.S | re.I)
RE_COMMENT = re.compile(r"<!--.*?-->", re.S)
PERSIAN_LETTER = re.compile(r"[پچژگکیء-ي]")
PERSIAN_ONLY = re.compile(r"[پچژگ]")


def parts(html):
    """Return (visible_text, css, js). Visible text has tags/scripts/styles removed."""
    css = "\n".join(RE_STYLE_BLOCK.findall(html))
    js = "\n".join(RE_SCRIPT_BLOCK.findall(html))
    body = RE_COMMENT.sub(" ", html)
    body = RE_STYLE_BLOCK.sub(" ", body)
    body = RE_SCRIPT_BLOCK.sub(" ", body)
    text = RE_TAG.sub(" ", body)
    return text, css, js


def mask_isolated(html):
    """Blank out content that is already inside a bdi / code / dir=ltr element, so the
    ordering checks only see text that would actually reorder."""
    out = re.sub(r"<(bdi|code|kbd|samp)\b[^>]*>.*?</\1>", " \u27e6ISO\u27e7 ", html, flags=re.S | re.I)
    out = re.sub(r'<([a-z]+)\b[^>]*\bdir\s*=\s*["\']ltr["\'][^>]*>.*?</\1>',
                 " \u27e6ISO\u27e7 ", out, flags=re.S | re.I)
    return out


def ltr_classes(css):
    """Class names whose CSS rule sets direction: ltr — an equally valid way to make a
    field an LTR island, and one the dir-attribute check would otherwise miss."""
    names = set()
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        if re.search(r"direction\s*:\s*ltr", m.group(2), re.I):
            names.update(re.findall(r"\.([A-Za-z0-9_-]+)", m.group(1)))
    return names


# --- individual defect checks ---------------------------------------------
# each returns (present: bool, evidence: str)

def d01_arabic_yeh_kaf(html, text, css, js, iso):
    m = re.search(r".{0,25}[يك].{0,25}", text)
    return (bool(m), m.group(0).strip() if m else "")


def d02_latin_digits(html, text, css, js, iso):
    """A standalone Latin number sitting in Persian prose. Alphanumeric identifiers
    (X1, WH-1000XM5, A55) are legitimately Latin and are not counted."""
    for m in re.finditer(r"(?<![A-Za-z0-9-])[0-9][0-9,.]*(?![A-Za-z0-9-])", text):
        ctx = text[max(0, m.start() - 30):m.end() + 30]
        if PERSIAN_LETTER.search(ctx):
            return True, ctx.strip()[:60]
    return False, ""


def d03_arabic_indic(html, text, css, js, iso):
    m = re.search(r".{0,20}[٠-٩].{0,20}", text)
    return (bool(m), m.group(0).strip() if m else "")


def d04_zwnj(html, text, css, js, iso):
    m = re.search(r"(?<![؀-ۿ‌])(ن?می) (?=[؀-ۿ])", text)
    if m:
        return True, text[max(0, m.start() - 15):m.end() + 15].strip()
    # a Persian page with essentially no ZWNJ at all is the same defect
    persian_words = len(re.findall(r"[؀-ۿ]{3,}", text))
    if persian_words >= 40 and text.count("‌") == 0:
        return True, f"{persian_words} Persian words, zero ZWNJ in the page"
    return False, ""


MONTHS = r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"


def d05_gregorian(html, text, css, js, iso):
    m = re.search(r"[0-9]{1,2}\s+" + MONTHS + r"\s+[0-9]{4}|" + MONTHS + r"\s+[0-9]{1,2},?\s+[0-9]{4}"
                  r"|20[0-9]{2}[/-][01][0-9][/-][0-3][0-9]", text)
    return (bool(m), m.group(0).strip() if m else "")


def d06_grouped_number(html, text, css, js, iso):
    """A number split into groups by space or hyphen, outside any isolate."""
    for m in re.finditer(r"[0-9]{1,4}[\s -][0-9]{2,4}(?:[\s -][0-9]{2,4})*", text):
        s = m.group(0)
        ctx = text[max(0, m.start() - 40):m.end() + 40]
        if PERSIAN_LETTER.search(ctx):
            return True, s.strip()
    return False, ""


def d07_currency_sign(html, text, css, js, iso):
    for m in re.finditer(r"[$€£]\s?[0-9][0-9,.\s]*", text):
        if PERSIAN_LETTER.search(text[max(0, m.start() - 40):m.end() + 40]):
            return True, m.group(0).strip()
    return False, ""


def d08_ascii_punct(html, text, css, js, iso):
    m = re.search(r"[؀-ۿ]\s?[?;]|[؀-ۿ],\s", text)
    if m:
        return True, text[max(0, m.start() - 20):m.end() + 10].strip()
    return False, ""


def d09_separators(html, text, css, js, iso):
    m = re.search(r"[۰-۹][.,][۰-۹]", text)      # Persian digits, ASCII sep
    return (bool(m), m.group(0) if m else "")


def d10_html_dir(html, text, css, js, iso):
    m = re.search(r"<html\b[^>]*>", html, re.I)
    if not m:
        return True, "no <html> tag"
    if not re.search(r'\bdir\s*=\s*["\']rtl["\']', m.group(0), re.I):
        return True, m.group(0)[:70]
    return False, ""


def d11_physical_css(html, text, css, js, iso):
    m = re.search(r"\b(margin|padding)-(left|right)\s*:|(?<![-\w])(left|right)\s*:\s*[-0-9]", css)
    return (bool(m), m.group(0) if m else "")


def d14_drawer(html, text, css, js, iso):
    for m in re.finditer(r"\{[^{}]*\}", css):
        b = m.group(0)
        if re.search(r"(?<![-\w])(left|right)\s*:\s*0", b) and "translateX" in b:
            return True, b.strip()[:80]
    return False, ""


def d15_input_dir(html, text, css, js, iso):
    for m in re.finditer(r"<input\b[^>]*>", html, re.I):
        tag = m.group(0)
        latin_field = re.search(r'type\s*=\s*["\'](tel|email|url)["\']', tag, re.I) \
            or re.search(r'inputmode\s*=\s*["\'](tel|email|url)["\']', tag, re.I)
        if not latin_field and re.search(r'inputmode\s*=\s*["\']numeric["\']', tag, re.I):
            # numeric inputs count only when the field is actually Latin data
            hints = " ".join(re.findall(r'(?:name|id|placeholder|aria-label)\s*=\s*["\']([^"\']*)["\']',
                                        tag, re.I)).lower()
            latin_field = bool(re.search(r"phone|mobile|tel|card|iban|sheba|otp|code|zip|postal", hints)) \
                and not re.search(r"[۰-۹]|تاریخ|تعداد|مبلغ|قیمت", tag)
        has_dir = re.search(r'\bdir\s*=\s*["\']ltr["\']', tag, re.I)
        cls = set(re.findall(r'class\s*=\s*["\']([^"\']*)["\']', tag))
        styled = any(c in iso for group in cls for c in group.split())
        if latin_field and not has_dir and not styled:
            return True, tag[:80]
    return False, ""


def d16_drag_math(html, text, css, js, iso):
    for m in re.finditer(r"(clientX|offsetX|pageX)[^;\n]{0,120}", js):
        s = m.group(0)
        if not re.search(r"rtl|direction|1\s*-\s*", s, re.I):
            return True, s.strip()[:80]
    return False, ""


def d17_letter_spacing(html, text, css, js, iso):
    for m in re.finditer(r"letter-spacing\s*:\s*([^;}!<]+)", css):
        v = m.group(1).strip().lower()
        if v not in {"0", "0px", "0em", "0rem", "normal", "inherit", "unset", "initial"}:
            return True, m.group(0).strip()
    return False, ""


def d18_line_height(html, text, css, js, iso):
    m = re.search(r"body\s*\{[^}]*line-height\s*:\s*([0-9.]+)", css, re.S)
    if m and float(m.group(1)) < 1.7:
        return True, f"body line-height: {m.group(1)}"
    vals = [float(v) for v in re.findall(r"line-height\s*:\s*([0-9.]+)\s*[;}]", css)]
    body_like = [v for v in vals if 1.0 < v < 1.7]
    if vals and not m and len(body_like) == len([v for v in vals if v > 1.0]):
        return True, f"no line-height at/above 1.7 anywhere (values: {sorted(set(vals))})"
    return False, ""


COMMERCIAL = r"(IRANSans|IRANYekan|Dana|Morabba|Peyda|Kalameh|IranNastaliq|Yekan\s?Bakh|Rokh|Ravi)"
NO_PERSIAN_FACES = r"(Tajawal|Readex Pro|Amiri Quran|Ruwudu|Alkalami|Fandogh)"


def d19_font_no_persian(html, text, css, js, iso):
    m = re.search(NO_PERSIAN_FACES, html, re.I)
    return (bool(m), m.group(0) if m else "")


def d20_commercial_font(html, text, css, js, iso):
    """Commercial face self-hosted or CDN-linked (naming it in a stack is fine)."""
    for m in re.finditer(r"@font-face\s*\{[^}]*\}", css, re.S):
        if re.search(COMMERCIAL, m.group(0), re.I):
            return True, m.group(0).strip()[:90]
    m = re.search(r'<link[^>]+href=["\'][^"\']*' + COMMERCIAL + r'[^"\']*["\']', html, re.I)
    return (bool(m), m.group(0)[:90] if m else "")


CHECKS = [
    ("01", "Arabic ي/ك in Persian text", d01_arabic_yeh_kaf),
    ("02", "Latin digits in Persian text", d02_latin_digits),
    ("03", "Arabic-Indic digits ٠-٩", d03_arabic_indic),
    ("04", "Missing ZWNJ", d04_zwnj),
    ("05", "Gregorian date shown to Persian users", d05_gregorian),
    ("06", "Grouped number not isolated (reverses)", d06_grouped_number),
    ("07", "Currency sign prefix not isolated", d07_currency_sign),
    ("08", "ASCII ? ; , in Persian sentence", d08_ascii_punct),
    ("09", "ASCII decimal/thousands separator", d09_separators),
    ("10", "<html> without dir=rtl", d10_html_dir),
    ("11", "Physical CSS instead of logical", d11_physical_css),
    ("14", "Drawer anchored to a physical side", d14_drawer),
    ("15", "Latin-data input without dir=ltr", d15_input_dir),
    ("16", "Pointer math without direction handling", d16_drag_math),
    ("17", "letter-spacing on Persian", d17_letter_spacing),
    ("18", "Latin line-height on Persian body", d18_line_height),
    ("19", "Font with no Persian coverage", d19_font_no_persian),
    ("20", "Commercial font shipped as a file", d20_commercial_font),
]


def score_file(path):
    html = Path(path).read_text(encoding="utf-8", errors="replace")
    text, css, js = parts(html)
    text_open, _, _ = parts(mask_isolated(html))   # isolated runs removed
    iso = ltr_classes(css)
    results = {}
    for pid, label, fn in CHECKS:
        try:
            visible = text_open if pid in {"02", "06", "07"} else text
            present, evidence = fn(html, visible, css, js, iso)
        except Exception as e:                     # a broken check must not fake a pass
            present, evidence = None, f"check error: {e}"
        results[pid] = {"label": label, "present": present, "evidence": evidence}
    return {"file": str(path), "defects": sum(1 for r in results.values() if r["present"]),
            "checked": len(CHECKS), "results": results}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Score generated HTML against the pain-point catalog.")
    ap.add_argument("path")
    ap.add_argument("--format", choices=["json", "text"], default="text")
    ap.add_argument("--summary", action="store_true", help="aggregate every .html under a directory")
    a = ap.parse_args(argv)

    root = Path(a.path)
    files = sorted(root.rglob("*.html")) if root.is_dir() else [root]
    if not files:
        print("no html files found", file=sys.stderr)
        return 2
    scored = [score_file(f) for f in files]

    if a.format == "json":
        print(json.dumps(scored if len(scored) > 1 else scored[0], ensure_ascii=False, indent=2))
        return 0

    if a.summary and len(scored) > 1:
        print(f"{len(scored)} files\n")
        print(f"{'#':<4}{'defect':<44}{'rate'}")
        for pid, label, _ in CHECKS:
            hits = sum(1 for s in scored if s["results"][pid]["present"])
            bar = "█" * hits + "·" * (len(scored) - hits)
            print(f"{pid:<4}{label:<44}{hits}/{len(scored)}  {bar}")
        avg = sum(s["defects"] for s in scored) / len(scored)
        print(f"\naverage defects per file: {avg:.1f} of {len(CHECKS)}")
        return 0

    for s in scored:
        print(f"\n{s['file']} — {s['defects']}/{s['checked']} defects present")
        for pid, r in s["results"].items():
            if r["present"]:
                print(f"  ✕ {pid} {r['label']}")
                if r["evidence"]:
                    print(f"       {r['evidence']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
