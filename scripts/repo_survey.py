#!/usr/bin/env python3
"""repo_survey — a fast, dependency-free lay of the land for a code repository.

Usage:
    python3 repo_survey.py <repo-path> [--max-tree-entries N] [--top-langs N]

Prints, to stdout:
  * a language / lines-of-code breakdown by file extension
  * a pruned file tree (skips vcs, deps, build artifacts, caches)
  * candidate entry points (main functions, CLI definitions, package mains, web bootstraps)
  * build / config files present
  * dependency manifests found (and their raw contents are pointed to, not dumped)

This is orientation only — it tells you where to *look*, not what the code means. Read the
README, the entry points, and the core types yourself afterward. The goal of the survey is to
let you reconstruct a *reading order*; it does not produce one for you.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

# Directories never worth walking into.
SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "vendor", "dist", "build", "out", "target",
    ".venv", "venv", "env", "__pycache__", ".mypy_cache", ".pytest_cache", ".tox",
    ".idea", ".vscode", ".gradle", ".next", ".nuxt", "coverage", ".cache", "bin", "obj",
    "Pods", "DerivedData", ".terraform", "site-packages", ".eggs",
}

# Extension -> language label, for the LOC breakdown.
LANGS = {
    ".py": "Python", ".pyi": "Python", ".ipynb": "Jupyter",
    ".c": "C", ".h": "C/C++ header", ".hpp": "C++ header", ".hh": "C++ header",
    ".cc": "C++", ".cpp": "C++", ".cxx": "C++", ".m": "Obj-C", ".mm": "Obj-C++",
    ".rs": "Rust", ".go": "Go", ".java": "Java", ".kt": "Kotlin", ".scala": "Scala",
    ".js": "JavaScript", ".jsx": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".rb": "Ruby", ".php": "PHP", ".swift": "Swift", ".cs": "C#", ".fs": "F#",
    ".hs": "Haskell", ".ml": "OCaml", ".ex": "Elixir", ".exs": "Elixir", ".erl": "Erlang",
    ".clj": "Clojure", ".lua": "Lua", ".jl": "Julia", ".r": "R", ".dart": "Dart",
    ".sh": "Shell", ".bash": "Shell", ".zig": "Zig", ".nim": "Nim", ".pl": "Perl",
    ".sql": "SQL", ".css": "CSS", ".scss": "CSS", ".html": "HTML", ".vue": "Vue",
    ".md": "Markdown", ".rst": "reStructuredText", ".tex": "TeX",
    ".toml": "config", ".yaml": "config", ".yml": "config", ".json": "config",
    ".proto": "Protobuf",
}

# Files that signal the build system / project config.
BUILD_FILES = {
    "Makefile", "makefile", "CMakeLists.txt", "configure", "meson.build", "BUILD",
    "BUILD.bazel", "WORKSPACE", "build.gradle", "build.gradle.kts", "pom.xml", "build.sbt",
    "Cargo.toml", "go.mod", "package.json", "pnpm-workspace.yaml", "tsconfig.json",
    "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile", "poetry.lock",
    "Gemfile", "composer.json", "mix.exs", "Dockerfile", "docker-compose.yml",
    "flake.nix", "default.nix", "justfile", "Taskfile.yml",
}
MANIFESTS = {
    "package.json", "Cargo.toml", "go.mod", "pyproject.toml", "requirements.txt",
    "setup.py", "Gemfile", "composer.json", "pom.xml", "build.gradle", "mix.exs", "Pipfile",
}
DOC_HINTS = {"README", "ARCHITECTURE", "CONTRIBUTING", "DESIGN", "OVERVIEW", "HACKING"}

# Heuristic patterns for entry points, keyed by extension family.
# MULTILINE so `^` matches the start of any line, not just the file.
_M = re.MULTILINE
ENTRY_PATTERNS = [
    (re.compile(r"^\s*(int|void)\s+main\s*\(", _M), "C/C++-style main()"),
    (re.compile(r"^\s*fn\s+main\s*\(", _M), "Rust main()"),
    (re.compile(r"^\s*func\s+main\s*\(", _M), "Go main()"),
    (re.compile(r'if\s+__name__\s*==\s*[\'"]__main__[\'"]', _M), "Python __main__ guard"),
    (re.compile(r"public\s+static\s+void\s+main\s*\(", _M), "Java main()"),
    (re.compile(r"\bapp\s*=\s*(Flask|FastAPI)\(", _M), "Python web app bootstrap"),
    (re.compile(r"\b(createServer|app\.listen)\s*\(", _M), "Node server bootstrap"),
    (re.compile(r"\bArgumentParser\s*\(|\bclick\.command\b|\bcommander\b", _M), "CLI definition"),
]
SCANNABLE = {
    ".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".rs", ".go", ".py", ".java",
    ".js", ".jsx", ".ts", ".tsx", ".rb",
}
MAX_SCAN_BYTES = 200_000  # don't read huge generated files line by line


def human(n: int) -> str:
    return f"{n:,}"


def count_lines(path: str) -> int:
    try:
        with open(path, "rb") as f:
            return sum(1 for _ in f)
    except Exception:  # noqa: BLE001
        return 0


def walk(root: str):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".git"))
        for fn in sorted(filenames):
            yield dirpath, fn


def survey(root: str, max_tree: int, top_langs: int) -> None:
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        print(f"error: {root} is not a directory", file=sys.stderr)
        raise SystemExit(1)

    loc_by_lang: dict[str, int] = {}
    files_by_lang: dict[str, int] = {}
    total_files = 0
    build_present: list[str] = []
    manifests_present: list[str] = []
    docs_present: list[str] = []
    entry_points: list[tuple[str, str]] = []
    tree_lines: list[str] = []

    for dirpath, fn in walk(root):
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, root)
        total_files += 1

        ext = os.path.splitext(fn)[1].lower()
        lang = LANGS.get(ext)
        if lang:
            n = count_lines(full)
            loc_by_lang[lang] = loc_by_lang.get(lang, 0) + n
            files_by_lang[lang] = files_by_lang.get(lang, 0) + 1

        if fn in BUILD_FILES:
            build_present.append(rel)
        if fn in MANIFESTS:
            manifests_present.append(rel)
        base = os.path.splitext(fn)[0].upper()
        if base in DOC_HINTS:
            docs_present.append(rel)

        if ext in SCANNABLE:
            try:
                size = os.path.getsize(full)
                if size <= MAX_SCAN_BYTES:
                    with open(full, encoding="utf-8", errors="ignore") as f:
                        head = f.read(MAX_SCAN_BYTES)
                    for pat, label in ENTRY_PATTERNS:
                        if pat.search(head):
                            entry_points.append((rel, label))
                            break
            except Exception:  # noqa: BLE001
                pass

        if len(tree_lines) < max_tree:
            depth = rel.count(os.sep)
            tree_lines.append("  " * depth + ("📄 " if depth else "") + rel)

    # ---- print report -------------------------------------------------------
    name = os.path.basename(root)
    bar = "=" * 70
    print(bar)
    print(f"REPO SURVEY: {name}")
    print(f"  path: {root}")
    print(f"  total files (after pruning vendor/build/vcs): {human(total_files)}")
    print(bar)

    print("\nLANGUAGES (by lines of code):")
    ranked = sorted(loc_by_lang.items(), key=lambda kv: -kv[1])
    if not ranked:
        print("  (no recognized source files)")
    for lang, n in ranked[:top_langs]:
        print(f"  {lang:<18} {human(n):>10} loc   ({files_by_lang[lang]} files)")
    if len(ranked) > top_langs:
        print(f"  … and {len(ranked) - top_langs} more language(s)")

    print("\nLIKELY PRIMARY LANGUAGE:",
          ranked[0][0] if ranked else "unknown",
          "→ pick your notebook code-cell strategy accordingly (see SKILL.md Phase 3).")

    print("\nDOCS TO READ FIRST:")
    for d in docs_present or ["  (none found — rely on entry points and core types)"]:
        print(f"  {d}" if d.strip().startswith("(") is False else d)

    print("\nBUILD / PROJECT CONFIG:")
    for b in sorted(set(build_present)) or ["  (none found)"]:
        print(f"  {b}" if not b.startswith("  ") else b)

    print("\nDEPENDENCY MANIFESTS (read these for the external surface):")
    for m in sorted(set(manifests_present)) or ["  (none found)"]:
        print(f"  {m}" if not m.startswith("  ") else m)

    print("\nCANDIDATE ENTRY POINTS (start your reading order here):")
    if entry_points:
        for rel, label in entry_points[:40]:
            print(f"  {rel:<48} — {label}")
        if len(entry_points) > 40:
            print(f"  … and {len(entry_points) - 40} more")
    else:
        print("  (none detected by heuristic — look at the manifest's declared bin/main,")
        print("   or the largest/most-imported module)")

    print(f"\nFILE TREE (first {min(max_tree, len(tree_lines))} entries, pruned):")
    for line in tree_lines:
        print("  " + line)
    if total_files > max_tree:
        print(f"  … ({human(total_files - max_tree)} more entries not shown; raise --max-tree-entries)")

    print("\n" + bar)
    print("NEXT: read the docs and entry points above, identify the core data types, then write")
    print("an orientation memo and design the spine (reading order). See SKILL.md Phases 1–2.")
    print(bar)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fast repo orientation for a literate reading.")
    ap.add_argument("repo", help="path to the repository root")
    ap.add_argument("--max-tree-entries", type=int, default=200)
    ap.add_argument("--top-langs", type=int, default=12)
    args = ap.parse_args()
    survey(args.repo, args.max_tree_entries, args.top_langs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
