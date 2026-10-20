#!/usr/bin/env python3
"""Validate the Thai Humanizer Skill folder structure and documentation.

Checks:
  - SKILL.md frontmatter: name (matches folder, kebab-case, <= 64 chars), description
    (non-empty, <= 1024 chars, no angle brackets), license, metadata.version
  - SKILL.md body length (<= 500 lines)
  - Every relative Markdown link in SKILL.md, README.md, CHANGELOG.md, references/*.md resolves
  - Version consistency: SKILL.md metadata.version == checker VERSION == newest CHANGELOG entry
  - Evaluation isolation: no KEY.json / holdout material inside the Skill, and historical
    benchmark names do not appear in SKILL.md or references/ (allowed only in examples/ and
    tests/ as legacy development fixtures)

Usage: python scripts/validate_skill.py [skill_dir]
Exit 0 = valid, 1 = problems found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
BENCHMARK_NAMES = ("TaskNest", "Slow Morning Cafe")


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---", 4)
    if end < 0:
        return {}, text
    meta: dict[str, str] = {}
    parent = ""
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        m = re.match(r"^(\s*)([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        indent, key, value = m.groups()
        value = value.strip().strip('"').strip("'")
        if indent:
            meta[f"{parent}.{key}"] = value
        else:
            parent = key
            meta[key] = value
    return meta, text[end + 4:]


def validate(root: Path) -> list[str]:
    problems: list[str] = []
    skill = root / "SKILL.md"
    if not skill.is_file():
        return ["SKILL.md is missing"]
    meta, body = parse_frontmatter(skill.read_text(encoding="utf-8"))
    name = meta.get("name", "")
    if not name:
        problems.append("frontmatter: name missing")
    elif not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        problems.append(f"frontmatter: invalid name {name!r}")
    elif name != root.resolve().name:
        problems.append(f"frontmatter: name {name!r} does not match folder {root.resolve().name!r}")
    desc = meta.get("description", "")
    if not desc:
        problems.append("frontmatter: description missing")
    elif len(desc) > 1024:
        problems.append(f"frontmatter: description is {len(desc)} chars (> 1024)")
    elif "<" in desc or ">" in desc:
        problems.append("frontmatter: description contains angle brackets")
    if not meta.get("license"):
        problems.append("frontmatter: license missing")
    version = meta.get("metadata.version", "")
    if not version:
        problems.append("frontmatter: metadata.version missing")
    if len(body.splitlines()) > 500:
        problems.append(f"SKILL.md body is {len(body.splitlines())} lines (> 500)")

    docs = [root / "SKILL.md", root / "README.md", root / "CHANGELOG.md", *sorted((root / "references").glob("*.md"))]
    for doc in docs:
        if not doc.is_file():
            problems.append(f"missing document: {doc.relative_to(root)}")
            continue
        text = re.sub(r"```.*?```", "", doc.read_text(encoding="utf-8"), flags=re.DOTALL)
        for target in LINK.findall(text):
            if re.match(r"^[a-z]+://|^mailto:|^#", target):
                continue
            path = (doc.parent / target.split("#", 1)[0]).resolve()
            if not path.exists():
                problems.append(f"broken link in {doc.relative_to(root)}: {target}")

    checker = root / "scripts" / "check_preservation.py"
    m = re.search(r'^VERSION = "([^"]+)"', checker.read_text(encoding="utf-8"), re.MULTILINE) if checker.is_file() else None
    if not m:
        problems.append("scripts/check_preservation.py: VERSION constant missing")
    elif version and m.group(1) != version:
        problems.append(f"version mismatch: SKILL.md {version} vs checker {m.group(1)}")
    changelog = root / "CHANGELOG.md"
    if changelog.is_file():
        c = re.search(r"^##\s*\[?v?([0-9][^\]\s]*)", changelog.read_text(encoding="utf-8"), re.MULTILINE)
        if not c:
            problems.append("CHANGELOG.md: no version heading found")
        elif version and c.group(1) != version:
            problems.append(f"version mismatch: SKILL.md {version} vs CHANGELOG {c.group(1)}")

    for bad in list(root.rglob("KEY.json")) + [p for p in root.rglob("*") if p.is_dir() and p.name.lower() == "holdout"]:
        problems.append(f"evaluation isolation: {bad.relative_to(root)} must not live inside the Skill")
    for doc in [root / "SKILL.md", *sorted((root / "references").glob("*.md"))]:
        text = doc.read_text(encoding="utf-8") if doc.is_file() else ""
        for name_ in BENCHMARK_NAMES:
            if name_ in text:
                problems.append(f"evaluation isolation: historical benchmark {name_!r} referenced in {doc.relative_to(root)}")
    return problems


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    problems = validate(root)
    if problems:
        print("INVALID:")
        for p in problems:
            print(f" - {p}")
        return 1
    print(f"VALID: {root.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
