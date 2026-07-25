# Decisions (finals only)

Decided 2026-07-25.

| # | Decision | Final |
|---|---|---|
| 1 | Skill/repo name | `rtl-design` — broad RTL scope, Persian as the flagship deep module. Skill dir: `skills/rtl-design/` (spec: name must equal dir name). Repo folder rename + GitHub repo creation pending. |
| 2 | v1 scope | Web + Flutter from day one. Arabic/Hebrew share the direction layer; deep Arabic module → v2. |
| 3 | Detector | `scripts/detect.py` ships in v1. Python stdlib-only, non-interactive, JSON stdout, exit codes 0/1/2. |
| 4 | Distribution | Repo layout `skills/<name>/SKILL.md` for `npx skills add`; Claude plugin marketplace + awesome-list PRs + launch article (Virgool fa / LinkedIn en) after repo is live. |
| 5 | License | Apache-2.0 + NOTICE.md crediting structural prior art (impeccable pattern). |
| 6 | Content policy | Two layers: correctness (RTL/Persian rules) + taste (Persian recipes). Categories/format may follow prior art (credited); every value re-derived for Persian. No sentence-level copying. No personal workflow content in `skills/`. |
| 7 | Fonts | Never bundle/link commercial font files. Recipes are stack-first (commercial name → OFL fallback). Free ladder: Vazirmatn (default), Estedad (second). Commercial fonts named with official fontiran.com links only. FontIran partnership: post-launch. |
