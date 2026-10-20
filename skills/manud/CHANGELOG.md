# Changelog

## [3.1.0] — 2026-10-20

Rename release. **The editing instructions are unchanged from V3.0.0.**

- Skill renamed from `thai-humanizer` to `manud` (display name MANUD · มะนุด). The `name` field and the folder name changed; agents now invoke the Skill as `manud`.
- `SKILL.md`: only the frontmatter changed (`name`, `metadata.version`, and new `metadata.display-name` / `metadata.formerly`). The description and the body are byte-identical to V3.0.0.
- `scripts/check_preservation.py`: `VERSION` constant 3.0.0 → 3.1.0 (no behaviour change).
- `README.md` (this folder): title and tree root renamed; opening description clarified (works through the agent's own model); evaluation status now summarises BENCH1 with its limitations; local evaluation path removed.
- Migration from `thai-humanizer`: see `docs/MIGRATION.md` in the repository.

## [3.0.0] — 2026-10-19

V3 turns the Skill from a rewrite style guide into an editorial workflow that decides *whether and how much* to edit before rewriting. Implemented and unit-tested; **not yet evaluated** on a held-out blind test (see `README.md` → Evaluation status).

### Skill instructions
- New Stage A–E workflow in `SKILL.md`: context classification → fidelity contract → editorial transformation → explicit edit-level decision (keep / light / substantial) → one-pass quality gate with at most one revision.
- Relationship preservation made explicit (values, actors, conditions, status must stay attached to the right entity; swapped prices called out as a named error).
- Output rule: return only the edited text unless an audit is requested; "no changes needed" is a valid answer; flag uncertainty instead of guessing.
- New references: `CONTEXT_PROFILES.md` (9 categories, norms not templates), `FIDELITY_CONTRACT.md`, `TECHNICAL_DOCS.md`, `SOCIAL_MEDIA.md`.
- Technical-docs policy: keep headings, lists, code, tables, warnings, versions, endpoints; never trade precision for conversational tone. (Addresses observed T07 weakness.)
- Social/founder policy: endings that fit ordinary posts; remove bureaucratic sign-offs such as `นำข้อมูลนี้ไปประกอบการพิจารณา` even when they come from the source; no forced CTAs, enthusiasm, testimonials, or founder backstory. (Addresses observed T01 weakness.)
- Explicit guidance against default particles, slang, emojis, rhetorical hooks, and automatic loanword substitution.
- `STYLE_GUIDE.md`: phrase tables reframed as pattern examples, not a banned-word filter; benchmark product names replaced with a neutral fictional name; one example that added an unsupported fact (`ตลอดช่วงทดสอบ`) corrected.

### Checker (`scripts/check_preservation.py` 3.0.0)
- Findings split into **deterministic failures**, **suspected semantic violations**, **stylistic warnings** (JSON keys `deterministic_failures`, `suspected_semantic_violations`, `stylistic_warnings`; V2 keys kept as aliases).
- New deterministic inventories: fenced code blocks, inline code, version strings, HTTP endpoints, code identifiers/flags; structure loss (headings, lists, tables, warnings) is deterministic with `--context technical`.
- New heuristics: value↔entity binding (swapped prices/quotas), negation reversal and introduced negation, missing conditions/bounds/exceptions/deadlines, dropped hedges and added certainty, proposed→completed status, actor substitution, added causal connectors, new Latin-script entities and capability verbs, fabricated testimonials and personal experience.
- Context-aware style warnings: formal register in social/founder posts (including retained closings), engagement bait, churn on already-natural text (`--context minimal`), large shortening.
- `--semantic-advisory` reports Tier 2 without failing; `--no-semantic-check` disables V3 heuristics. Exit codes unchanged (0/1/2).
- All V2.1 checks and message strings retained; the 28 V2.1 tests pass unchanged.

### Tests & tooling
- `tests/test_v3_regressions.py`: 37 tests on new synthetic examples (none from historical benchmarks).
- `tests/fixtures/`: synthetic release-note fixtures (structured, good rewrite, flattened regression).
- `scripts/validate_skill.py`: frontmatter, links, version consistency, evaluation-isolation checks.

### Evaluation integrity (behaviour-affecting changes)
- Removed the Slow Morning Cafe worked example from `SKILL.md` and the TaskNest/Cafe benchmark answers from `references/EVALUATION_RUBRIC.md`. Both are preserved verbatim, read-only, in `~/thai-humanizer-eval/historical/`. The model no longer sees these reference answers during rewriting, which may change outputs on those historical tasks.
- `examples/social_after.txt` corrected: the V2.1 version added facts not in the source (`ต้นไม้เยอะ`, `บรรยากาศโปร่งสบายมาก`).
- Rubric frozen as V3 (same five 1–5 dimensions as the October 2026 run, plus separate factual and format gates).

## [0.2.1] — V2.1 (October 2026)
- Audience-aware openings, voice differentiation, anti-hallucination guardrails, spoken presentation mode, 28 checker tests. Preserved in `~/thai-humanizer-backups/`.
