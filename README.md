# literate-repo

Turn any code repository into a **literate-programming reading of itself** — a series of Jupyter
notebooks, organized as chapters, that explain the codebase as a work of literature, in the
tradition of Knuth's *WEB* and Pharr & Humphries' *Physically Based Rendering* (pbrt).

The deliverable is not API docs and not a file-by-file tour. It is a guided exposition a newcomer
can read front to back and come away understanding **what the system does, how it is put together,
and why it was built that way.**

> "Let us concentrate rather on explaining to human beings what we want a computer to do." — Knuth
>
> "Instead of writing code containing documentation, the literate programmer writes documentation
> containing code." — Ross Williams

## The idea

A normal program is arranged in the order the *compiler* needs. A literate reading is arranged in
the order a *human mind* needs. This skill performs that re-arrangement — a "weave" — over code that
already exists: it recovers a conceptual reading order, decomposes the system top-down into small
**named fragments**, and presents prose as the main text with real, attributed code woven in.

## What it produces

A folder of notebooks for the target repo:

```
<repo>-literate/
├── 00_overview.ipynb   front matter, how-to-read, architecture diagram, table of contents,
│                       and "the system at a glance" (the whole program via fragments)
├── 01_<subsystem>.ipynb
├── 02_<subsystem>.ipynb   one chapter per major subsystem, in dependency order
├── ...
└── 99_index.ipynb      (larger repos) glossary + fragment index + identifier index
```

Each chapter is prose-first, top-down, with numbered sections (§2.1, §2.2, …), bracketed fragment
references like `⟨Build the camera, sampler, and integrator 2.4⟩`, and — above every excerpt — a
**clickable link to the exact file and lines** (line-precise GitHub/GitLab/Bitbucket permalinks when
the repo is on a git host, relative file links otherwise). Excerpts are faithful to the source,
followed by design notes that explain the *why*, and — where the repo's language matches the kernel —
runnable demonstration cells.

## How it works

Four phases, orchestrated by `SKILL.md`:

1. **Orient** — clone/locate the repo, run `scripts/repo_survey.py` for a fast lay of the land
   (languages, entry points, manifests, tree), then read the README, entry points, and core types
   and write an orientation memo.
2. **Design the spine** — derive a *reading order* from concept dependencies (not the directory
   tree): the system at a glance, then foundations, then subsystems in dependency order, then
   integration. Confirm the spine with the user before writing everything.
3. **Write the chapters** — one notebook each, following `references/chapter-guide.md`.
4. **Assemble** — overview, optional index, validate, and present.

## Layout

```
literate-repo/
├── SKILL.md                              the orchestrator (read by Claude when the skill triggers)
├── README.md                             this file
├── LICENSE
├── Makefile                              make package | demo | check | test | clean
├── references/
│   ├── literate-principles.md            the philosophy, distilled from the primary sources
│   └── chapter-guide.md                  chapter template, fragment notation, worked example
├── scripts/
│   ├── repo_survey.py                    dependency-free repo orientation
│   └── litnb.py                          build valid Jupyter notebooks (no Jupyter needed) + --check
├── tools/
│   └── package_skill.py                  build the installable .skill (stdlib only)
├── demo/                                 the runnable MVP (input repo + the reading produced from it)
└── .github/workflows/ci.yml              validates the skill, rebuilds the demo, runs sample tests
```

## Build & install

The repository is self-contained — building the installable skill needs only the Python standard
library:

```bash
make package          # or: python3 tools/package_skill.py  ->  dist/literate-repo.skill
```

Then install `dist/literate-repo.skill` in the Claude app/UI under Settings → Capabilities → Skills
(upload the `.skill` file). For distribution, attach the `.skill` to a
[GitHub Release](https://docs.github.com/en/repositories/releasing-projects-on-github) — CI also
uploads it as a build artifact on every push.

Other handy targets: `make demo` (regenerate the demo notebooks), `make check` (validate they are
well-formed), `make test` (run the sample repo's tests), `make clean`.

## Using it

Install the packaged `.skill`, then point it at a repo:

> "Give me a literate-programming reading of this repo."
> "Explain this codebase as a series of notebook chapters, pbrt-style."
> "Help me understand `<path-or-git-url>`."

For a large repo a literate reading is *selective*: it covers the spine and the load-bearing
subsystems deeply and summarizes the periphery, telling you what was covered and what was deferred.

## See it first: the demo

`demo/` is a complete, runnable MVP. It reads one small real repo (`demo/sample_repo` — a ~100-line
arithmetic evaluator) and produces a four-chapter literate reading in `demo/calc-literate/` that you
can open and execute. Start at `demo/calc-literate/00_overview.ipynb`. See `demo/README.md` for a
tour of what it demonstrates.

```bash
cd demo && python3 build_demo.py        # regenerate the reading from the sample repo
```

## Credits

Built on the literate-programming tradition: Knuth (WEB/CWEB), Ross Williams (FunnelWeb), Sewell
(*Weaving a Program*), Childs, de Marneffe (Holon Programming), van Leeuwen (CWEBx), and Pharr &
Humphries (pbrt). Source material: <http://www.literateprogramming.com>.

## License

MIT — see [LICENSE](LICENSE).
