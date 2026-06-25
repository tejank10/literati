# literate-repo

Turn any code repository into a **literate-programming reading of itself** — a series of Jupyter
notebooks, organized as chapters, that explain the codebase front to back: what the system does, how
it's put together, and why. In the tradition of Knuth's *WEB* and Pharr & Humphries' *pbrt*.

## Quick start

1. **Build the skill** (stdlib only, no dependencies):

   ```bash
   make package        # -> dist/literate-repo.skill
   ```

2. **Install it** in the Claude app under Settings → Capabilities → Skills (upload the `.skill`).

3. **Point it at a repo:**

   > "Give me a literate-programming reading of this repo."
   > "Explain `<path-or-git-url>` as notebook chapters, pbrt-style."

It produces a `<repo>-literate/` folder: an overview notebook plus one chapter per subsystem (in
dependency order), each prose-first with real code woven in and clickable links to the exact source
lines. For large repos the reading is selective — deep on the spine, summarized on the periphery.

## See it in action

`demo/` is a runnable MVP: it reads a ~100-line arithmetic evaluator (`demo/sample_repo`) and
produces a four-chapter reading. Open `demo/calc-literate/00_overview.ipynb`, or regenerate it:

```bash
cd demo && python3 build_demo.py
```

## More

- **How it works, layout, and philosophy:** see [`SKILL.md`](SKILL.md) and [`references/`](references/).
- **Other make targets:** `make demo | check | test | clean`.

## License

MIT — see [LICENSE](LICENSE).
