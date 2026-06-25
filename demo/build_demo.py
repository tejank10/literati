#!/usr/bin/env python3
"""Build the demo literate reading of `sample_repo/calc` into `calc-literate/`.

This script is itself a worked example of using `litnb` to assemble notebooks. It reads
*faithful* excerpts straight from the sample repo's source (so provenance line ranges are
always accurate) and weaves them into four chapter notebooks.

Run it from this directory:   python3 build_demo.py
Then validate:                python3 ../scripts/litnb.py --check calc-literate
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.join(HERE, "sample_repo")
OUT = os.path.join(HERE, "calc-literate")
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import litnb  # noqa: E402

# Build links to the source. from_git gives line-precise permalinks once this repo has a GitHub
# (or GitLab/Bitbucket) remote and the commit is pushed; with no remote it falls back to a relative
# file link that still opens the file in Jupyter. Override the auto-detection with --repo-url/--ref.
LINK = litnb.SourceLinker.from_git(REPO, notebooks_dir=OUT)


def link(rel: str, start: int | None = None, end: int | None = None) -> str:
    """A clickable '📄 calc/file lines a–b' markdown link line for a source location."""
    abs_path = os.path.join(REPO, rel)
    if start is None:
        label = rel
    elif end and end != start:
        label = f"{rel} lines {start}\u2013{end}"
    else:
        label = f"{rel} line {start}"
    return "\U0001f4c4 " + LINK.link(abs_path, start, end, label=label)


def excerpt(rel: str, start: int, end: int, lang: str = "python") -> str:
    """A clickable link line followed by a faithful, provenance-headed excerpt of lines [start, end]."""
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        lines = f.read().splitlines()
    body = "\n".join(lines[start - 1:end])
    comment = "#" if lang == "python" else "//"
    fence = f"```{lang}\n{comment} {rel} : lines {start}-{end}\n{body}\n```"
    return f"{link(rel, start, end)}\n\n{fence}"


# A setup cell that finds the bundled package so demonstration cells can import it.
SETUP = (
    "import os, sys\n"
    "# Find the bundled demo package (works when run from the calc-literate directory).\n"
    "d = os.getcwd()\n"
    "for _ in range(6):\n"
    "    for cand in (os.path.join(d, 'sample_repo'), os.path.join(d, '..', 'sample_repo')):\n"
    "        if os.path.isdir(os.path.join(cand, 'calc')):\n"
    "            sys.path.insert(0, os.path.abspath(cand))\n"
    "            break\n"
    "    else:\n"
    "        d = os.path.dirname(d); continue\n"
    "    break\n"
    "import calc\n"
    "print('imported calc', calc.__version__)"
)

U = litnb.fragment_use
D = litnb.fragment_def


# ---------------------------------------------------------------- Chapter 0: overview
def overview() -> None:
    cells = [
        litnb.md(
            "# calc — a literate reading",
            "",
            "*Produced by the `literate-repo` skill from the repository in `../sample_repo`.*",
            "",
            "`calc` is a pocket calculator: it turns a string like `1 + 2 * 3` into the number "
            "`7.0`, honoring operator precedence, parentheses, and unary minus. It is small — "
            "about 100 lines — which lets us read **all** of it, the way Knuth read TeX and "
            "*Physically Based Rendering* reads a renderer: as an essay whose subject is a program.",
        ),
        litnb.md(
            "## How to read this",
            "",
            "These notebooks are meant to be read **in order**, front to back. Each introduces only "
            "ideas that earlier chapters have already established.",
            "",
            "- **Prose leads; code follows.** Every excerpt is preceded by the idea it embodies.",
            "- **Named fragments.** A bracketed phrase like " + U("Tokenize, parse, evaluate", "1.2")
            + " stands for code refined in the section whose number it carries. This lets you see "
            "the whole shape before any detail, and descend only where you wish.",
            "- **Sections are numbered** (§1.1, §1.2, …) so fragments and prose can cross-reference.",
            "- **Provenance.** Each excerpt is the repo's real code, headed by its `file : lines`.",
            "- **Runnable.** Because `calc` is Python, the demonstration cells import the real package "
            "and run it — a literate reading you can execute.",
        ),
        litnb.md(
            "## The shape of the system",
            "",
            "`calc` is the textbook three-stage pipeline. A string becomes a list of **tokens**, the "
            "tokens become an **abstract syntax tree** (AST), and the tree is walked to a **number**:",
            "",
            "```mermaid",
            "flowchart LR",
            '    A["source string<br/>\\"1 + 2 * 3\\""] -->|tokenize| B["tokens<br/>NUMBER + NUMBER * NUMBER"]',
            '    B -->|parse| C["AST<br/>(+ 1 (* 2 3))"]',
            '    C -->|evaluate| D["number<br/>7.0"]',
            "```",
            "",
            "Plain-text fallback, if your viewer does not render Mermaid:",
            "",
            "```text",
            '  "1 + 2 * 3"  --tokenize-->  [NUMBER + NUMBER * NUMBER]  --parse-->  (+ 1 (* 2 3))  --evaluate-->  7.0',
            "```",
        ),
        litnb.md(
            "## Reading order is not file order",
            "",
            "On disk the modules sort roughly alphabetically — `cli`, `evaluator`, `nodes`, "
            "`parser`, `tokens`. That is the order Python's importer is happy with, not the order a "
            "person learns the system in. We read it in the order ideas *depend* on one another:",
            "",
            "| Chapter | Notebook | Source it reads |",
            "|---|---|---|",
            "| §1 The system at a glance | this notebook | `cli.py` |",
            "| §2 Reading input: the tokenizer | [01](01_reading_input_the_tokenizer.ipynb) | `tokens.py` |",
            "| §3 Structure: the parser | [02](02_structure_the_parser.ipynb) | `nodes.py`, `parser.py` |",
            "| §4 Meaning: the evaluator | [03](03_meaning_the_evaluator.ipynb) | `evaluator.py` |",
            "",
            "Rearranging the source into the order best for human understanding is the whole point of "
            "a literate reading; the compiler already has its own order.",
        ),
        litnb.md(
            "## §1 The system at a glance",
            "",
            "The top of the program is `calc()`: one function that names the three stages and nothing "
            "else. Read it and you have the entire arc of a run; each bracketed stage is a fragment "
            "refined in a later chapter.",
            "",
            link("calc/cli.py", 16, 20),
            "",
            "```python",
            "# calc/cli.py : lines 16-20",
            "def calc(text: str) -> float:",
            '    """Evaluate a single expression string end to end."""',
            "    " + U("Turn the string into tokens", "2") + "        # tokens = tokenize(text)",
            "    " + U("Turn the tokens into a syntax tree", "3") + "  # tree = parse(tokens)",
            "    " + U("Walk the tree to a number", "4") + "           # return evaluate(tree)",
            "```",
            "",
            "That is the book in miniature: chapters §2, §3, and §4 refine the three fragments. Notice "
            "the staging — each function consumes exactly what the previous one produced, and the data "
            "type changes at every arrow (string → tokens → tree → number). The clean handoffs are why "
            "each stage can be understood, and tested, on its own.",
        ),        litnb.md(
            "### §1.1 Around the core: the command line",
            "",
            "`calc()` is wrapped by `main()`, which only decides *where the text comes from* — an "
            "argument, or a line of standard input — and *where errors go*. Keeping this apart from "
            "`calc()` means the evaluation pipeline never has to know it is running in a terminal.",
            "",
            excerpt("calc/cli.py", 23, 35),
            "",
            "The `try/except` here is the program's single error boundary: the inner stages raise "
            "`SyntaxError`, `ZeroDivisionError`, or `TypeError` freely, and this one place turns them "
            "into a friendly message. We will see each stage trust that arrangement and not re-check.",
        ),
        litnb.md(
            "## See it run",
            "",
            "Before descending, let us confirm the whole pipeline works, end to end:",
        ),
        litnb.code(SETUP),
        litnb.code(
            "for expr in ['1 + 2 * 3', '(1 + 2) * 3', '-3 + 4', '8 - 2 - 1', '2 * (3 + 4) - 1']:\n"
            "    print(f'{expr:>16}  =  {calc.calc(expr)}')"
        ),
        litnb.md(
            "## Where this leads",
            "",
            "You now hold the skeleton: tokenize → parse → evaluate, wrapped by a thin command line. "
            "The next three chapters refine the three fragments in dependency order. We begin with the "
            "simplest, the tokenizer (§2), because the parser (§3) consumes its output, and the "
            "evaluator (§4) consumes the parser's.",
            "",
            "---",
            "",
            "### Fragment index",
            "",
            "| Fragment | Defined in |",
            "|---|---|",
            "| ⟨Turn the string into tokens⟩ | §2 |",
            "| ⟨Turn the tokens into a syntax tree⟩ | §3 |",
            "| ⟨Walk the tree to a number⟩ | §4 |",
        ),
    ]
    litnb.build(cells, os.path.join(OUT, "00_overview.ipynb"), title="calc — a literate reading")


# ---------------------------------------------------------------- Chapter 1: tokenizer
def tokenizer() -> None:
    cells = [
        litnb.md(
            "# §2 Reading input: the tokenizer",
            "",
            "*Reads `calc/tokens.py`. Refines the fragment ⟨Turn the string into tokens⟩ from §1.*",
            "",
            "The first stage answers a narrow question: what are the indivisible *words* of an "
            "expression? The tokenizer chops the raw string into a list of **tokens** — a number, an "
            "operator, a parenthesis — and throws away whitespace. Crucially it does **not** know that "
            "`*` binds tighter than `+`, or that parentheses group. That knowledge belongs to the "
            "parser (§3); keeping it out here is what makes both stages simple.",
        ),
        litnb.md(
            "## §2.1 A token, and the kinds there are",
            "",
            "A token is just a *kind* tag plus the original text it came from. The kinds are plain "
            "string constants — the parser will compare against them by name.",
            "",
            excerpt("calc/tokens.py", 11, 35),
            "",
            "Using bare strings as kinds (rather than an `Enum`) keeps the demo short; a larger language "
            "would reach for an enum to get exhaustiveness checking. That is the kind of *alternative* a "
            "literate reading should name even when the code does not take it.",
        ),
        litnb.md(
            "## §2.2 The scan loop",
            "",
            "Tokenizing is a single left-to-right pass with a manual cursor `i`. At each position one of "
            "four things is true, so the loop body is four cases:",
            "",
            link("calc/tokens.py", 38, 58),
            "",
            "```python",
            "# calc/tokens.py : lines 38-58  (skeleton)",
            "def tokenize(text: str) -> list[Token]:",
            "    tokens, i, n = [], 0, len(text)",
            "    while i < n:",
            "        c = text[i]",
            "        " + U("Skip whitespace", "2.2.1"),
            "        " + U("Emit a single-character operator or paren", "2.2.2"),
            "        " + U("Read a multi-digit number", "2.2.3"),
            "        " + U("Otherwise, reject the character", "2.2.4"),
            "    tokens.append(Token(EOF, ''))   # a sentinel the parser relies on",
            "    return tokens",
            "```",
            "",
            "The trailing `EOF` token is worth pausing on: it is a sentinel so the parser can always "
            "`peek()` one more token without bounds-checking. A small lie told here buys simplicity "
            "downstream — a recurring theme.",
        ),
        litnb.md(
            "### §2.2.1–§2.2.3 The cases that consume input",
            "",
            "Whitespace advances the cursor and produces nothing. A single character that appears in the "
            "`_SINGLE` table becomes one token. Digits (and `.`) are gathered greedily into one "
            "`NUMBER` token — this inner `while` is the only place the tokenizer looks at more than one "
            "character at a time:",
            "",
            excerpt("calc/tokens.py", 43, 55),
            "",
            "Note what the number case does *not* do: it does not convert to `float`. It keeps the raw "
            "text and lets the parser decide when to parse the value (§3.5). Each stage does the least "
            "it can.",
        ),
        litnb.md(
            "### §2.2.4 Rejecting the unknown",
            "",
            "Anything else is a lexical error, reported with its position. This is the tokenizer's only "
            "failure mode — and it is caught far away, at the command line's error boundary (§1.1).",
            "",
            excerpt("calc/tokens.py", 56, 56),
        ),
        litnb.md("## See it run", "", "Watch a string become tokens:"),
        litnb.code(SETUP),
        litnb.code(
            "from calc.tokens import tokenize\n"
            "for t in tokenize('1 + 2 * 3'):\n"
            "    print(f'{t.kind:<7} {t.value!r}')"
        ),
        litnb.md(
            "## Where this leads",
            "",
            "We now have a flat list of tokens with no structure beyond their order. Giving that list "
            "*structure* — discovering that `2 * 3` is a unit inside `1 + 2 * 3` — is the parser's job, "
            "and the subject of §3.",
        ),
    ]
    litnb.build(cells, os.path.join(OUT, "01_reading_input_the_tokenizer.ipynb"),
                title="Reading input: the tokenizer")


# ---------------------------------------------------------------- Chapter 2: parser
def parser() -> None:
    cells = [
        litnb.md(
            "# §3 Structure: the recursive-descent parser",
            "",
            "*Reads `calc/nodes.py` and `calc/parser.py`. Refines ⟨Turn the tokens into a syntax tree⟩.*",
            "",
            "The parser is the heart of `calc`. It takes the flat token list from §2 and discovers its "
            "structure, producing an **abstract syntax tree** whose *shape* captures precedence and "
            "grouping. Once the tree exists, evaluation (§4) is almost trivial — so the cleverness of "
            "the whole program lives here.",
        ),
        litnb.md(
            "## §3.1 What the parser produces: the AST",
            "",
            "Before reading how the tree is built, meet the tree itself. Three node kinds suffice for "
            "arithmetic: a literal `Num`, a binary `BinOp`, and a `Unary` negation.",
            "",
            excerpt("calc/nodes.py", 13, 31),
            "",
            "The comment in the source states the key idea: **the tree's shape encodes precedence and "
            "associativity.** `1 + 2 * 3` parses to `BinOp('+', Num(1), BinOp('*', Num(2), Num(3)))` — "
            "the multiplication is *nested deeper*, so the evaluator reaches it first, with no "
            "precedence logic of its own. The parser's job is to build exactly the right shape.",
        ),
        litnb.md(
            "## §3.2 The grammar, and a method per rule",
            "",
            "The parser is *recursive descent*: each grammar rule becomes one method, and rules that "
            "should bind tighter are nested deeper in the call chain. The grammar, lifted from the "
            "module's own docstring:",
            "",
            excerpt("calc/parser.py", 6, 8),
            "",
            "Read it top to bottom as *loosest to tightest*: an `expression` is a sum of `term`s; a "
            "`term` is a product of `factor`s; a `factor` is the atom — a number, a parenthesized "
            "expression, or a negation. Because `term` sits *inside* `expression`, multiplication is "
            "resolved before addition. Precedence is encoded in the call graph, not a table.",
        ),
        litnb.md(
            "## §3.3 The cursor",
            "",
            "Like the tokenizer, the parser walks its input with a cursor, exposed through three tiny "
            "helpers. `expect` is `advance` with an assertion — it is how the grammar's literal tokens "
            "(like a closing `)`) are consumed and checked at once.",
            "",
            excerpt("calc/parser.py", 25, 36),
        ),
        litnb.md(
            "## §3.4 Sums and products — and where associativity comes from",
            "",
            "`expression` and `term` are the same loop at two precedence levels. Read `expression`: parse "
            "one `term`, then *while* the next token is `+` or `-`, fold another `term` onto the right:",
            "",
            excerpt("calc/parser.py", 43, 55),
            "",
            "The `while` loop is where **left-associativity** is born. For `8 - 2 - 1` it builds "
            "`BinOp('-', BinOp('-', 8, 2), 1)` — the left operand grows as we iterate, so subtraction "
            "groups left-to-right and the answer is `5`, not `7`. Had we written this with recursion on "
            "the right instead of a loop, the grouping — and the answer — would flip. A one-line "
            "structural choice with an arithmetic consequence: exactly the kind of *tough place* a "
            "literate reading must not gloss over.",
        ),
        litnb.md(
            "## §3.5 Atoms, parentheses, and the recursion",
            "",
            "`factor` handles the three smallest things. A `NUMBER` becomes a `Num` (this is where the "
            "raw text from §2.2.3 finally becomes a `float`). A `(` re-enters `expression` — the single "
            "recursive call that lets parentheses override precedence to any depth. A leading `-` "
            "becomes a `Unary`.",
            "",
            excerpt("calc/parser.py", 57, 70),
            "",
            "That call back up to `self.expression()` inside the parentheses case is the 'descent' in "
            "recursive descent: an arbitrarily nested `((1 + 2) * (3 + 4))` is handled by the same three "
            "methods calling one another. And `parse()` (§3.3 earlier, lines 38–41) finishes by "
            "demanding `EOF`, so trailing garbage like `1 + 2 )` is rejected rather than silently "
            "ignored.",
        ),
        litnb.md("## See it run", "", "Parse two expressions and look at the shapes they produce:"),
        litnb.code(SETUP),
        litnb.code(
            "from calc.tokens import tokenize\n"
            "from calc.parser import parse\n"
            "for expr in ['1 + 2 * 3', '(1 + 2) * 3']:\n"
            "    print(expr, '->', parse(tokenize(expr)))"
        ),
        litnb.md(
            "Notice how `(1 + 2) * 3` puts the **addition** deeper than the multiplication — the "
            "opposite nesting from `1 + 2 * 3` — which is precisely how the parentheses change the "
            "answer. The tree *is* the meaning.",
        ),
        litnb.md(
            "## Design notes",
            "",
            "- **Precedence by grammar vs. by table.** Recursive descent encodes precedence in the call "
            "structure. The common alternative — a precedence-climbing or Pratt parser driven by a "
            "table of binding powers — scales better to many operators, at the cost of being less "
            "transparent. For four operators, layered rules win on clarity.",
            "- **No look-ahead beyond one token.** Every decision is made from `peek()` alone, which is "
            "what makes this grammar a clean `LL(1)`.",
            "",
            "## Where this leads",
            "",
            "The parser hands §4 a tree in which structure already means precedence. The evaluator can "
            "therefore be the simplest chapter in the book.",
        ),
    ]
    litnb.build(cells, os.path.join(OUT, "02_structure_the_parser.ipynb"),
                title="Structure: the recursive-descent parser")


# ---------------------------------------------------------------- Chapter 3: evaluator
def evaluator() -> None:
    cells = [
        litnb.md(
            "# §4 Meaning: the tree-walk evaluator",
            "",
            "*Reads `calc/evaluator.py`. Refines the fragment ⟨Walk the tree to a number⟩ from §1.*",
            "",
            "The last stage gives the tree a value. Because the parser (§3) already baked precedence into "
            "the tree's shape, evaluation has no precedence logic at all — it is a plain post-order "
            "walk: evaluate the children, then combine them.",
        ),
        litnb.md(
            "## §4.1 One function, three cases",
            "",
            "`evaluate` dispatches on the node kind, mirroring the three node types from §3.1:",
            "",
            excerpt("calc/evaluator.py", 11, 27),
            "",
            "- A `Num` is its own value — the base case that ends the recursion.",
            "- A `Unary` evaluates its operand and negates it.",
            "- A `BinOp` evaluates **both children first** (this is the post-order), then applies the "
            "operator. Because the `*` node sits below the `+` node in `1 + 2 * 3`, the multiplication "
            "is evaluated during the recursion into the children, before the addition combines them — "
            "precedence, for free, from the tree's shape.",
            "",
            "The closing `raise TypeError` is unreachable for trees the parser builds; it documents the "
            "invariant ('every node is one of the three kinds') and would catch a future fourth node "
            "kind that forgot to update this function.",
        ),
        litnb.md("## See it run", "", "Evaluate a tree, and re-run the whole pipeline for good measure:"),
        litnb.code(SETUP),
        litnb.code(
            "from calc.tokens import tokenize\n"
            "from calc.parser import parse\n"
            "from calc.evaluator import evaluate\n"
            "tree = parse(tokenize('1 + 2 * 3'))\n"
            "print('tree :', tree)\n"
            "print('value:', evaluate(tree))\n"
            "print('assoc:', evaluate(parse(tokenize('8 - 2 - 1'))), '(left-associative, so 5.0)')"
        ),
        litnb.md(
            "## The whole book in one line",
            "",
            "We have now read every stage. Composed, they are exactly the `calc()` of §1 — string to "
            "tokens to tree to number:",
        ),
        litnb.code(
            "print(evaluate(parse(tokenize('2 * (3 + 4) - 1'))))   # the three stages, by hand\n"
            "import calc\n"
            "print(calc.calc('2 * (3 + 4) - 1'))                  # the same thing, via the public API"
        ),
        litnb.md(
            "## Closing",
            "",
            "`calc` is four ideas: words (§2), structure (§3), meaning (§4), and a thin shell that wires "
            "them together (§1). The design decision that organizes everything is making the parser "
            "encode precedence in the tree's *shape*, which let the tokenizer stay ignorant of grammar "
            "and the evaluator stay ignorant of precedence. Read in dependency order, the program "
            "explains itself — which is the whole promise of a literate reading.",
        ),
    ]
    litnb.build(cells, os.path.join(OUT, "03_meaning_the_evaluator.ipynb"),
                title="Meaning: the tree-walk evaluator")


def main() -> None:
    global LINK
    import argparse

    ap = argparse.ArgumentParser(description="Build the demo literate reading of calc.")
    ap.add_argument("--repo-url", help="git host URL (e.g. https://github.com/you/literate-repo) "
                                       "to force line-precise permalinks instead of auto-detecting")
    ap.add_argument("--ref", default="HEAD", help="commit SHA, tag, or branch for the links")
    args = ap.parse_args()

    if args.repo_url:
        web_base, kind = litnb._normalize_remote(args.repo_url)
        # paths in this demo's links are relative to the git root, which contains demo/sample_repo
        root = litnb._run_git(["rev-parse", "--show-toplevel"], REPO) or os.path.dirname(HERE)
        LINK = litnb.SourceLinker(mode=kind or "github", web_base=web_base, ref=args.ref,
                                  root=root, notebooks_dir=OUT)
        print(f"links: {kind or 'github'} permalinks at {web_base}@{args.ref}")
    else:
        print(f"links: {LINK.mode}" + (" (relative file links; push to a git host and re-run, "
              "or pass --repo-url, for line-precise permalinks)" if LINK.mode == "local" else ""))

    os.makedirs(OUT, exist_ok=True)
    overview()
    tokenizer()
    parser()
    evaluator()
    print("Built notebooks in", OUT)
    for fn in sorted(os.listdir(OUT)):
        print("  ", fn)


if __name__ == "__main__":
    main()
