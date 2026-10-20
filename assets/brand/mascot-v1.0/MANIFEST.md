# Little Manud (เจ้ามะนุด) — MANUD mascot v1.0 asset manifest

Status: **FINAL — approved by the owner 2026-10-20. Frozen.** Do not edit these files. Changes need a new version folder (`mascot-v1.1/` …) and owner approval.
Package: `thai-humanizer-eval/branding/manud/mascot-v1.0/` contains only the six canonical SVGs, their editable source generator, this manifest and `SHA256SUMS`. No previews, renders or temporary files.

## Canonical assets

| File | Role / use | viewBox | Colors | SHA-256 |
| :-- | :-- | :-- | :-- | :-- |
| `svg/manud-mascot-light.svg` | **Standard mascot, light backgrounds** (white, cream, GitHub light), ≥ 48px | 0 0 512 512 | Coral, Ink | `3ea31a4e48ca59e6ea74b54afc5ef99d7e3e1c3b498931883e24ed226df8a125` |
| `svg/manud-mascot-dark.svg` | **Standard mascot, dark backgrounds** (`#151C2F`, GitHub dark `#0D1117`), ≥ 48px. Cream outer rim keeps the ink outline visible | 0 0 512 512 | Coral, Ink, Cream | `7bb7bf52a372f41204c4a7fccbe4bd259f4c2d0965e56a55a74b11337dc1ea29` |
| `svg/manud-icon-32-light.svg` | **Small icon, light backgrounds**, about 24–40px (avatars, list icons) | 0 0 32 32 | Coral, Ink | `e2b181444201fbfd965643543b40fee8cdb8372794bc9f58ed75e144ca88301b` |
| `svg/manud-icon-32-dark.svg` | **Small icon, dark backgrounds**, about 24–40px (cream outline) | 0 0 32 32 | Coral, Ink, Cream | `bbe239cffae7aff88d427960cd831580ca750e3cfe33223bc1264688db8bb602` |
| `svg/manud-icon-16-light.svg` | **Favicon / ≤ 20px, light backgrounds** (no mouth) | 0 0 16 16 | Coral, Ink | `76d9eab4920ce7a29e0bafa1185c5e765e01de85c9727123b4147dd6cf9ee632` |
| `svg/manud-icon-16-dark.svg` | **Favicon / ≤ 20px, dark backgrounds** (cream outline, no mouth) | 0 0 16 16 | Coral, Ink, Cream | `291a499d50ee890f5e0aceb670c4e395a015f40ab1701cc0ea705e35360fd25d` |
| `source/build_mascot.py` | Editable source: one parametric geometry that writes all six SVGs (Python stdlib). Regenerates them **byte-identically** (checked 2026-10-20) | — | — | `899f7f5ec030d0b66ceb7897705493660a73f24aade28bd33580a431a27f4023` |

Colors (exact, nothing else used): Coral `#FF95A5` (body), Ink `#1E2A4A` (outline, loop, eyes, mouth), Cream `#FFF6DC` (dark-variant rim/outline only). No gradients, filters, opacity, raster images or text elements. Each SVG has a `<title>` for an accessible name.

The SVGs themselves are editable vectors: live strokes with round caps/joins, one fill path, one outline path including the loop, ellipse eyes and a mouth path. Expand strokes only for derived exports (e.g. a print file). Never edit the canonical files in place.

## Which variant to use

| Background | ≥ 48px | 24–40px | ≤ 20px |
| :-- | :-- | :-- | :-- |
| Light (white, cream `#FFF6DC`, GitHub light) | `manud-mascot-light` | `manud-icon-32-light` | `manud-icon-16-light` |
| Dark (`#151C2F`, GitHub dark `#0D1117`) | `manud-mascot-dark` | `manud-icon-32-dark` | `manud-icon-16-dark` |

- In a README, pair light and dark with `<picture>` + `prefers-color-scheme` (see Brand Pack §7.2).
- Don't use the standard mascot below 48px (fine details blur) or the icons above about 64px (heavy outline).
- Don't place the light variant on dark backgrounds (the ink outline disappears) or any variant on coral, pink or busy photos.

## Provenance

| Step | Record |
| :-- | :-- |
| Concept | Concept A "Loop Bubble", `../MASCOT_DESIGN_BRIEF.md` (approved 2026-10-20) |
| AI reference image | A3 Pebble v2: Meshy text-to-image, model `gpt-image-2`, task `01a157fc-772b-7483-8622-a48b58301e07`, file `../previews/round2/manud-A3-pebble-v02-original.png` (sha256 `165d1a37b5bf125f41822f6114881086cd83f175f7a2149f7d2358e0e42659cb`), prompt in `../MASCOT_IMAGE_PROMPTS.md` §0.2b |
| Vector | Hand-traced from the A3 v2 reference (polar outline samples, gridded crops), then redrawn: smoothed tail notch, refined loop (the outline itself forms one closed cursive loop, leaned 50° outward), exact brand colors. No pixels from the AI image are embedded in any SVG |
| Verification | `../mascot/VERIFY_REPORT.json`: XML well-formed, allowed elements/colors only, transparency at 128/64/32/16px, loop hole open at 128px, body silhouette IoU 0.99 vs A3 v2. Rendered with headless Chrome only |
| Working files (not part of this package) | `../mascot/` (renders, tools, review sheet), `../previews/round1/`, `../previews/round2/` (all Meshy originals kept unchanged with their hash files) |

## Checks still required before open-source publication (none done yet)

1. **AI-output terms.** Review Meshy's terms of service and the terms for `gpt-image-2` outputs obtained through Meshy, covering commercial use, ownership and any attribution or disclosure requirement for the A3 reference that the vector was traced from.
2. **Copyright status / disclosure.** The vector is a human redraw of an AI-generated reference. Copyright protection of AI-assisted works varies by country. Decide whether to disclose "designed with AI-generated references" in the asset README.
3. **Asset license choice.** The repository code is MIT (`LICENSE`, "thai-humanizer contributors"). Decide whether the mascot is MIT-licensed too, put under a separate artwork license (e.g. CC BY 4.0), or kept all-rights-reserved as a brand mark. Write it into an asset README/LICENSE before publishing.
4. **Trademark.** Search "MANUD" / "มะนุด" and the mascot as a figurative mark (Thai DIP, plus other target markets). Consider whether open licensing should exclude trademark use (common practice: a code license plus a separate trademark policy).
5. **Originality.** Reverse-image search the final mascot and get an informal check by Thai designers against existing speech-bubble or chat characters and logos.
6. **Third-party content.** None embedded: no fonts, raster images or external artwork in the SVGs. Color Hunt palettes were used as hex references only; no attribution is required, though the Brand Pack credits the sources.
7. **Copyright line.** Decide the holder name for the artwork (currently the code says "thai-humanizer contributors"; a rename to MANUD is a separate, unapproved step).

Integrity: `SHA256SUMS` lists every file in this package except itself. Check with `sha256sum -c SHA256SUMS` from this folder. The SVG files use Windows **CRLF** line endings, and the hashes are of those exact bytes. If the package goes into git, mark `*.svg` as binary or `-text` in `.gitattributes`, so line-ending conversion can't change the hashes.
