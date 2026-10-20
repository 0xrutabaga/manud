# Optional Apple Silicon inference with HumanizerTH (MLX)

This step is optional. `SKILL.md` runs with the host LLM alone and requires no additional model. Do **not** install packages, contact Hugging Face, or download multi-GB weights without the user's explicit consent.

Model pages checked at project creation:

- Q4: https://huggingface.co/chantra/humanizerth-thai-12B-Q4_0-MLX
- Q8: https://huggingface.co/chantra/humanizerth-thai-12B-Q8_0-MLX

The publisher reports Q4 at around 6.3 GB of files (the Hub also displays a rounded footprint), and reports roughly 7–9 GB inference peak memory. **8 GB physical unified memory is tight, not a guarantee of comfortable usage**. Actual speed and memory depend on hardware, prompt length, system load, and `mlx-lm` version. Q8 needs substantially more memory. Neither model is included in this repository. Model card metrics are publisher-reported, not independently verified in this project.

## Setup (macOS Apple Silicon)

Recommended: create a dedicated Python environment, then install MLX LM.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip mlx-lm
```

Try model interactively (the first run may download several GB):

```bash
mlx_lm.chat --model chantra/humanizerth-thai-12B-Q4_0-MLX
```

To rewrite a UTF-8 file through a small optional wrapper (requires Python plus `mlx-lm`):

```bash
python scripts/run_local_mlx.py examples/before.txt /tmp/thai-rewrite.txt --variant q4
python scripts/check_preservation.py examples/before.txt /tmp/thai-rewrite.txt --terms-file examples/protected_terms.txt
```

Only use the rewritten text after a **human/agent semantic comparison** confirms claims, negations, names, quoted material, and all relevant facts. A numeric check alone is insufficient. When check fails, correct the output or retain the original.

## Licensing, privacy and safety

- The model repositories list a `gemma` license. Do not redistribute the weights under the MIT license for this skill.
- Review the base-model and upstream terms before commercial or redistributed use.
- First download involves network access; subsequent local inference need not send text to a third-party service, subject to environment and telemetry behavior.
- Do not feed proprietary or personal text to a network service unless authorized.
- Downloading/running a model and using a Skill are different steps; the Agent will not automatically have an MLX tool just because a markdown file mentions it.
