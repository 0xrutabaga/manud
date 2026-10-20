# Thai Humanizer V3 Evaluation Rubric

This file is for evaluators. It is **not** needed for rewriting, and it intentionally contains **no benchmark tasks, reference answers, or scores**. Historical benchmark tasks and reference answers used up to V2.1 (including the October 2026 T01–T10 run) were moved out of the installed Skill into a separate evaluation workspace (`~/thai-humanizer-eval/`) and are frozen as development evidence. They must not be reused as held-out data.

The rubric below is frozen for V3. **Do not change it after seeing evaluation results.** If it must change, version it (V3.1 rubric) and re-score everything under the new version.

---

## 1. Gates (pass/fail, scored separately from quality)

| Gate | Pass | Fail |
| :--- | :--- | :--- |
| **Factual validity** | Every material fact from the source is present, correct, and attached to the right entity (prices, dates, actors, conditions, negations, certainty, status, technical strings). Nothing unsupported is added. | Any confirmed distortion: changed/swapped value, dropped condition or limitation, reversed negation, wrong actor, upgraded certainty or status, invented reason, capability, testimonial, or personal story. |
| **Format** | Required structure preserved (headings, lists, code, tables, slide markers, email parts) unless the user asked to change it. | Structure needed by the reader was removed or code/commands were altered. |

An output that fails the factual gate is reported as a failure regardless of its quality scores. Report gate failures as counts, with the specific distortion.

## 2. Quality dimensions (1–5 each)

Same five dimensions as the October 2026 run, so totals remain comparable (5 dims × 5 points per task).

| Dimension | 5 | 3 | 1 |
| :--- | :--- | :--- | :--- |
| **Naturalness** | Reads like a skilled native writer of this genre wrote it; no translated syntax or AI tics. | Mostly natural; a few stiff or formulaic spots. | Clearly machine-like or translated. |
| **Fluency** | Smooth rhythm, good transitions, easy to read (or to say aloud, for speech). | Readable with some awkward joins. | Hard to follow. |
| **Contextual appropriateness** | Register, voice, opening, ending, and format fit the category, audience, and author. | Partly fits; some register mismatch (e.g. formal closing on a casual post). | Wrong genre or voice. |
| **Conciseness** | No padding; nothing important cut; length fits purpose. | Some padding or some over-cutting. | Bloated, or important content dropped. |
| **Minimal unnecessary editing** | Changes are all justified; good parts left alone; already-natural input essentially unchanged. | Some unnecessary churn. | Rewrote good text for no reason, or changed the author's voice. |

Score anchors 2 and 4 are in between. Evaluators should note one sentence of reason for any score ≤ 3.

## 3. Pairwise preference

For each task, after scoring both outputs, record which output the evaluator would rather send to the intended audience: option 1, option 2, or tie. Preference is recorded independently of the totals.

## 4. Reporting requirements

- Number of tasks per category, number of evaluators, and how prompts were sourced.
- Means with 95% confidence intervals; win/loss/tie counts; non-tied win rate with Wilson 95% CI; sign-test p-value.
- Factual-gate failures for each condition, listed individually.
- Inter-rater agreement where more than one evaluator scored the same task.
- Any deviation from the protocol (host change, model setting change, re-runs).

## 5. Limits

- Automated checks (`scripts/check_preservation.py`) are a screening aid for the factual gate. They do not replace a human reading source and output side by side.
- Unit tests prove checker behaviour, not writing quality.
- A historical score (e.g. 219/250 or any higher number on the old tasks) is not an acceptance criterion for V3.
