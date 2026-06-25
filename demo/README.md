# Demo — a literate reading of `calc`

This folder is a complete, runnable MVP of what the `literate-repo` skill produces. It takes one
small real repository and turns it into a four-chapter literate reading you can read front to back
— and execute.

```
demo/
├── sample_repo/        ← INPUT: a tiny but real repo (a ~100-line expression evaluator)
│   └── calc/           tokens.py · nodes.py · parser.py · evaluator.py · cli.py
├── calc-literate/      ← OUTPUT: the literate reading the skill produced
│   ├── 00_overview.ipynb                      §1  the system at a glance
│   ├── 01_reading_input_the_tokenizer.ipynb   §2  the tokenizer
│   ├── 02_structure_the_parser.ipynb          §3  the recursive-descent parser
│   └── 03_meaning_the_evaluator.ipynb         §4  the tree-walk evaluator
└── build_demo.py       ← regenerates calc-literate/ from sample_repo/ using ../scripts/litnb.py
```

## What to look at

Open `calc-literate/00_overview.ipynb` first and read the notebooks in numeric order. The reading
demonstrates every move the skill is built around:

- **Reading order ≠ file order.** The modules sort alphabetically on disk (`cli`, `evaluator`,
  `nodes`, `parser`, `tokens`); the reading follows concept dependencies instead
  (`cli` → `tokens` → `nodes`/`parser` → `evaluator`). The overview has a table making this explicit.
- **Top-down with named fragments.** §1 shows the whole program as `calc()` with three bracketed
  fragments — `⟨Turn the string into tokens 2⟩`, `⟨…tree 3⟩`, `⟨…number 4⟩` — each refined in a
  later chapter. You understand the whole before any part.
- **Prose leads; real code follows.** Every excerpt is faithful to the source and preceded by a
  **clickable link** to the file and lines it came from (the 📄 line above each code block). In this
  checkout the links are relative file links into `../sample_repo` (clickable in Jupyter). Once the
  repo is on GitHub and you re-run `make demo`, the build auto-detects the remote and commit and
  upgrades them to **line-precise permalinks** (e.g. `…/blob/<sha>/demo/sample_repo/calc/parser.py#L43-L55`).
  You can also force them with `python3 build_demo.py --repo-url https://github.com/you/literate-repo --ref <sha>`.
- **Explains the why.** The parser chapter dwells on the *tough place* — how the `while` loop in
  `expression()` creates left-associativity, and how the tree's shape (not any precedence table)
  encodes precedence — rather than restating the syntax.
- **A reading you can run.** Because `calc` is Python, the demonstration cells import the real
  package and execute; their outputs are saved in the notebooks (e.g. the parser chapter shows the
  two different tree shapes for `1 + 2 * 3` and `(1 + 2) * 3`).

## Regenerate / re-run it

```bash
cd demo
python3 build_demo.py                          # rebuild the four notebooks from source
python3 ../scripts/litnb.py --check calc-literate   # validate them

# optional: re-execute so the embedded outputs refresh
cd calc-literate
for nb in *.ipynb; do jupyter nbconvert --to notebook --execute --inplace "$nb"; done
```

The input repo works on its own too: `cd sample_repo && python3 -m calc "1 + 2 * 3"` prints `7.0`,
and `python3 -m pytest tests/` passes.
