---
name: literate-repo
description: >
  Turn any code repository into a literate-programming reading of itself — a series of Jupyter
  notebooks organized as chapters that explain the codebase as a work of literature, in the
  tradition of Knuth's WEB and Pharr & Humphries' "Physically Based Rendering" (pbrt). The
  notebooks present code in human reading order (not file order), decomposed top-down into small
  named fragments, with prose explaining the problem, algorithms, data structures, and design
  decisions — documentation containing code, not code containing comments. Use whenever someone
  wants to understand, document, onboard onto, study, or explain a repo or codebase deeply;
  whenever they mention "literate programming", "literate", "Knuth", "WEB/CWEB/noweb", "pbrt",
  "explain this codebase as a book/chapters/notebooks", "code walkthrough", "annotated source",
  "guided tour of the code", "make this repo readable", or "reading order". Trigger even when the
  user just points at a repo and says "help me understand this" — a literate reading fits.
---

# Literate Repo

Produce a **literate-programming reading** of an existing repository: a set of Jupyter notebooks,
one per chapter, that explain the codebase the way Knuth explained TeX and the way pbrt explains
a renderer — as an essay whose subject happens to be a program.

The deliverable is *not* API docs and *not* a file-by-file tour. It is a guided exposition that a
newcomer can read front to back and come away understanding **what the system does, how it is put
together, and why it was built that way.**

## The one idea that makes this work

A normal program is arranged in the order the *compiler* needs. A literate reading is arranged in
the order a *human mind* needs. Everything in this skill follows from that inversion:

> "Let us concentrate rather on explaining to human beings what we want a computer to do."
> — Knuth

> "Instead of writing code containing documentation, the literate programmer writes documentation
> containing code." — Ross Williams

So you are doing a *weave*: re-presenting existing source in conceptual reading order, broken into
small pieces, with prose as the main text and code woven in. Read
`references/literate-principles.md` before designing the spine — it distills the philosophy and
the conventions (named fragments, top-down refinement, sectioning, cross-reference) you will use.

## Workflow

Four phases: **Orient → Design the spine → Write the chapters → Assemble.** Don't skip orientation
and don't write chapters in file order. Use a TodoList to track the phases and the chapter list.

---

### Phase 0 — Locate the repo

The user will give a local path or a URL.

- **Local path** (e.g. `/mnt/user-data/uploads/...` or a working dir): use it directly. Copy
  read-only locations into the working dir if you need to run/build anything.
- **Git URL**: clone it (`git clone --depth 1 <url>` into `/home/claude`). If the network blocks
  it, tell the user their network settings may need an org owner to allow the host, and ask them
  to upload an archive instead.

Decide where output goes: `<repo-name>-literate/` in the working dir (or `/mnt/user-data/outputs/`
for the final deliverable).

---

### Phase 1 — Orient (survey before you write a word)

You cannot give a logical reading order for a system you don't yet understand. Build a mental
model first.

Run the survey helper to get a fast, factual lay of the land:

```bash
python3 scripts/repo_survey.py <repo-path>
```

It prints a language/LOC breakdown, a pruned file tree, candidate entry points, build/config
files, and dependency manifests. Then **read, don't just scan**:

- The `README`, any `ARCHITECTURE.md`/`docs/`, and the build config — these state the domain and
  intended structure in the authors' own words.
- **The linked paper, if one exists.** READMEs for research repos almost always link an arXiv
  paper. Fetch it (use `WebFetch` on the HTML version at `arxiv.org/html/<id>v1`). The paper is
  the primary source for *why* design decisions were made — implementation details sections give
  exact hyperparameters, ablation tables justify vocabulary sizes, and the introduction frames
  the core claims. Read the paper before writing any prose about design rationale.
- The entry points the survey found (`main`, CLI definitions, package exports, server bootstraps).
- The central data structures and interfaces (the headers/types/base classes everything else
  refers to). In most systems a handful of types carry the whole design.
- The test directory layout — tests reveal the units the authors think in and the public surface.

Write yourself a short **orientation memo** (in the working dir, not a deliverable) capturing:
the domain and the problem the software solves; the principal entry point(s) and top-level control
flow; the core abstractions/data types; the major subsystems and how they depend on each other;
and a first guess at reading order. This memo is the raw material for the spine.

---

### Phase 2 — Design the spine (the chapter plan)

The spine is the table of contents in **reading order**, derived from concept dependencies, not
from the directory tree. Order chapters so that nothing is used before it has been explained.

A reliable shape, adapted from pbrt:

1. **The system at a glance** — follow the top-level entry point (`main`/bootstrap) all the way
   down, but with every detail factored out into *named fragments*. The reader sees the whole
   skeleton of the program in one or two pages before meeting any detail. This is the most
   important chapter; it is the map for everything after.
2. **Foundations** — the core data types and utilities that the rest of the system is built on
   (the geometry/math/memory layer in pbrt; the domain model elsewhere).
3. **One chapter per major subsystem**, ordered by dependency: explain a subsystem only after the
   things it rests on. Each chapter is sized to be held in one head — split anything sprawling.
4. **Integration** — how the pieces compose into the running whole; the end-to-end path of a
   representative input through the system; cross-cutting concerns (config, errors, concurrency).

Produce the spine as an explicit list. For each chapter record: number + title; a one-line purpose;
the source files/regions it draws from; the key named fragments it will define; and which earlier
chapters it depends on.

**Then pause and show the user the spine** before writing all the notebooks — chapter writing is
expensive and the reading order is the part most worth their input. For a small repo (a handful of
files) you may proceed without pausing; say so and continue.

---

### Phase 3 — Write the chapters (one notebook each)

Read `references/chapter-guide.md` now — it contains the chapter template, the named-fragment
notation, the section-numbering scheme, and a full worked example. Follow it for every chapter.
The essentials:

- **Prose is the main text; code is woven in.** Each section is: explanation first, then the code
  that the explanation was about. If a code cell has no surrounding prose, you are writing comments,
  not a literate program — fix it.
- **Top-down refinement with named fragments.** Present a high-level routine with its inner detail
  replaced by bracketed, numbered fragment names like `⟨Build the camera, sampler, and integrator 2.4⟩`.
  Define (refine) each fragment in its own later section. This is the core literate move — it lets a
  reader understand the whole before any part, then descend only where they choose. (Sewell calls it
  "data reduction"; the fragment name stands in for code the reader doesn't need yet.)
- **Number sections** (§2.1, §2.2, …) so fragments and prose can cross-reference precisely, within
  and across chapters.
- **Faithful excerpts with provenance.** Code shown must be the repo's actual code, each excerpt
  led by a provenance comment: `path/to/file.ext:Lstart–Lend`. Never paraphrase code into something
  that wasn't in the repo; you may elide with `…` and a note when a body is long.
- **File references as clickable links.** When citing a source file in prose, use a markdown
  hyperlink rather than a plain text path: `[filename.py:L66](../path/to/filename.py#L66)`. This
  applies everywhere a file path appears — inline mentions, provenance headers, and design notes.
  Relative paths from the notebook location keep the links portable.
- **Explain the why, not only the what** (Childs' requirements): design decisions, invariants,
  tradeoffs, alternatives the authors could have taken, and maintenance hazards. This is what makes
  it literature rather than a listing.
- **Never invent rationale.** Only attribute a design decision to the authors if it is stated in
  the code comments, README, or paper. When none of those sources explain a choice, say so
  explicitly: *"The paper/code does not document why X was chosen over Y."* A plausible-sounding
  explanation you invented is worse than silence — it misleads the reader. Label speculation as
  speculation if you include it at all.
- **Annotate ambiguous tensor shapes.** In multi-camera or multi-modal models, two axes can share
  the same integer value by coincidence (e.g. N_cam=3 and C=3 in a 3-camera RGB model). Always
  annotate shapes with explicit axis names when any ambiguity exists:
  `(B, N_cam=3, C=3, H, W)` not `(B, 3, 3, H, W)`. In prose write "N_cam camera images, each
  with 3 RGB channels" not "3 camera images of shape (3, H, W)". Confusing camera and channel
  axes is a silent correctness bug that is very hard to debug.
- **Use figures when they carry meaning** — Mermaid diagrams in markdown cells for control flow,
  data flow, class/type relationships, or state machines; equations in LaTeX for any math.
- **Cross-reference generously** — backward to foundations already laid, forward to where a deferred
  fragment is refined.

**Clarity rules — principles for making a reading genuinely useful:**

- **Disambiguate shared names at the chapter entrance.** When the same word covers multiple distinct
  concepts in the codebase, place a disambiguation table before any code. The reader should never
  have to guess which sense of a term is in use.

- **Distinguish active code from dead code.** If a parameter, branch, or module exists but is
  never exercised in the system under study, say so explicitly — cite the call sites that prove it.
  Describing dead code as if it were live gives a false picture of how the system actually works.

- **State what an operation does in plain language before showing the formula or code.** A reader
  who doesn't yet understand the operation cannot read the formula productively. One sentence of
  concrete English — "the weights select which sampled pixel features contribute to the output" —
  prepares the reader for the notation that follows. Use an ASCII data-flow chain when a
  transformation moves across representations or abstraction layers.

- **Name contrasts explicitly when similarity would mislead.** If a mechanism resembles a
  well-known pattern but differs in a load-bearing way, name the difference before the reader
  assumes the familiar semantics. Silence about a contrast is a lie by omission.

- **Each demo must faithfully represent the actual system, not a convenient approximation.**
  A placeholder (random noise, dummy inputs, simplified shapes) hides what the real quantity
  represents. Compute the real value even when it requires more setup. Explain in prose what
  the demo input *is* in the live system before running the cell.

- **Each demo should make exactly one concept obvious; choose the form that achieves it.**
  Before writing a demo, ask: "what should the reader understand after seeing this output?"
  If the current form doesn't make that understanding inevitable, find one that does — a
  different plot type, a different slice of the data, an overlay on real input. Reuse the
  same colour scheme across related demos so the reader can cross-reference them.

- **Preemptively answer structural questions a reader will ask.** When a design choice looks
  unnecessary or surprising (a batch dimension on an initially identical tensor, a parameter
  that is always None, a code path that is never taken), answer the question in prose before
  the reader has to ask it. Unanswered "why?" questions break reading flow.

**Code-cell strategy depends on the repo's language** (decide once, state it in Chapter 0):

- *Notebook kernel language matches the repo* (Python repo → Python kernel): put real source in
  executable code cells where it helps, and add small **demonstration cells** that import/construct
  the actual objects and show them working. A literate reading you can *run* is the ideal.
- *Repo language differs from the kernel* (C/C++/Rust/Go/JS/…): show source as language-tagged
  fenced code blocks **inside markdown cells** (perfect highlighting, never mis-executed). For
  demonstrations, use shell code cells (`!`/`subprocess`) that build and run the real project, or
  show captured output. Don't paste foreign-language source into Python code cells.

Build each notebook with the helper so the JSON is always valid:

```python
import sys; sys.path.insert(0, "scripts")
import litnb
litnb.build(
    [litnb.md("# Chapter 2 — Foundations\n..."),
     litnb.md("## §2.1 The point type\n...prose...\n```cpp\n// src/geometry.h:14-40\n...\n```"),
     litnb.code("import numpy as np  # demonstration\n...")],
    "<repo-name>-literate/02_foundations.ipynb",
    title="Foundations",
)
```

`litnb` also has `litnb.fragment_use(...)` and `litnb.fragment_def(...)` helpers for the
bracket notation if you want them; see the docstrings. You may instead hand the prose markdown
directly — whatever is clearest.

**Run and test every notebook in a correction loop.** After writing each chapter, execute
every code cell top-to-bottom in the correct kernel and fix all errors before moving on.
Do not skip this step — a notebook that crashes is not a deliverable. Common failure classes
and their fixes:

- **`AttributeError: object has no attribute X`** — you referenced a config field or object
  attribute that doesn't exist. Read the actual class/dataclass to find the correct name.
- **`FileNotFoundError` on `savefig` or file reads** — the notebook's `os.chdir` sets CWD
  to the repo root; any path to the literate output directory must be relative to that
  (e.g. `../SparseDriveV2-literate/`) or use an absolute path. Never assume the CWD is the
  notebook's own directory.
- **`FileNotFoundError` on data/checkpoint files** — the file genuinely doesn't exist.
  Either use a guard (`if os.path.exists(...)`) and print a helpful message, or use a
  smaller/guaranteed file that is always present.
- **`ImportError` / `ModuleNotFoundError`** — the kernel doesn't have the package. Either
  install it or restructure the cell to not require it.
- **CUDA errors** — some kernels require GPU. Mark those sections clearly and add a
  `assert torch.cuda.is_available()` guard with a readable error message.

The correction loop is: **run → see error → fix the cell → re-run from the failing cell →
repeat until the full notebook runs clean.** Only move to the next chapter once the current
one is error-free.

**Distinguish fixable errors from out-of-scope prerequisites.** Before attempting a fix,
decide which kind of error you have:

| Error kind | Example | Correct response |
|---|---|---|
| **Notebook bug** | wrong attribute name, bad relative path, missing import | Fix the cell and re-run |
| **Missing prerequisite** | dataset not downloaded, checkpoint not present, GPU absent | Stop — tell the user what to do |

Out-of-scope prerequisites are things you cannot fix by editing the notebook — the user
must take an action outside the notebook to resolve them. When you hit one:

1. **Stop the correction loop** for that cell.
2. **Add a clear guard** in the cell that detects the missing resource and prints a
   descriptive message instead of crashing:
   ```python
   if not os.path.exists("data/navmini"):
       print("Dataset not found. Download it with: ...")
       raise SystemExit("Missing dataset — see message above.")
   ```
3. **Report to the user** which prerequisite is missing and exactly how to obtain it
   (download command, URL, or README section). Do not leave the user debugging a
   `FileNotFoundError` with no context.

The rule of thumb: if fixing the error requires you to *write code*, it is a notebook bug.
If fixing it requires the *user to run a command or download a file*, it is an
out-of-scope prerequisite — stop and hand off.

---

### Phase 4 — Assemble

- **Chapter 0 / `00_overview.ipynb`** — the front matter: what the system is and the problem it
  solves; how to read these notebooks; the code-cell convention you chose; a clickable table of
  contents linking every chapter notebook; and a top-level architecture diagram. This is also where
  "The system at a glance" lives (or it can be its own Chapter 1 — your call based on size).
- **Appendix / `99_index.ipynb`** (worthwhile for larger repos) — a glossary of domain terms; an
  index of every named fragment with the section that defines it; and an index of the key
  identifiers (types, functions) with the chapter that introduces them. Cross-references are a
  defining feature of literate programs — this is where they pay off.
- Number notebooks with zero-padded prefixes (`00_`, `01_`, …) so they sort correctly.
- Validate every notebook before delivering: `python3 scripts/litnb.py --check <dir>` confirms each
  `.ipynb` is well-formed.

Put the finished notebooks in `/mnt/user-data/outputs/<repo-name>-literate/` and present them with
`present_files`, leading with `00_overview.ipynb`. Keep the closing message short — the notebooks
are the deliverable.

---

## Quality bar (check before delivering)

- Could a newcomer read Chapter 0 → last chapter **in order** and never hit a concept that wasn't
  already introduced? If not, the spine is in the wrong order.
- Does Chapter 1 show the **whole skeleton** of the program on a page or two via fragments, before
  any detail? If a reader has to understand a leaf before the trunk, refactor.
- Is every code excerpt **real, attributed to a clickable file:line link**, and surrounded by prose
  that explains it?
- Does the reading explain **why**, not just restate the code in English? Restating `for (i…)` as
  "loops over i" adds nothing; explaining *why this iteration order* does.
- Are fragments and sections **numbered and cross-referenced** so a reader can navigate?
- **Do all code cells run without error?** Execute every notebook top-to-bottom in the correct
  kernel. A notebook with a crashing cell is not done. Run the correction loop (run → fix →
  re-run) until every chapter is clean.

## Scope notes

- **Big repos**: don't try to cover every line. A literate reading is selective — cover the spine
  and the load-bearing subsystems deeply; summarize the periphery and point to it. Tell the user
  what you chose to cover and what you deferred.
- **Faithfulness over polish**: when unsure what code does, say so and read more rather than
  inventing a rationale. Never attribute a design decision the evidence doesn't support. Evidence
  hierarchy: (1) paper implementation-details section, (2) code comments, (3) README, (4) ablation
  tables. If none of these explain a choice, the honest answer is "the source does not document
  this."
- This skill *reads* code; it does not modify the repo.

## Bundled resources

- `references/literate-principles.md` — the philosophy and conventions, distilled from the
  primary sources. Read before Phase 2.
- `references/chapter-guide.md` — chapter template, fragment notation, numbering, and a full
  worked example. Read before Phase 3.
- `scripts/repo_survey.py` — fast, dependency-free repo survey (Phase 1).
- `scripts/litnb.py` — build valid Jupyter notebooks and validate them (Phases 3–4).
