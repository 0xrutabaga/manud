# Changelog

Repository-level changes. The Skill's own detailed history is in [`skills/manud/CHANGELOG.md`](skills/manud/CHANGELOG.md).

## [3.1.0] — 2026-10-20 (first public release)

### Renamed
- **thai-humanizer → MANUD (มะนุด).** The Skill folder and `name` are now `manud`. The editing instructions are byte-identical to Thai Humanizer V3.0.0. See [docs/MIGRATION.md](docs/MIGRATION.md).

### Added
- Brand assets: mascot **Little Manud v1.0** (`assets/brand/mascot-v1.0/`, six SVG variants with a hash manifest).
- Bilingual README, install guide (with agent test results), migration guide, contributing guide, licence-scope page (`LICENSING.md`), brand policy (`TRADEMARKS.md`), security policy (`SECURITY.md`).
- Public BENCH1 summary (`docs/evaluation/BENCH1_SUMMARY.md`): exploratory evidence of improvement, with limitations.
- One-command install through the Skills CLI (`npx skills add 0xrutabaga/manud`); README Quick install section.
- Repository tests (`tests/test_release_packaging.py`: packaging integrity, plus Skills CLI install, reinstall and removal) and a CI workflow for Linux, macOS and Windows.

### Unchanged
- Skill behaviour, checker behaviour (`check_preservation` VERSION constant 3.0.0 → 3.1.0 only), tests (65 passing).

## [3.0.0] — 2026-10-19 (as thai-humanizer)
- Editorial A–E workflow, fidelity contract, context profiles, three-tier checker.
