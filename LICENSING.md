<!-- DRAFT PROPOSAL for owner review (release candidate). Not legal advice. -->
# What license covers what

MANUD has two kinds of material, under different terms.

| Path | Terms | Notice to keep |
| :-- | :-- | :-- |
| `skills/manud/**` (the Skill: instructions, references, scripts, tests, examples) | **MIT License** | `skills/manud/LICENSE` ("Copyright (c) 2026 thai-humanizer contributors"), kept verbatim |
| Everything else outside `assets/brand/` (README, docs, `CONTRIBUTING.md`, `CHANGELOG.md`, Git config files) | **MIT License** | root `LICENSE` |
| `assets/brand/**` (Little Manud mascot SVGs, their generator `source/build_mascot.py`, manifest, checksums, brand README) | **Not MIT-licensed.** Provided for referring to the MANUD project, under [TRADEMARKS.md](TRADEMARKS.md). The project grants no other rights in these files, to the extent it holds any | — |
| The names **MANUD** and **มะนุด**, and the `manud.` wordmark when published | **Not licensed.** Used by the project as unregistered brand names; see [TRADEMARKS.md](TRADEMARKS.md) | — |

Notes:

- The MIT License covers copyright in the code and text. It doesn't grant any right to use the project's names or brand assets.
- **No registered trademark is claimed.** MANUD is not a registered mark of this project, and the same word is registered by an unrelated company for clothing and footwear in some countries. This page only states how the project asks its brand to be used.
- **No exclusive copyright is claimed in the mascot beyond what the law gives.** The mascot was made with AI assistance (see `assets/brand/README.md`). Whether, and how far, copyright protects it may vary by country.
- Third-party material isn't bundled. `skills/manud/references/LOCAL_MLX.md` mentions optional third-party models and tools that you download yourself under their own terms.
- Contributions are accepted under the same terms as the file they change (MIT for code and docs; brand files aren't open for outside changes). See [CONTRIBUTING.md](CONTRIBUTING.md).
