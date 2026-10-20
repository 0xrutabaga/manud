# BENCH1 summary (exploratory)

**Classification: COMPLETED — EXPLORATORY EVIDENCE OF IMPROVEMENT** (closed 2026-10-20 by the project owner).
This is a public summary. The raw evidence (held-out tasks, outputs, judgments, manifests) stays in the private evaluation workspace and is not part of this repository. Nothing here is a claim of statistical or scientific certainty.

## What was compared

| | |
| :-- | :-- |
| Arm A | the model with no Skill |
| Arm B | the same model with Thai Humanizer **V3.0.0** (MANUD 3.1.0 has byte-identical editing instructions) |
| Model route | `ag/gemini-3.8-flash-high` through the third-party router **9Router 0.5.81** (served label `gemini-3.8-flash-n`) |
| Tasks | 30 synthetic Thai editing tasks written independently of the Skill (held-out set v4h-1.0), 3 samples each |
| Generation | 180/180 calls; 1 unit excluded (provider safety block); 89 complete units |
| Judge | **one** AI judge, Claude Opus 5.5 (`claude-opus-5-5`), both presentation orders: 178/178 valid judgments |

## Preregistered results

| Gate | Result |
| :-- | :-- |
| G1: preference for B (task level) | 0.994 (30/30 tasks favour B; Wilson 95% interval [0.886, 1.0]) |
| G2′: deterministic fidelity failures | A 53/89, B 19/89. About half are false positives; true omissions or changed values: A 19/89, B 2/89 |
| G3: units with a material fidelity problem | A 87.6%, B 1.1%. The A figure is 67.4% if both judge orders must agree; the rubric counts embellishment as material. Not adjudicated by a human |

## Limitations (read these before citing the numbers)

1. **No native-Thai human review.** A blind review package was prepared but not used, so judge–human agreement is unknown.
2. **Single AI judge**, from the same model family as the author of the held-out tasks; its effective effort level could not be verified. A same-model manual audit is not independent.
3. **9Router uncertainty:** effective thinking level, full upstream prompt, router retries and actual model weights are not visible. Results apply to this environment only and do not show equivalence with Antigravity's own Gemini Flash High.
4. **No native Antigravity activation test:** the Skill text was injected into the API prompt. Whether agents load and trigger the Skill on their own was not measured.
5. **Small, exploratory scope:** n = 30 tasks; 2 tasks flagged for upstream drift; blinding was partial, because no-Skill outputs were visibly different (multiple versions in about 70% of outputs, about 3.3× longer).

## Integrity

At closure, all sealed BENCH1 files matched their SHA-256 manifests (run files 1,080/1,080; held-out set 39/39; Skill 40/40). The closure record and manifests are kept in the private evaluation workspace.
