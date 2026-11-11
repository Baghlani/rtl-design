# rtl-design

Current status and history: see docs/HANDOFF.md

Open-source RTL/Persian UI design skill on the Agent Skills standard (works in Claude Code, Cursor, Codex CLI, Gemini CLI…). Name is final: `rtl-design`; the skill lives at `skills/rtl-design/`.

**Context docs:** `docs/decisions.md` (final decisions), `docs/pain-points.md` (the defect catalog), `docs/research/` (standard anatomy + font licensing audits), `bench/RESULTS.md` (measured benchmark).

## Layout
- `skills/rtl-design/SKILL.md` — lean body (<80 lines); deep detail in `references/` (`web.md`, `flutter.md`, `typography.md`, `hooks.md`); `scripts/detect.py` — zero-dependency violation detector.
- `tests/check.py` + `tests/fixtures/` — detector regression tests.
- `bench/` — benchmark: `prompts.md`, `score.py` (independent checker), `runs/`, `results/`, `figures/` (EN + FA charts).
- `demo/index.html` — live proof-of-concept page for every pain point.
- `.github/workflows/ci.yml` — compile + tests + `skills-ref validate`.

## Commands
- Detector: `python3 skills/rtl-design/scripts/detect.py <path> [--format text]` — stdlib-only, zero deps; keep it that way. JSON stdout, exit codes 0/1/2.
- Tests: `python tests/check.py` · compile check: `python -m py_compile skills/rtl-design/scripts/detect.py`.
- Spec validation: `pip install "git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref" && skills-ref validate skills/rtl-design`.
- Benchmark scoring: `python3 bench/score.py` (see `bench/RESULTS.md` for method).

## Rules
- All artifacts (SKILL.md, docs, commits) in English.
- Close open decisions in ONE numbered round with recommended defaults, then build autonomously. Decision docs record finals only, no churn narrative.
- Keep the skill token-lean (lean SKILL.md body <80 lines, deep detail in references/, zero-token detector script) — it's a selling point.
- Remote: github.com/Baghlani/rtl-design. Work on branches and open PRs; the maintainer merges.
- Never commit: .env*, .claude/, CLAUDE.md, BRIEF.md (internal doc), scratch/report .md files (docs/ is fine).
- Skill content itself must follow the rules it teaches (ی/ک U+06CC/U+06A9, Persian digits in examples, correct bidi in mixed-text samples).
- Fonts: never bundle or link commercial font files; recipes are stack-first with OFL fallbacks (Vazirmatn default, Estedad second).
- Verify any comparison claim empirically before building a narrative on it; frame comparisons with other skills as complementary.
