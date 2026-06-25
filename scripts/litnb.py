#!/usr/bin/env python3
"""litnb — build and validate Jupyter notebooks for literate-programming repo readings.

Dependency-free: writes nbformat 4.5 JSON directly, so it works even when `nbformat`/`jupyter`
are not installed. If `nbformat` *is* present, `--check` uses it for stricter validation.

As a library (the normal use, from a chapter-building script):

    import sys; sys.path.insert(0, "<skill>/scripts")
    import litnb
    cells = [
        litnb.md("# Chapter 1", "", "Prose paragraph ...",
                 "```cpp", "// src/x.cpp:1-3", "int main(){}", "```"),
        litnb.code("print('a runnable demonstration cell')"),
    ]
    litnb.build(cells, "out/01_overview.ipynb", title="Overview")

Helpers:
    litnb.md(*lines)            -> a markdown cell (lines joined by "\n")
    litnb.code(src, outputs=[]) -> a code cell
    litnb.fragment_use(name, s) -> "⟨name s⟩"        (a fragment reference)
    litnb.fragment_def(name, s) -> "⟨name s⟩ ≡"      (a fragment definition header)
    litnb.SourceLinker.from_git(repo_path, notebooks_dir)  -> clickable source links
    litnb.build(cells, path, title=None, kernel="python3", language=None)

Clickable code links — every excerpt should be preceded by a link to the file/lines it came from:
    link = litnb.SourceLinker.from_git(repo_path, notebooks_dir="out")
    link.link("/abs/path/file.py", 43, 55)   # -> "[`file.py` lines 43–55](https://…/blob/<sha>/…#L43-L55)"
On GitHub/GitLab/Bitbucket repos this yields line-precise permalinks; with no remote it falls back
to a relative file link that still opens the file in Jupyter.

As a CLI:
    python3 litnb.py --check <file-or-dir>   # validate one notebook or every .ipynb in a tree
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid

NBFORMAT = 4
NBFORMAT_MINOR = 5


def _cell_id() -> str:
    return uuid.uuid4().hex[:12]


def _split_source(text: str) -> list[str]:
    """nbformat stores source as a list of lines, each (except the last) ending in '\n'."""
    if text == "":
        return []
    lines = text.splitlines(keepends=True)
    return lines


def md(*lines: str) -> dict:
    """A markdown cell. Pass any number of strings; they are joined with newlines."""
    text = "\n".join(lines)
    return {
        "cell_type": "markdown",
        "id": _cell_id(),
        "metadata": {},
        "source": _split_source(text),
    }


def code(src: str = "", outputs: list | None = None, execution_count=None) -> dict:
    """A code cell. `src` is the cell's code; `outputs` is an optional list of output dicts."""
    return {
        "cell_type": "code",
        "id": _cell_id(),
        "metadata": {},
        "execution_count": execution_count,
        "outputs": outputs or [],
        "source": _split_source(src),
    }


def fragment_use(name: str, section: str) -> str:
    """Reference to a fragment defined elsewhere, e.g. fragment_use('Render the image','2.1')."""
    return f"\u27e8{name} {section}\u27e9"


def fragment_def(name: str, section: str) -> str:
    """Header line that defines a fragment, e.g. '⟨Render the image 2.1⟩ ≡'."""
    return f"\u27e8{name} {section}\u27e9 \u2261"


# ----------------------------------------------------------------- clickable source links
#
# Every code reference in a literate reading should be a *clickable link* to the exact file (and,
# when the host allows, the exact lines). `SourceLinker` builds those links. Prefer
# `SourceLinker.from_git(repo_path, notebooks_dir)`: it inspects the repo's git remote and HEAD
# commit and produces line-precise permalinks on GitHub/GitLab/Bitbucket; with no usable remote it
# falls back to a relative file link from the notebook to the source (clickable in Jupyter, but
# without a line anchor).


def _run_git(args: list[str], cwd: str) -> str | None:
    try:
        out = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:  # noqa: BLE001  (git missing, not a repo, timeout, …)
        return None


def _normalize_remote(url: str | None):
    """(remote url) -> (web_base, host_kind) e.g. ('https://github.com/o/r', 'github')."""
    if not url:
        return None, None
    u = url.strip()
    if u.startswith("git@"):                       # git@host:owner/repo.git
        host, _, path = u[4:].partition(":")
    elif "://" in u:                                # https://… or ssh://…
        rest = u.split("://", 1)[1]
        if "@" in rest.split("/", 1)[0]:            # strip user@ / creds
            rest = rest.split("@", 1)[1]
        host, _, path = rest.partition("/")
    else:
        return None, None
    if path.endswith(".git"):
        path = path[:-4]
    hl = host.lower()
    kind = ("github" if "github" in hl else
            "gitlab" if "gitlab" in hl else
            "bitbucket" if "bitbucket" in hl else "generic")
    return f"https://{host}/{path}", kind


class SourceLinker:
    """Builds clickable markdown links to source files (line-precise on known git hosts)."""

    HOSTS = {"github", "gitlab", "bitbucket", "generic"}

    def __init__(self, mode: str = "local", web_base: str | None = None, ref: str | None = None,
                 root: str | None = None, notebooks_dir: str | None = None):
        self.mode = mode
        self.web_base = web_base
        self.ref = ref
        self.root = os.path.abspath(root) if root else None
        self.notebooks_dir = os.path.abspath(notebooks_dir) if notebooks_dir else None

    @classmethod
    def from_git(cls, repo_path: str, notebooks_dir: str | None = None) -> "SourceLinker":
        """Detect a git host + commit for permalinks; fall back to local relative links."""
        repo_path = os.path.abspath(repo_path)
        root = _run_git(["rev-parse", "--show-toplevel"], repo_path)
        if root:
            web_base, kind = _normalize_remote(_run_git(["config", "--get", "remote.origin.url"], root))
            sha = _run_git(["rev-parse", "HEAD"], root)
            if web_base and sha:
                return cls(mode=kind, web_base=web_base, ref=sha, root=root, notebooks_dir=notebooks_dir)
            return cls(mode="local", root=root, notebooks_dir=notebooks_dir)
        return cls(mode="local", root=repo_path, notebooks_dir=notebooks_dir)

    def _anchor(self, start: int, end: int | None) -> str:
        if self.mode == "bitbucket":
            return f"#lines-{start}" if not end or end == start else f"#lines-{start}:{end}"
        if self.mode == "gitlab":
            return f"#L{start}" if not end or end == start else f"#L{start}-{end}"
        return f"#L{start}" if not end or end == start else f"#L{start}-L{end}"  # github/gitea/generic

    def _rel_to_root(self, abs_path: str) -> str:
        base = self.root or os.path.dirname(abs_path)
        return os.path.relpath(os.path.abspath(abs_path), base).replace(os.sep, "/")

    def url(self, abs_path: str, start: int | None = None, end: int | None = None) -> str:
        abs_path = os.path.abspath(abs_path)
        if self.mode in self.HOSTS and self.web_base and self.ref:
            seg = "src" if self.mode == "bitbucket" else "blob"
            u = f"{self.web_base}/{seg}/{self.ref}/{self._rel_to_root(abs_path)}"
            return u + (self._anchor(start, end) if start is not None else "")
        base = self.notebooks_dir or os.getcwd()                      # local: relative file link
        return os.path.relpath(abs_path, base).replace(os.sep, "/")

    def link(self, abs_path: str, start: int | None = None, end: int | None = None,
             label: str | None = None) -> str:
        """Return a markdown link string, e.g. '[`calc/parser.py` lines 43–55](https://…#L43-L55)'."""
        if label is None:
            rel = self._rel_to_root(abs_path)
            if start is None:
                label = f"`{rel}`"
            elif end and end != start:
                label = f"`{rel}` lines {start}\u2013{end}"
            else:
                label = f"`{rel}` line {start}"
        return f"[{label}]({self.url(abs_path, start, end)})"


_KERNELS = {
    "python3": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "file_extension": ".py", "mimetype": "text/x-python"},
    }
}


def build(cells: list[dict], path: str, title: str | None = None,
          kernel: str = "python3", language: str | None = None) -> str:
    """Write `cells` to `path` as a valid .ipynb. Returns the path.

    `kernel` selects the kernelspec (default python3 — the most portable choice; source from other
    languages should live in markdown fenced blocks, with code cells reserved for demonstrations).
    `language` optionally overrides the displayed source language of the notebook metadata.
    """
    meta = dict(_KERNELS.get(kernel, _KERNELS["python3"]))
    metadata = {
        "kernelspec": meta["kernelspec"],
        "language_info": meta["language_info"],
    }
    if title:
        metadata["title"] = title
    if language:
        metadata = {**metadata, "language_info": {**metadata["language_info"], "name": language}}

    nb = {
        "cells": cells,
        "metadata": metadata,
        "nbformat": NBFORMAT,
        "nbformat_minor": NBFORMAT_MINOR,
    }
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return path


# ----------------------------------------------------------------------------- validation


def check_file(path: str) -> list[str]:
    """Return a list of problems with one notebook (empty list == valid)."""
    problems: list[str] = []
    try:
        with open(path, encoding="utf-8") as f:
            nb = json.load(f)
    except Exception as e:  # noqa: BLE001
        return [f"not valid JSON: {e}"]

    if nb.get("nbformat") != NBFORMAT:
        problems.append(f"nbformat is {nb.get('nbformat')!r}, expected {NBFORMAT}")
    if "cells" not in nb or not isinstance(nb["cells"], list):
        problems.append("missing or non-list 'cells'")
        return problems
    for i, c in enumerate(nb["cells"]):
        if c.get("cell_type") not in ("markdown", "code", "raw"):
            problems.append(f"cell {i}: bad cell_type {c.get('cell_type')!r}")
        if "source" not in c:
            problems.append(f"cell {i}: missing 'source'")
        if c.get("cell_type") == "code":
            if "outputs" not in c:
                problems.append(f"cell {i}: code cell missing 'outputs'")
            if "execution_count" not in c:
                problems.append(f"cell {i}: code cell missing 'execution_count'")

    # Stricter pass if nbformat is available.
    try:
        import nbformat  # type: ignore

        nbformat.validate(nb)
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001
        problems.append(f"nbformat.validate: {e}")
    return problems


def _check_path(target: str) -> int:
    files = []
    if os.path.isdir(target):
        for root, _dirs, names in os.walk(target):
            files += [os.path.join(root, n) for n in names if n.endswith(".ipynb")]
        files.sort()
    else:
        files = [target]
    if not files:
        print(f"no .ipynb files found at {target}")
        return 1
    bad = 0
    for fp in files:
        probs = check_file(fp)
        if probs:
            bad += 1
            print(f"FAIL {fp}")
            for p in probs:
                print(f"     - {p}")
        else:
            print(f"ok   {fp}")
    print(f"\n{len(files) - bad}/{len(files)} notebooks valid")
    return 0 if bad == 0 else 2


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "--check":
        return _check_path(argv[1])
    print(__doc__)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
