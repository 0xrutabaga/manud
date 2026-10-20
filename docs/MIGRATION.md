# Migrating from `thai-humanizer` to `manud`

MANUD 3.1.0 is Thai Humanizer V3.0.0 under a new name. **The editing instructions in `SKILL.md` are byte-identical.** Only the frontmatter (`name`, `metadata.version`, two new metadata keys), the checker's `VERSION` constant, the Skill folder's README and the changelog differ.

## What changes for you

| | Before | After |
| :-- | :-- | :-- |
| Folder | `…/skills/thai-humanizer/` | `…/skills/manud/` |
| Skill name / command | `thai-humanizer` (`/thai-humanizer` in Claude Code) | `manud` (`/manud`) |
| Checker | `check_preservation 3.0.0` | `check_preservation 3.1.0` (same checks, same exit codes, same JSON keys) |

Prompts that don't name the Skill ("make this Thai sound natural") keep working: agents choose the Skill by its description, which is unchanged.

## Recommended steps

1. **Install `manud`** with `npx skills add 0xrutabaga/manud` or by copying the folder (see [INSTALL.md](INSTALL.md)). Neither method touches an existing `thai-humanizer` folder (checked before release).
2. **Try it** on a text you know, in a new agent session.
3. **Disable or archive `thai-humanizer`** once MANUD works: remove it from every skills folder that has it (personal and project), or move it somewhere outside those folders. Keeping both is **not** recommended: they have the same description, so an agent may load either one. In a pre-release test with both installed, Claude Code chose the old `thai-humanizer`. In Claude Code you can also turn the old Skill off without deleting it: add `"skillOverrides": {"thai-humanizer": "off"}` to your settings.
4. Update scripts, docs or team instructions that call `/thai-humanizer` or point to the old folder path.

To roll back, delete `manud` and restore your backup copy of the `thai-humanizer` folder. Keep that backup until you're happy with `manud`. The Skill stores no settings or data outside its folder.

## Why there is no compatibility alias

An extra `thai-humanizer` stub Skill that forwards to `manud` was considered and rejected. Agents pick Skills by description, so a stub either competes with `manud` (same description) or is never chosen (different description). A clean replacement is more predictable.

## Name clash note

A different, unrelated project also publishes a Skill named `thai-humanizer` (`citelogics-th/thai-humanizer`, MIT). The rename to `manud` also avoids confusion with it. If you installed that Skill, it isn't affected by this migration.
