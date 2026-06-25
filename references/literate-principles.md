# Literate Programming — principles for reading a repo

Distilled from the primary sources (Knuth, Williams, Sewell, Childs, de Marneffe, van Leeuwen,
Pharr & Humphries). Read this before designing a spine (Phase 2). The goal is to internalize the
*mindset*, then apply it in reverse: the original authors wrote ordinary code; you are weaving a
literate reading of it after the fact.

## What literate programming actually is

It is not "code with good comments." It is an inversion of priority. In ordinary code, the program
is primary and prose is squeezed into comment delimiters around it. In a literate program, **the
prose is the document and the code is woven into it**, in the order that best explains the system
to a person. The same source then serves two audiences: the human reader (via "weave") and the
compiler (via "tangle", which reorders the fragments into machine order).

You are producing the *weave* for code that already exists. You will not run a tangler; the
compiler already has its order. Your job is the human-order presentation that was never written.

Three quotes worth keeping in mind:

- Knuth: explain to *human beings* what we want a computer to do; the programmer is an essayist
  whose concern is exposition and excellence of style.
- Williams: documentation containing code, not code containing documentation — the code is
  "wrenched into the daylight" of a document directed at humans.
- Pharr & Humphries (pbrt): present a complete real system through documented source, in a logical
  order, so the reader acquires a *deep* understanding of a few things rather than a superficial
  understanding of many.

## The five moves

### 1. Reading order, not machine order
Arrange the exposition by what a human needs next, never by filename or by the order the compiler
requires. Nothing should be used before it has been introduced. This is the whole game; the other
moves serve it. (van Leeuwen: parts that belong together logically should appear near each other;
the order can even bring together fragments whose locations in the source are unrelated.)

### 2. Top-down successive refinement (the "holon" hierarchy)
Start from the most general statement of what the system/subsystem does, then expand into more
specific and detailed actions step by step (Krommes, quoting Kernighan & Plauger). de Marneffe's
"holon" is a *part of a whole*: to understand the whole you understand the parts and each part's
relationship to its neighbors. So: present the trunk first; let each branch be a named placeholder;
refine branches into smaller branches; reach the leaves last. A reader can stop descending at any
level and still have a correct, complete picture at that level of abstraction.

### 3. Named code fragments ("scraps" / "modules" / "sections")
The mechanism that makes top-down refinement possible on real code. Replace a chunk of code with a
descriptive phrase in brackets — `⟨Write the final image to disk⟩` — that both *stands for* the
code and *documents its purpose*. The phrase is defined (refined) elsewhere as its own small
section. Sewell calls this **data reduction**: the name is a placeholder, so the surrounding code
shrinks to what the reader needs to follow the current level. van Leeuwen: identification by an
elaborate phrase (not a terse identifier) is the practical heart of the technique — and uses are
allowed to precede definitions, which is normal, not exceptional.

### 4. Small sections, each doing one thing
Knuth breaks programs into small modules; to understand the complicated whole you understand the
small parts and their local relationships. Childs: a literate program has logical subdivisions
(modules/sections), each with (some of) documentation, definitions, and code. Keep each section
small enough to explain in a paragraph or two.

### 5. Explain the why, with the full apparatus of a book
Childs' requirements, which separate a literate reading from a listing:
- Documentation and code are complementary and address the *same* elements of the algorithm.
- Present in an order based on **logical** considerations, not syntactic constraints.
- Examine **alternative solutions**; note future maintenance problems and extensions.
- Describe the **problem and its solution**, using whatever aids — mathematics, diagrams, figures,
  tables — communicate it best.
- Provide **cross-references and an index**; distinguish prose, keywords, identifiers, literals
  typographically.

McIlroy's point: writing the prose forces design choices into the open — "it can't gloss over the
tough places." When you read a repo this way, the tough places are exactly where you must slow
down and explain, not skip.

## Applying it in reverse (reading vs. writing)

The original authors did not write literately, so you must *recover* the structure:

- The **named fragments** correspond to coherent chunks you identify in the real code — a block
  inside `main`, a helper method, a phase of an algorithm. Name them by *intent*, not by mechanism.
- The **reading order** is your reconstruction of concept dependencies, which you derive in the
  orientation phase. The directory tree is evidence, not the answer.
- **Faithfulness is paramount.** In real literate programming the prose and code are guaranteed
  consistent because they share one source. Here they don't: you are excerpting. So every excerpt
  must be the repo's real code, attributed to its `file:line` range, and you must not invent
  rationales the code/commits/docs don't support. When you're unsure, read more or say you're
  unsure — never paper over a tough place with a confident guess.

## Anti-patterns (what a literate reading is *not*)

- **A file tour.** "Here's `utils.py`, here's `models.py`…" is machine order wearing a hat.
- **Comments with extra steps.** A code cell followed by one sentence of paraphrase is not prose-
  first exposition. Lead with the idea; show the code as evidence.
- **Restating syntax in English.** "This loop iterates over the list" tells the reader nothing they
  couldn't see. Explain intent, invariants, and why-this-way.
- **All detail, no skeleton.** If the reader meets leaves before the trunk, the refinement is upside
  down. The first chapter must show the whole shape via fragments.
- **API reference.** Generated signatures and parameter tables are reference material; a literate
  reading is a narrative you read front to back.
