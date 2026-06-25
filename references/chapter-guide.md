# Chapter Guide — how to write one literate notebook

Read this before Phase 3. It gives the chapter template, the fragment/section notation, and a full
worked example. Apply it to every chapter notebook.

## Notation (be consistent across all chapters)

**Sections** are numbered `§<chapter>.<n>` — e.g. `§2.1`, `§2.2`. Number them in reading order
within the chapter. Sections are the unit of a literate program: one idea each, a paragraph or two
of prose plus the code it concerns.

**Named fragments** use angle brackets and carry the number of the section that *defines* them:

- A **use** of a fragment (inside higher-level code) looks like:
  `⟨Construct the camera, sampler, and integrator 2.4⟩`
  — the number `2.4` tells the reader where it is refined.
- A **definition** of a fragment heads its own section and is written with `≡`:
  `⟨Construct the camera, sampler, and integrator 2.4⟩ ≡`
  followed by the code cell that realizes it.

Name fragments by **intent** ("Validate the request and reject malformed input"), never by
mechanism ("the if-block"). A good fragment name reads as a sentence in the surrounding code and
makes the high-level routine legible on its own.

**Provenance — a clickable link above every excerpt.** Each code reference must link to the exact
file, and to the exact lines when the repo is on a git host. Because links inside a fenced code
block are not clickable, put the link on the markdown line *immediately above* the fence, and keep a
short `file:lines` comment inside the fence for plain-text exports:

```
📄 [`src/render/integrator.cpp` lines 88–140](https://github.com/owner/repo/blob/<sha>/src/render/integrator.cpp#L88-L140)

​```cpp
// src/render/integrator.cpp:88-140
... real code ...
​```
```

Build the link with the Phase-1 `SourceLinker` rather than by hand — `link.link(abs_path, 88, 140)`
returns exactly that markdown string and gets the host's line-anchor format right. Anchor formats it
handles: GitHub/Gitea `#L88-L140`, GitLab `#L88-140`, Bitbucket `#lines-88:140`; with no git remote
it emits a relative file link (clickable in Jupyter, no line anchor). **Link every reference**, not
only the first — when prose names another function or type, link to its definition too. If you elide
part of a body, mark it `… (elided: <what>)`. The excerpt must be the repo's actual code.

**Cross-references.** Write them inline: "(introduced in §1.2)", "(refined in §3.5)", "(see
Chapter 4)". In notebook markdown you can also link to other notebooks: `[Chapter 4](04_xxx.ipynb)`.

## Chapter template

Each chapter notebook follows this shape. Cells alternate markdown (prose) and, where useful, code.

1. **Title + placement** (markdown): `# Chapter N — <Title>`. One short paragraph: what this
   chapter explains, why it matters, and where it sits relative to earlier chapters (what it
   assumes the reader now knows).
2. **Roadmap** (markdown): two or three sentences previewing the sections, so the reader has a map.
3. **Top-level section first** (markdown + code): present the subsystem's entry point with its
   internals factored into named fragments. The reader should grasp the subsystem's whole shape
   here before any detail.
4. **Refinement sections** (markdown + code, one per fragment): in the order a reader would descend.
   Each: prose explaining the idea and the *why*; the fragment definition (`≡`) and its code cell;
   any deeper fragments it introduces. Add a diagram or equation where it carries meaning.
5. **Design notes** (markdown): alternatives the authors could have taken, invariants the code
   relies on, tradeoffs, and maintenance hazards — woven in where relevant or gathered at the end.
6. **Closing** (markdown): one paragraph recapping what the reader now understands and naming what
   the next chapter builds on it.

Keep prose leading. A code cell should almost never appear without a sentence before it saying what
idea it embodies.

## Demonstrations

Where the kernel language matches the repo (e.g. a Python repo with a Python kernel), add a few
**demonstration cells** that construct the real objects and show them working — a literate reading
you can run is worth far more than one you can only read. Where the languages differ, demonstrate
by building/running the real project in a shell cell (`!cmd` or `subprocess`) and showing its
output, or by showing captured output. Keep demonstrations small and pointed: they illustrate one
claim the prose just made.

## Worked example (a renderer's main loop — pbrt-flavored, abridged)

The following shows the *texture* to aim for: prose-first, top-down, fragment-driven, with the
whole shape visible before the detail. (Lengths here are compressed; real chapters breathe more.)

---

> # Chapter 1 — The system at a glance
>
> Before any single piece of the renderer makes sense, it helps to see the whole arc of a run: we
> turn a text description of a scene into an image file. This chapter follows that arc from the top,
> deferring every detail to a named fragment so the shape stays visible. Later chapters refine the
> fragments. If you read only this chapter, you will still have a correct mental model of the
> system — just at low resolution.
>
> **Roadmap.** §1.1 shows the entire run as one routine. §1.2–§1.5 refine its four steps: reading
> the scene, building the rendering objects, rendering, and writing the image. The render step
> itself is large enough that its refinement opens Chapter 2.
>
> ## §1.1 A run, end to end
>
> Stripped of error handling, the whole program is four steps. Each bracketed phrase is a fragment
> refined in the section whose number follows it:
>
> 📄 [`src/main/render.cpp` lines 42–61](https://github.com/owner/repo/blob/<sha>/src/main/render.cpp#L42-L61)
>
> ```cpp
> // src/main/render.cpp:42-61
> int main(int argc, char **argv) {
>     Options opts;
>     ⟨Parse the command line and scene file into a scene description 1.2⟩
>     ⟨Build the camera, sampler, and integrator from the description 1.3⟩
>     ⟨Render the image 2.1⟩
>     ⟨Write the rendered image to disk 1.4⟩
>     return 0;
> }
> ```
>
> Two things are worth noticing immediately. First, rendering is bracketed off as a single step even
> though it is the bulk of the work — the top level doesn't care *how* we render, only that we do.
> Second, the objects built in §1.3 (camera, sampler, integrator) are the three abstractions the
> whole system turns on; Chapter 2 is devoted to them.
>
> ## §1.2 Parse the command line and scene file into a scene description
>
> The parser's job is to produce a fully-populated `SceneDescription` — a passive record of
> everything the scene file asked for, with no rendering objects built yet. Separating *what was
> asked for* from *what we build to satisfy it* keeps file-format concerns out of the renderer
> proper, and lets the same description drive different back ends.
>
> 📄 [`src/main/render.cpp` lines 63–92](https://github.com/owner/repo/blob/<sha>/src/main/render.cpp#L63-L92)
>
> ```cpp
> // src/main/render.cpp:63-92
> ⟨Parse the command line and scene file into a scene description 1.2⟩ ≡
>     for (int i = 1; i < argc; ++i) ⟨Handle one command-line flag 1.2.1⟩
>     SceneDescription scene = ParseFiles(opts.sceneFiles);
> ```
>
> *(…refinement of §1.2.1, then §1.3, §1.4 follow in the same pattern…)*
>
> ## Design notes
>
> The description-then-build split (§1.2 vs §1.3) is the load-bearing decision of the front end. An
> alternative the authors rejected — building objects directly while parsing — is simpler for a
> single back end but couples the file grammar to object construction; the indirection here is what
> later lets the same scene feed both the path tracer and the debugger (Chapter 6). The cost is one
> extra in-memory representation of the scene, which for these workloads is negligible.
>
> ## Where this leads
>
> You now have the skeleton: read → build → render → write. The three objects built in §1.3 are the
> spine of everything else, so Chapter 2 explains them and their relationships before we descend, in
> Chapter 3, into the render step bracketed at §2.1.

---

Notice what the example does: the reader sees all four steps of the program before learning how any
one of them works; each fragment is named by intent and carries the section number where it's
refined; the code is real, attributed, and preceded by a clickable link to its exact lines; and the
design note explains a decision and the alternative, not the syntax. That is the target for every
chapter.

## Building the notebook

Assemble cells with the helper (valid JSON guaranteed), and use a `SourceLinker` for the link lines:

```python
import sys; sys.path.insert(0, "scripts")   # adjust to the skill's scripts path
import litnb

link = litnb.SourceLinker.from_git("myrepo", notebooks_dir="myrepo-literate")  # permalinks or local
cells = [
    litnb.md("# Chapter 1 — The system at a glance", "", "Before any single piece ..."),
    litnb.md("## §1.1 A run, end to end", "", "Stripped of error handling ...", "",
             link.link("myrepo/src/main/render.cpp", 42, 61),   # 📄 clickable, line-precise
             "", "```cpp", "// src/main/render.cpp:42-61", "int main(int argc, char **argv) {",
             "    ...", "}", "```"),
    # a Python-kernel demonstration cell, only if the repo is Python or you shell out:
    litnb.code("!python -c \"import thispkg; print(thispkg.__version__)\""),
]
litnb.build(cells, "myrepo-literate/01_overview.ipynb", title="The system at a glance")
```

`litnb.md(*lines)` joins its arguments with newlines, so you can pass prose, the link line, and the
fenced code as separate string arguments. `litnb.SourceLinker.from_git(repo, notebooks_dir)` builds
clickable file/line links (GitHub/GitLab/Bitbucket permalinks, or a relative file link with no
remote). `litnb.fragment_use(name, sec)` and `litnb.fragment_def(name, sec)` return the `⟨… N⟩` and
`⟨… N⟩ ≡` strings if you'd rather not type the brackets by hand. Validate the whole directory at the
end with `python3 scripts/litnb.py --check <dir>`.
