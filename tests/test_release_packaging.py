"""Release packaging and Skills CLI installation tests for the MANUD repository.

Run from the repository root:

    python -m unittest discover -s tests -v

PackagingTests need only Python. SkillsCliTests also need Node.js (npx) and network access to
the npm registry; they install into temporary folders with HOME/USERPROFILE redirected, so they
never touch your real skills folders. Set MANUD_SKIP_CLI=1 to skip them, and MANUD_SKILLS_CLI to
choose the CLI version (default below).
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "manud"
MASCOT = ROOT / "assets" / "brand" / "mascot-v1.0"
CLI = os.environ.get("MANUD_SKILLS_CLI", "skills@1.7.0")
NPX = shutil.which("npx")


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def tree_hashes(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): sha256(p) for p in sorted(root.rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts}


class PackagingTests(unittest.TestCase):
    def test_exactly_one_skill_is_discoverable(self):
        found = [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("SKILL.md")
                 if ".git" not in p.parts]
        self.assertEqual(found, ["skills/manud/SKILL.md"])

    def test_frontmatter_name_matches_folder(self):
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        fm = text.split("---")[1]
        self.assertRegex(fm, r"(?m)^name: manud$")
        desc = re.search(r"(?m)^description: (.+)$", fm).group(1)
        self.assertLessEqual(len(desc), 1024)

    def test_operational_files_ship_inside_the_skill_folder(self):
        # every relative link in SKILL.md must resolve inside skills/manud/, so an installer that
        # copies only that folder still delivers the references the instructions point to
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\(([^)#\s]+)", text)
        self.assertTrue(links)
        for link in links:
            if "://" in link:
                continue
            target = (SKILL / link).resolve()
            self.assertTrue(target.is_file(), link)
            self.assertTrue(str(target).startswith(str(SKILL.resolve())), link)
        for needed in ("references", "scripts", "examples", "tests", "LICENSE"):
            self.assertTrue((SKILL / needed).exists(), needed)

    def test_mascot_hashes(self):
        for line in (MASCOT / "SHA256SUMS").read_text().splitlines():
            digest, name = line.split(maxsplit=1)
            self.assertEqual(sha256(MASCOT / name.lstrip("*")), digest, name)

    def test_gitattributes_protect_hashed_trees(self):
        attrs = (ROOT / ".gitattributes").read_text()
        self.assertIn("assets/brand/mascot-v1.0/** -text", attrs)
        self.assertIn("skills/manud/** -text", attrs)


@unittest.skipIf(os.environ.get("MANUD_SKIP_CLI") == "1" or not NPX, "Skills CLI tests skipped (MANUD_SKIP_CLI=1 or no npx)")
class SkillsCliTests(unittest.TestCase):
    """Install / reinstall / remove through the Skills CLI, from a local copy of this repository."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="manud-install-"))
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.src = self.tmp / "src"
        shutil.copytree(ROOT, self.src, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        self.env = dict(os.environ, HOME=str(self.home), USERPROFILE=str(self.home),
                        DO_NOT_TRACK="1", DISABLE_TELEMETRY="1")
        self.expected = tree_hashes(SKILL)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def cli(self, *args, cwd):
        r = subprocess.run([NPX, "-y", CLI, *args], cwd=cwd, env=self.env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=300)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return re.sub(r"\x1b\[[0-9;?]*[a-zA-Z]", "", r.stdout + r.stderr)

    def assert_installed(self, base: Path):
        canonical = base / ".agents" / "skills" / "manud"
        self.assertEqual(tree_hashes(canonical), self.expected)
        claude = base / ".claude" / "skills" / "manud"  # symlink/junction or copy
        self.assertTrue((claude / "SKILL.md").is_file())
        self.assertEqual(tree_hashes(claude), self.expected)

    def test_list_finds_only_manud(self):
        out = self.cli("add", str(self.src), "--list", cwd=self.tmp)
        self.assertIn("manud", out)
        self.assertRegex(out, r"Found\s+1\s+skill")

    def test_project_install_reinstall_remove(self):
        proj = self.tmp / "proj"
        proj.mkdir()
        self.cli("add", str(self.src), "--skill", "manud", "-a", "claude-code", "codex", "-y", cwd=proj)
        self.assert_installed(proj)
        # reinstall from a changed source = the update path for local sources
        readme = self.src / "skills" / "manud" / "README.md"
        readme.write_text(readme.read_text(encoding="utf-8") + "\n<!-- reinstall marker -->\n",
                          encoding="utf-8", newline="\n")
        self.cli("add", str(self.src), "--skill", "manud", "-a", "claude-code", "codex", "-y", cwd=proj)
        self.assertIn("reinstall marker", (proj / ".agents/skills/manud/README.md").read_text(encoding="utf-8"))
        self.cli("remove", "manud", "-a", "claude-code", "codex", "-y", cwd=proj)
        self.assertFalse((proj / ".agents/skills/manud").exists())
        self.assertFalse(os.path.lexists(proj / ".claude/skills/manud"))

    def test_global_install_leaves_thai_humanizer_untouched(self):
        old = {}
        for d in (".claude/skills/thai-humanizer", ".agents/skills/thai-humanizer"):
            p = self.home / d
            p.mkdir(parents=True)
            (p / "SKILL.md").write_text("---\nname: thai-humanizer\ndescription: old\n---\nold\n", encoding="utf-8")
            old[d] = tree_hashes(p)
        work = self.tmp / "elsewhere"
        work.mkdir()
        self.cli("add", str(self.src), "--skill", "manud", "-g", "-a", "claude-code", "codex", "-y", cwd=work)
        self.assert_installed(self.home)
        self.cli("remove", "manud", "-g", "-a", "claude-code", "codex", "-y", cwd=work)
        self.assertFalse(os.path.lexists(self.home / ".claude/skills/manud"))
        self.assertFalse((self.home / ".agents/skills/manud").exists())
        for d, h in old.items():
            self.assertEqual(tree_hashes(self.home / d), h, d)


if __name__ == "__main__":
    unittest.main()
