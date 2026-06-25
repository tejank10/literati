# calc

A tiny arithmetic expression evaluator: a pocket calculator that understands
`+ - * /`, parentheses, and unary minus, with the usual precedence.

```
$ python -m calc "1 + 2 * 3"
7.0
```

It is structured as the classic three-stage pipeline — **tokenize → parse →
evaluate** — split across small modules so it can serve as a teaching example.
This repo is the input for the `literate-repo` skill's demo; the literate
reading produced from it lives in `../calc-literate/`.
