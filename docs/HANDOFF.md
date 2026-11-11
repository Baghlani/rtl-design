# rtl-design — Handoff

## 1. Snapshot (as of 2026-11-12)
- v1 is built and the repo `Baghlani/rtl-design` is **public** (flipped after the 2026-07-28 work; 1 star at last check). All PRs (#1–#14) are merged; no open PRs.
- v1 content: 21-entry pain-point catalog (+ row 22, the SVG `text-anchor` trap), web + Flutter references, Persian typography with font safety, zero-dependency detector with self-verification, live demo page, benchmark.
- Benchmark (`bench/RESULTS.md`): defects per page Sonnet 5 2.0 → 0.0, Haiku 4.5 3.0 → 0.0 with the skill.
- Launch media (96 s video, square cut, covers, carousels) were produced in a separate media project (2026-07-28). Whether the launch posts went out is unverified.
- The skill is already consumed by other projects (e.g. Box installs it from GitHub via `skills-lock.json`).
- No commits since 2026-07-28.

## 2. People & context
- Maintainer: Abolfazl Baghlani (GitHub: Baghlani). Launch media live in a separate, non-public project.

## 3. Timeline (newest first)
- 2026-07-28 — Launch media session (separate media project); benchmark figures EN/FA (#13) and catalog row 22 (#14).
- 2026-07-27 — README rewritten around the measured benchmark (#11); three detector gaps closed + self-verification, Haiku reaches 0.0 (#12).
- 2026-07-26 — v1 repositioning: pain-point catalog, live proof-of-concept, font safety (#10); display taste parked for phase 2.
- 2026-07-25 — Five open questions closed (`docs/decisions.md`); skill drafted.
- 2026-07-24 — Project seeded from `BRIEF.md`.

## 4. Key decisions and why
- Broad `rtl-design` name with Persian as the flagship deep module; Arabic/Hebrew share the direction layer, deep Arabic module is v2.
- Web + Flutter from day one — the owner's real experience spans both and their RTL rules differ.
- Detector ships in v1, stdlib-only, so the skill costs zero tokens to verify.
- Apache-2.0 + `NOTICE.md` crediting structural prior art.
- Display-typography "taste" parked for phase 2; v1 keeps only font safety.
- Media lives in a separate project so the OSS repo doesn't fill with marketing files.

## 5. Open work / next steps
1. Rename the local folder to `rtl-design` (between sessions) and update local notes that reference the old path.
2. Distribution from decision #4: Claude plugin marketplace listing, awesome-list PRs, launch article (Virgool fa / LinkedIn en) — status unverified.
3. Housekeeping: delete merged branch `fix/detector-multiline-dart-constructors` (local + remote).
4. Phase 2: Persian display typography recipes, deep Arabic module.

## 6. Waiting on the owner
- Confirmation of what was published (articles, posts) and any community feedback to act on.

## 7. Environments & operations
- GitHub Actions CI only (`.github/workflows/ci.yml`). No deployment. Install path for users: `npx skills add Baghlani/rtl-design` (Agent Skills layout).

## 8. Where the history lives
- Conversation digests: `~/Documents/claude-backup/digests/Users-abolfazl-baghlani-Documents-persian-rtl-skill/`.
