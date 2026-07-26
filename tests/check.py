#!/usr/bin/env python3
"""Detector self-tests. Stdlib only, Python 3.9+. Exit 0 = all pass."""

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DETECT = ROOT / "skills" / "rtl-design" / "scripts" / "detect.py"
FIX = ROOT / "tests" / "fixtures"
failures = []


def run(target, *args):
    p = subprocess.run([sys.executable, str(DETECT), str(target), *args],
                       capture_output=True, text=True)
    data = json.loads(p.stdout) if p.stdout.strip().startswith("{") else None
    return p.returncode, data


def check(name, cond, detail=""):
    if cond:
        print(f"  ok  {name}")
    else:
        print(f"FAIL  {name}  {detail}")
        failures.append(name)


# 1. clean file → exit 0, zero findings
rc, d = run(FIX / "clean.html")
check("clean: exit 0", rc == 0, f"rc={rc}")
check("clean: no findings", d["counts"] == {"error": 0, "warning": 0}, str(d["counts"]))

# 2. html violations → known rule set
rc, d = run(FIX / "violations.html")
rules = Counter(f["rule"] for f in d["findings"])
check("html: exit 1", rc == 1, f"rc={rc}")
check("html: rules R001,R002,R003,R007,R008,R009",
      set(rules) == {"R001", "R002", "R003", "R007", "R008", "R009"}, str(dict(rules)))
check("html: R001+R002+R009 are errors",
      all(f["severity"] == "error" for f in d["findings"]
          if f["rule"] in ("R001", "R002", "R009")))

# 3. css violations → R004 x3, R005 x1; zero-value letter-spacing not flagged
rc, d = run(FIX / "violations.css")
rules = Counter(f["rule"] for f in d["findings"])
check("css: R004 x3, R005 x1", rules == Counter({"R004": 3, "R005": 1}), str(dict(rules)))
check("css: logical suggestions resolved",
      all("logical equivalent" not in f["suggestion"] for f in d["findings"]
          if f["rule"] == "R004"))

# 4. dart violations → R005 (error: file has Persian) + R006; letterSpacing: 0 accepted
rc, d = run(FIX / "violations.dart")
rules = Counter(f["rule"] for f in d["findings"])
check("dart: R005 x1, R006 x1", rules == Counter({"R005": 1, "R006": 1}), str(dict(rules)))
check("dart: R005 is error in Persian file",
      all(f["severity"] == "error" for f in d["findings"] if f["rule"] == "R005"))

# 5. suppression markers → exactly one finding (the unmarked line)
rc, d = run(FIX / "suppressed.dart")
check("suppress: single unmarked finding survives",
      len(d["findings"]) == 1 and d["findings"][0]["rule"] == "R001",
      str(d["findings"]))

# 5b. legit LTR islands and direction-scoped CSS → zero findings
# (field regression: detector must not bark at the exact patterns web.md §5 teaches)
rc, d = run(FIX / "legit-islands.html")
check("islands: exit 0", rc == 0, f"rc={rc}")
check("islands: zero findings on taught patterns",
      d["counts"] == {"error": 0, "warning": 0}, str(d["findings"]))

# 5c. <style> blocks in markup files get pure-CSS treatment; JS stays exempt
# (field regression: RTL drawer anchored with left:0 inside an HTML style block)
rc, d = run(FIX / "embedded-style.html")
rules = Counter(f["rule"] for f in d["findings"])
check("embedded-style: exactly one R004", rules == Counter({"R004": 1}), str(dict(rules)))
check("embedded-style: it is the drawer line, not the JS object",
      d["findings"][0]["line"] == 4 and "drawer" in d["findings"][0]["snippet"],
      str(d["findings"][0]))

# 6. unknown rule id → exit 2
rc, _ = run(FIX / "clean.html", "--rules", "R999")
check("unknown rule id: exit 2", rc == 2, f"rc={rc}")

# 7. findings cap: counts stay complete, storage truncates
rc, d = run(FIX, "--max-findings", "3")
check("cap: stored <= 3", len(d["findings"]) <= 3, str(len(d["findings"])))
check("cap: truncated flag", d["truncated"] is True)
check("cap: full counts preserved", sum(d["counts"].values()) > 3, str(d["counts"]))

print()
if failures:
    print(f"{len(failures)} FAILED")
    sys.exit(1)
print("all detector self-tests passed")
