# Installing MANUD

## Recommended: one command

```bash
npx skills add 0xrutabaga/manud
```

- Needs **Node.js 22.20 or newer**. Uses the [Skills CLI](https://github.com/vercel-labs/skills); nothing else is installed, and MANUD itself needs no Node.js.
- It normally lets you choose which agents to install for. To skip the questions: `npx skills add 0xrutabaga/manud -a claude-code codex -y`.
- **Project vs. global:** without flags it installs into the current project; add `-g` to install for your user (all projects).
- It installs the whole `manud` folder (`SKILL.md`, `references/`, `scripts/`, `examples/`, `tests/`, `LICENSE`). The files go once into `.agents/skills/manud`; for Claude Code the CLI adds a link at `.claude/skills/manud` (a junction on Windows). Add `--copy` to get plain copies instead of links.
- It also writes `skills-lock.json` in a project, recording where the Skill came from.

| Agent | Project | Global (`-g`) |
| :-- | :-- | :-- |
| Claude Code | `.claude/skills/manud` → link to `.agents/skills/manud` | `~/.claude/skills/manud` → link to `~/.agents/skills/manud` |
| Codex | `.agents/skills/manud` | `~/.agents/skills/manud` |
| Google Antigravity | `.agents/skills/manud` | `~/.agents/skills/manud` (see below) |

Paths are what Skills CLI 1.7.0 produced in testing; other CLI versions may differ.

**Update:** run the same `npx skills add 0xrutabaga/manud …` command again; it overwrites the installed copy. (`npx skills update manud` is meant to do the same, but it hasn't been tested yet.)
**Remove:** `npx skills remove manud` (add `-g` for a global install).

### Antigravity

The CLI puts Antigravity's global install in `~/.agents/skills`. Whether your Antigravity version reads that folder depends on the version; different Antigravity versions are reported to use `~/.gemini/config/skills`, `~/.gemini/antigravity/skills` or `~/.gemini/antigravity-cli/skills`. If MANUD doesn't show up, use a project install (`.agents/skills`), or copy the folder into your version's global skills folder (see [Manual install](#manual-install)). Antigravity hasn't been tested with MANUD yet.

## Manual install

Use this if you don't have Node.js.

1. Download the repository as a ZIP from GitHub (green **Code** button → **Download ZIP**) and unpack it.
2. Copy the folder `skills/manud` (the whole folder, keeping the name `manud`) into one of:

| Agent | Personal (all projects) | One project |
| :-- | :-- | :-- |
| Claude Code | `~/.claude/skills/` | `<project>/.claude/skills/` |
| Codex | `~/.agents/skills/` | `<repo>/.agents/skills/` |
| Antigravity | your version's global skills folder (above) | `<workspace>/.agents/skills/` |

Windows PowerShell example (Claude Code, personal):

```powershell
Copy-Item -Recurse .\manud-main\skills\manud "$HOME\.claude\skills\manud"
```

## Check it works

Start a **new** agent session and ask: "ช่วยเกลาข้อความนี้ให้อ่านเป็นธรรมชาติ: …". To call it by name: `/manud` in Claude Code, `$manud` in Codex.

Optional self-test, if you have Python 3:

```bash
python <skills-folder>/manud/scripts/validate_skill.py <skills-folder>/manud
```

## Troubleshooting

| Problem | Fix |
| :-- | :-- |
| `npx` not found, or the CLI complains about the Node version | Install Node.js 22.20+, or use the [manual install](#manual-install) |
| The agent doesn't use MANUD | Start a new session; check that the folder is named exactly `manud` and contains `SKILL.md`; call it by name (`/manud`, `$manud`) |
| The agent uses the old `thai-humanizer` | Both are installed. Remove `thai-humanizer` (see [MIGRATION.md](MIGRATION.md)); in Claude Code you can also turn it off with `"skillOverrides": {"thai-humanizer": "off"}` |
| Windows: link not created / permission error | Re-run with `--copy` |
| Antigravity doesn't see it | See [Antigravity](#antigravity) |

## What was tested before release (2026-10-20)

Skills CLI 1.7.0 on Windows 11, installing from a local copy of this repository (including a git-clone source with `core.autocrlf=true`):

- project and global install, reinstall (update) and removal: OK; all 40 Skill files byte-identical after install;
- an existing `thai-humanizer` folder was not touched by install or removal;
- after install, Claude Code 2.1.302 and Codex CLI 0.161.0 both listed `manud`. In earlier runs, Claude Code used it for a plain Thai request, and Codex used it when named (`$manud`);
- **not yet tested:** installing from GitHub (`0xrutabaga/manud`), `npx skills update`, Linux and macOS (covered by the repository's CI tests once it's public), and Antigravity.
