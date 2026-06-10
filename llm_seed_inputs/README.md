# LLM-pregenerated initial inputs for `elfuzz direct`

Each `llm_seed_inputs/<sut>/` folder holds the initial input population for
`elfuzz direct <sut>`. These inputs are **generated ahead of time by a (stronger)
LLM**, not fetched from the web: local TGI models can't produce valid in-format
inputs from scratch, but seeding from a real online corpus would hand direct mode
a coverage head start that synth mode never gets. Pregenerated LLM inputs avoid
both problems and keep the RQ1 comparison fair.

## How it's used

`direct_initial.py` copies every real file in the resolved folder **verbatim**
into the initial population (with `--topup-llm` off, the folder *is* the
population — no TGI call needed to bootstrap). Resolution happens in
`cli/direct_mode.py::_resolve_seed_corpus`, overridable via the
`ELFUZZ_DIRECT_SEED_CORPUS` env var.

- One input per file. Filenames are provenance only — they are renamed to
  `input_NNNNNNNN<ext>` on copy.
- `README.md` and dotfiles (e.g. `.gitkeep`) are ignored and do **not** count as
  inputs.
- A SUT whose folder has no real input files yet is a **hard error** when you run
  `elfuzz direct` for it — fill the folder first.

| SUT | Format | Extension | Status |
| --- | --- | --- | --- |
| cpython3 | Python 3 source | `.py` | populated |
| jsoncpp | JSON | `.json` | placeholder |
| libxml2 | XML | `.xml` | placeholder |
| re2 | POSIX regex | `.re` | placeholder |
| librsvg | SVG | `.svg` | placeholder |
| cvc5 | SMT-LIB v2 | `.smt2` | placeholder |
| sqlite3 | SQLite SQL | `.sql` | placeholder |
