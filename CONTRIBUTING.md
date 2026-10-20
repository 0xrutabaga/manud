# Contributing to MANUD

Thanks for helping! MANUD is small and careful on purpose, so please read this first.

## Good first contributions

- **Report a bad edit.** Open an issue with the original Thai text, MANUD's output, which agent/model you used, and what went wrong (a fact changed, the wrong tone, it edited text that was fine). Remove anything private first.
- **Report a checker miss or false alarm** in `scripts/check_preservation.py`, with a minimal pair of files.
- **Fix docs**, in English or Thai.

## Changing the Skill

The instructions in `skills/manud/SKILL.md` and `references/` change how the model edits. Please:

1. **Open an issue first** for anything beyond a typo, explaining the problem with a real (anonymised) or synthetic example.
2. **Never use evaluation material.** Don't copy held-out benchmark tasks, reference answers or judge outputs into the Skill, examples or tests. New examples must be your own synthetic text.
3. **Don't add** default particles, slang, emoji, hype, or rules that make the model add facts.
4. Keep `SKILL.md` under 500 lines; put detail in `references/`.
5. Bump the version consistently in `SKILL.md` (`metadata.version`), `scripts/check_preservation.py` (`VERSION`) and `CHANGELOG.md`.

## Checks before a pull request

```bash
cd skills/manud
python scripts/validate_skill.py .
python -m unittest discover -s tests
```

Both must pass. Add a test for checker changes. Python standard library only; no new dependencies.

## Brand files

Don't edit anything in `assets/brand/`. Those files are frozen and hash-checked. New artwork needs a maintainer decision and a new version folder. See [TRADEMARKS.md](TRADEMARKS.md).

## License of contributions

By contributing, you agree that your contribution is licensed under the [MIT License](LICENSE) of this repository (inbound = outbound). Only submit work you have the right to license this way.
*(Owner decision D6: whether to also require a Developer Certificate of Origin sign-off.)*

## Conduct

Be kind and specific. Critique the text, not the person. Discussions can be in Thai or English.
