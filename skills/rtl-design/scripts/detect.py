#!/usr/bin/env python3
"""rtl-design deterministic detector.

Scans a file or directory for mechanical RTL/Persian violations. Zero dependencies
(Python stdlib only), no network, no LLM. JSON on stdout, diagnostics on stderr.

Usage:
    python3 detect.py <path> [--format json|text] [--rules R001,R004]
                      [--max-findings N] [--max-file-size BYTES]

Exit codes: 0 = clean, 1 = findings, 2 = usage/IO error.
Output is bounded: at most --max-findings findings are stored (20 per file+rule);
`counts` in the JSON envelope always reflects the FULL totals.
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

VERSION = "0.1.0"

SCAN_EXTS = {
    ".html", ".htm", ".vue", ".svelte", ".jsx", ".tsx", ".js", ".ts", ".mjs", ".cjs",
    ".css", ".scss", ".sass", ".less", ".styl",
    ".dart", ".arb",
    ".json", ".yaml", ".yml", ".xml", ".md", ".txt", ".strings", ".resx", ".po",
    ".php",  # Laravel Blade templates and Persian strings in PHP
}
PURE_STYLE_EXTS = {".css", ".scss", ".sass", ".less", ".styl"}
STYLE_EXTS = PURE_STYLE_EXTS | {".vue", ".svelte", ".jsx", ".tsx", ".js", ".ts",
                                ".html", ".htm"}
SKIP_DIRS = {
    "node_modules", ".git", "build", "dist", ".dart_tool", "vendor",
    ".next", ".nuxt", ".output", ".svelte-kit", ".expo", ".turbo", ".angular",
    ".cache", "coverage", "__pycache__", ".venv", "venv", "target", ".gradle",
    ".terraform", "Pods", "DerivedData", "bower_components",
    ".idea", ".vscode", ".claude", ".agents", ".cursor", ".codex",
}
SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock",
    "Podfile.lock", "pubspec.lock", "Cargo.lock", "poetry.lock", "uv.lock",
}
SKIP_SUFFIXES = (".min.js", ".min.css", ".map")

RULE_IDS = {"R001", "R002", "R003", "R004", "R005", "R006", "R007", "R008", "R009"}

MAX_SNIPPET = 120
MAX_LINE_LEN = 2000          # longer lines are minified/generated — skip them
PER_FILE_RULE_CAP = 20       # stored findings per (file, rule)
DEFAULT_MAX_FINDINGS = 300   # stored findings total
DEFAULT_MAX_FILE_SIZE = 1_000_000  # bytes

# Character classes
RE_PERSIAN = re.compile(r"[پچژگکی‌]")   # letters unique to Persian + ZWNJ
ARABIC_SCRIPT = re.compile(r"[؀-ۿ]")
RE_ARABIC_YEH_KAF = re.compile(r"[يك]")          # ي ك
RE_ARABIC_INDIC = re.compile(r"[٠-٩]")           # ٠-٩
RE_LATIN_DIGIT_IN_FA = re.compile(r"[؀-ۿ][^\S\n]?[0-9]|[0-9][^\S\n]?[؀-ۿ]")
RE_PHYSICAL_PROPS = re.compile(
    r"\b(margin-left|margin-right|padding-left|padding-right|border-left|border-right"
    r"|border-top-left-radius|border-top-right-radius|border-bottom-left-radius"
    r"|border-bottom-right-radius)\s*:"
    r"|\b(text-align|float)\s*:\s*(left|right)\b")
# bare left:/right: declarations — pure stylesheets only (too noisy in JS objects)
RE_BARE_INSET = re.compile(r"(?<![-\w$#.])(left|right)\s*:\s*[^;{}]*(?:[;}]|$)")
RE_LETTER_SPACING = re.compile(r"letter-spacing\s*:\s*([^;}!]+)")
LETTER_SPACING_OK = {"0", "0px", "0em", "0rem", "normal", "inherit", "unset", "initial",
                     "revert", "revert-layer"}
RE_DART_LETTER_SPACING = re.compile(r"\bletterSpacing\s*:\s*([^,)\]}]+)")
DART_LETTER_SPACING_OK = {"0", "0.0", "null"}
RE_DART_PHYSICAL = re.compile(
    r"EdgeInsets\.only\s*\([^)]*\b(left|right)\s*:"
    r"|EdgeInsets\.fromLTRB\s*\("
    r"|Alignment\.(centerLeft|centerRight|topLeft|topRight|bottomLeft|bottomRight)\b"
    r"|Positioned\s*\([^)]*\b(left|right)\s*:"
    r"|BorderRadius\.only\s*\([^)]*\b(topLeft|topRight|bottomLeft|bottomRight)\s*:"
    r"|TextAlign\.(left|right)\b")
RE_DIR_LTR = re.compile(r"""dir\s*=\s*["']ltr["']""", re.IGNORECASE)
# self-declared LTR islands: dir="ltr" on these elements is the documented pattern
RE_ISLAND_TAG = re.compile(r"<\s*(input|textarea|select|bdi|code|pre|kbd|samp)\b", re.IGNORECASE)
RE_HTML_TAG = re.compile(r"<html\b[^>]*?>", re.IGNORECASE | re.DOTALL)
RE_DIR_ATTR = re.compile(r"""\bdir\s*=""", re.IGNORECASE)
# می / نمی followed by an ordinary space then a Persian letter → ZWNJ candidate
RE_MI_SPACE = re.compile(r"(?<![؀-ۿ‌])(ن?می) (?=[؀-ۿ])")

LOGICAL_MAP = {
    "margin-left": "margin-inline-start", "margin-right": "margin-inline-end",
    "padding-left": "padding-inline-start", "padding-right": "padding-inline-end",
    "border-left": "border-inline-start", "border-right": "border-inline-end",
    "border-top-left-radius": "border-start-start-radius",
    "border-top-right-radius": "border-start-end-radius",
    "border-bottom-left-radius": "border-end-start-radius",
    "border-bottom-right-radius": "border-end-end-radius",
    "left": "inset-inline-start", "right": "inset-inline-end",
    "text-align: left": "text-align: start", "text-align: right": "text-align: end",
    "float: left": "float: inline-start", "float: right": "float: inline-end",
}


def has_persian(text):
    """Persian-specific letters (or ZWNJ) — distinguishes Persian from generic Arabic."""
    return bool(RE_PERSIAN.search(text))


def snippet(line):
    line = "".join(ch for ch in line.strip()
                   if unicodedata.category(ch) != "Cc")  # strip control chars (ANSI etc.)
    return line[:MAX_SNIPPET] + ("…" if len(line) > MAX_SNIPPET else "")


class Sink:
    """Collects findings with bounded storage; counts always stay complete."""

    def __init__(self, max_findings, rules_filter):
        self.stored = []
        self.counts = {"error": 0, "warning": 0}
        self.max_findings = max_findings
        self.rules_filter = rules_filter
        self.truncated = False
        self._per_file_rule = {}

    def add(self, rule, name, severity, path, lineno, line, suggestion):
        if self.rules_filter and rule not in self.rules_filter:
            return
        self.counts[severity] = self.counts.get(severity, 0) + 1
        key = (str(path), rule)
        n = self._per_file_rule.get(key, 0) + 1
        self._per_file_rule[key] = n
        if n > PER_FILE_RULE_CAP or len(self.stored) >= self.max_findings:
            self.truncated = True
            return
        self.stored.append({
            "rule": rule, "name": name, "severity": severity,
            "file": str(path), "line": lineno,
            "snippet": snippet(line), "suggestion": suggestion,
        })


def check_file(path, sink):
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"skip {path}: {e}", file=sys.stderr)
        return

    ext = path.suffix.lower()
    lines = text.splitlines()
    file_has_persian = has_persian(text)

    def add(rule, name, severity, lineno, line, suggestion):
        sink.add(rule, name, severity, path, lineno, line, suggestion)

    for i, line in enumerate(lines, 1):
        if len(line) > MAX_LINE_LEN:
            continue  # minified/generated content
        if "rtl-ignore" in line or (i > 1 and "rtl-ignore-next" in lines[i - 2]):
            continue  # explicit suppression (normalization code, teaching material)

        # R001 — Arabic yeh/kaf
        if RE_ARABIC_YEH_KAF.search(line):
            if has_persian(line) or file_has_persian:
                add("R001", "arabic-yeh-kaf", "error", i, line,
                    "Replace Arabic ي (U+064A) with ی (U+06CC) and ك (U+0643) with ک (U+06A9) in Persian text.")
            else:
                add("R001", "arabic-yeh-kaf", "warning", i, line,
                    "Arabic ي/ك found. Correct if this text is Arabic; a bug if it is Persian.")

        # R002 — Arabic-Indic digits in Persian context
        if RE_ARABIC_INDIC.search(line) and (has_persian(line) or file_has_persian):
            add("R002", "arabic-indic-digits", "error", i, line,
                "Use Persian digits ۰-۹ (U+06F0–U+06F9), not Arabic-Indic ٠-٩ (U+0660–U+0669), in Persian text.")

        # R003 — Latin digits adjacent to Persian text (Persian context only)
        if (has_persian(line) or file_has_persian) and RE_LATIN_DIGIT_IN_FA.search(line):
            add("R003", "latin-digits-in-persian", "warning", i, line,
                "Persian UI text should use Persian digits ۰-۹. Legit exceptions: phone numbers, "
                "OTP/codes, card/technical IDs — keep those Latin and LTR-isolated.")

        # R004 — physical CSS properties
        # (skipped when the line is direction-scoped — [dir=…]/:dir(…) rules use
        # physical values deliberately, e.g. manual icon flips and island styling)
        if ext in STYLE_EXTS and "[dir=" not in line and ":dir(" not in line:
            m = RE_PHYSICAL_PROPS.search(line)
            if m:
                key = m.group(1) if m.group(1) else f"{m.group(2)}: {m.group(3)}"
                add("R004", "physical-css", "warning", i, line,
                    f"Prefer logical properties: replace `{key}` with `{LOGICAL_MAP[key]}`. "
                    "Physical values are only correct for physically-anchored UI (video controls, maps, code).")
            elif ext in PURE_STYLE_EXTS:
                m2 = RE_BARE_INSET.search(line)
                if m2:
                    add("R004", "physical-css", "warning", i, line,
                        f"Prefer logical properties: replace `{m2.group(1)}` with "
                        f"`{LOGICAL_MAP[m2.group(1)]}`. Physical values are only correct for "
                        "physically-anchored UI (video controls, maps, code).")

        # R005 — letter-spacing (fatal on Persian)
        if ext in STYLE_EXTS:
            ls = RE_LETTER_SPACING.search(line)
            if ls and ls.group(1).strip().lower() not in LETTER_SPACING_OK \
                    and not ls.group(1).strip().startswith("var("):
                add("R005", "letter-spacing", "error" if file_has_persian else "warning",
                    i, line,
                    "Never use letter-spacing on Persian/Arabic — it tears the joined script and "
                    "breaks PDF text layers. Zero it (Material 3 defaults include tracking).")
        if ext == ".dart":
            ls = RE_DART_LETTER_SPACING.search(line)
            if ls and ls.group(1).strip() not in DART_LETTER_SPACING_OK:
                add("R005", "letter-spacing", "error" if file_has_persian else "warning",
                    i, line,
                    "Never use letterSpacing on Persian text — it tears the joined script. "
                    "Material 3 TextTheme carries nonzero letterSpacing (labelLarge, bodySmall…); "
                    "zero it in your Persian TextTheme.")

        # R006 — Flutter physical APIs
        if ext == ".dart" and RE_DART_PHYSICAL.search(line):
            add("R006", "flutter-physical", "warning", i, line,
                "Use the Directional twin: EdgeInsetsDirectional.only(start:/end:), "
                "AlignmentDirectional.centerStart, PositionedDirectional, "
                "BorderRadiusDirectional, TextAlign.start/end.")

        # R007 — hardcoded dir="ltr" alongside Persian/Arabic content
        # (not flagged on self-declared islands — inputs/bdi/code — nor on CSS
        # attribute selectors like input[dir="ltr"], which style rather than wrap)
        m7 = RE_DIR_LTR.search(line) if file_has_persian else None
        if m7 and not (m7.start() > 0 and line[m7.start() - 1] == "[") \
                and not RE_ISLAND_TAG.search(line):
            add("R007", "hardcoded-ltr", "warning", i, line,
                "dir=\"ltr\" in a Persian file — correct only for LTR islands (phone/email/code "
                "inputs, code blocks); a bug if it wraps Persian content.")

        # R008 — missing ZWNJ after می/نمی
        if RE_MI_SPACE.search(line):
            add("R008", "missing-zwnj", "warning", i, line,
                "«می / نمی» followed by a full space — likely needs ZWNJ (U+200C): "
                "می‌شود not «می شود».")

    # R009 — <html> without dir in a file containing Arabic-script text
    # (searched on full text: <html … > tags often span multiple lines)
    if ext in {".html", ".htm", ".php"} and ARABIC_SCRIPT.search(text):
        for m in RE_HTML_TAG.finditer(text):
            if not RE_DIR_ATTR.search(m.group(0)):
                lineno = text.count("\n", 0, m.start()) + 1
                add("R009", "missing-dir", "error", lineno, m.group(0).replace("\n", " "),
                    'This page contains Arabic-script text but <html> has no dir attribute. '
                    'Add <html dir="rtl" lang="fa">.')


def iter_files(root, max_file_size):
    """Yield scannable files. Prunes skipped dirs before descending; never follows
    symlinks; skips lockfiles, minified/generated files, and oversized files."""
    def wanted(p):
        name = p.name
        if name in SKIP_FILES or name.lower().endswith(SKIP_SUFFIXES):
            return False
        if p.suffix.lower() not in SCAN_EXTS:
            return False
        if os.path.islink(p):
            return False
        try:
            if p.stat().st_size > max_file_size:
                print(f"skip {p}: larger than {max_file_size} bytes", file=sys.stderr)
                return False
        except OSError:
            return False
        return True

    if root.is_file():
        # explicitly named file: scan regardless of name filters, but keep the size guard
        try:
            if root.stat().st_size <= max_file_size:
                yield root
            else:
                print(f"skip {root}: larger than {max_file_size} bytes", file=sys.stderr)
        except OSError as e:
            print(f"skip {root}: {e}", file=sys.stderr)
        return
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            p = Path(dirpath) / fn
            if wanted(p):
                yield p


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Deterministic RTL/Persian violation detector (rtl-design skill).")
    ap.add_argument("path", help="File or directory to scan")
    ap.add_argument("--format", choices=["json", "text"], default="json")
    ap.add_argument("--rules", help="Comma-separated rule ids to run (default: all)")
    ap.add_argument("--max-findings", type=int, default=DEFAULT_MAX_FINDINGS,
                    help=f"Max findings to store in output (default {DEFAULT_MAX_FINDINGS}); "
                         "counts always reflect full totals")
    ap.add_argument("--max-file-size", type=int, default=DEFAULT_MAX_FILE_SIZE,
                    help=f"Skip files larger than this many bytes (default {DEFAULT_MAX_FILE_SIZE})")
    args = ap.parse_args(argv)

    root = Path(args.path)
    if not root.exists():
        print(f"error: path not found: {root}", file=sys.stderr)
        return 2
    rules_filter = None
    if args.rules:
        rules_filter = {r.strip() for r in args.rules.split(",") if r.strip()}
        unknown = rules_filter - RULE_IDS
        if unknown:
            print(f"error: unknown rule id(s): {', '.join(sorted(unknown))} "
                  f"(valid: {', '.join(sorted(RULE_IDS))})", file=sys.stderr)
            return 2

    sink = Sink(args.max_findings, rules_filter)
    scanned = 0
    for f in iter_files(root, args.max_file_size):
        scanned += 1
        check_file(f, sink)

    total = sum(sink.counts.values())
    if args.format == "json":
        print(json.dumps({
            "version": VERSION, "path": str(root), "files_scanned": scanned,
            "counts": sink.counts, "truncated": sink.truncated,
            "findings": sink.stored,
        }, ensure_ascii=False))
    else:
        for f in sink.stored:
            print(f"{f['severity'].upper():7} {f['rule']} {f['file']}:{f['line']}  {f['snippet']}")
            print(f"        ↳ {f['suggestion']}")
        note = f" (showing {len(sink.stored)} of {total})" if sink.truncated else ""
        print(f"\n{scanned} files scanned — {sink.counts.get('error', 0)} errors, "
              f"{sink.counts.get('warning', 0)} warnings{note}")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
