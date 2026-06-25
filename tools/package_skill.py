#!/usr/bin/env python3
"""Package this repository into an installable `.skill` file (a zip archive).

A `.skill` is simply a zip whose top-level folder is the skill, with `SKILL.md` at its root. This
script is self-contained — it needs only the Python standard library — so the repository does not
depend on any external tooling to produce a distributable skill.

Usage:
    python3 tools/package_skill.py            # writes dist/<name>.skill
    python3 tools/package_skill.py ./out      # writes ./out/<name>.skill

What goes in the .skill: SKILL.md, README.md, LICENSE, references/, scripts/, demo/.
What stays out (repo/dev scaffolding): .git, .github, .gitignore, Makefile, tools/, dist/, and the
usual caches. The top-level folder inside the archive is taken from the `name:` in SKILL.md so the
installed skill is named correctly regardless of the checkout directory's name.
"""
from __future__ import annotations

import os
import sys
import zipfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path prefixes (relative to repo root) that are repo scaffolding, not skill payload.
EXCLUDE_TOP = {".git", ".github", ".gitignore", "Makefile", "tools", "dist", ".venv", "venv"}
EXCLUDE_DIR_NAMES = {"__pycache__", "node_modules", ".ipynb_checkpoints", ".pytest_cache",
                     ".mypy_cache"}
EXCLUDE_FILE_GLOBS = ("*.pyc", ".DS_Store")


def _read_skill_name(skill_md: str) -> str:
    """Pull the `name:` field out of the SKILL.md YAML frontmatter."""
    with open(skill_md, encoding="utf-8") as f:
        text = f.read()
    if not text.startswith("---"):
        raise SystemExit("SKILL.md has no YAML frontmatter")
    end = text.find("\n---", 3)
    front = text[3:end]
    for line in front.splitlines():
        if line.strip().startswith("name:"):
            return line.split(":", 1)[1].strip()
    raise SystemExit("SKILL.md frontmatter has no 'name:' field")


def _validate(skill_md: str, name: str) -> None:
    """Minimal validation mirroring the install-time checks."""
    with open(skill_md, encoding="utf-8") as f:
        text = f.read()
    end = text.find("\n---", 3)
    front = text[3:end]
    # description may be a YAML folded block; join continuation lines for a length check.
    desc_lines, in_desc = [], False
    for line in front.splitlines():
        if line.startswith("description:"):
            in_desc = True
            rest = line.split(":", 1)[1].strip()
            if rest and rest != ">":
                desc_lines.append(rest)
            continue
        if in_desc:
            if line and not line[0].isspace():
                break
            desc_lines.append(line.strip())
    desc = " ".join(s for s in desc_lines if s)
    if not name:
        raise SystemExit("validation failed: empty skill name")
    if len(desc) > 1024:
        raise SystemExit(f"validation failed: description is {len(desc)} chars (max 1024)")
    print(f"validated: name={name!r}, description={len(desc)} chars")


def _excluded(rel: str) -> bool:
    parts = rel.split(os.sep)
    if parts[0] in EXCLUDE_TOP:
        return True
    if any(p in EXCLUDE_DIR_NAMES for p in parts):
        return True
    base = parts[-1]
    if base == ".DS_Store" or base.endswith(".pyc"):
        return True
    return False


def package(output_dir: str) -> str:
    skill_md = os.path.join(REPO_ROOT, "SKILL.md")
    if not os.path.isfile(skill_md):
        raise SystemExit("SKILL.md not found at repo root")
    name = _read_skill_name(skill_md)
    _validate(skill_md, name)

    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(os.path.abspath(output_dir), f"{name}.skill")

    added = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if not _excluded(
                os.path.relpath(os.path.join(root, d), REPO_ROOT))]
            for fn in files:
                full = os.path.join(root, fn)
                rel = os.path.relpath(full, REPO_ROOT)
                if _excluded(rel):
                    continue
                z.write(full, os.path.join(name, rel))  # prefix with the skill name
                added += 1
    print(f"packaged {added} files -> {out}")
    return out


if __name__ == "__main__":
    package(sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, "dist"))
