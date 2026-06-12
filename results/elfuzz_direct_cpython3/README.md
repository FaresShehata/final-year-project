# cpython3 ELFuzz-DIRECT run — results

Run: full RQ1 pipeline via `run_elfuzz_direct_rq1.sh` on `cpython3`, fuzzer
`elfuzz_direct`, small model (Qwen2.5-Coder-1.5B).
Direct evolution ran ~6h (initial + gen0–gen60, 62 steps); AFL++ campaign ran
21,660s (6h), 1 repetition. Direct seeds its initial population from the
downloaded corpus (`seed_corpora/cpython3/`); for cpython3 this was only **5
inputs** (expected — the Python seed corpus used here is small), versus 500 for
jsoncpp.

Layout mirrors `../elfuzz_synth_cpython3/`, plus a `pool/` folder specific to
direct mode (it evolves a single growing input pool).

## rq1/  — analysis outputs (xlsx)
Same as the synth folder: `rq1_sum.xlsx` (AFL coverage-over-time mean),
`rq1_sum_1..10.xlsx` (per-repetition), `rq1_std.xlsx`, `seed_cov.xlsx`. The
`elfuzz_direct` column/data is what this run produced; cpython3 `elfuzz_direct`
seed coverage = **9,790** (afl-showmap), vs 19,634 for synth.

## afl_campaign/  — raw AFL++ coverage-over-time (fuzzing phase)
- `cpython3_elfuzz_direct_plot_data.csv` — AFL `plot_data`; key columns
  `relative_time` (s), `edges_found` (final 22,523 at t=21,660s).
- `cpython3_elfuzz_direct_fuzzer_stats.txt` — final AFL stats. Headline:
  edges_found 22,523 / total_edges 133,395 (bitmap_cvg 16.88%), execs_done
  3,332,625 (153.86 execs/s), corpus_count 6,636, 0 crashes, 0 hangs.
- `cpython3_elfuzz_direct_1.tar.zst` — full AFL output dir.

## evolution/  — coverage throughout the direct run
- `coverage_by_generation.csv` — one row per step (`initial` = gen_index -1):
  - `num_candidates`          — candidates evaluated that generation
  - `best_candidate_edges`    — max edges by a single candidate that gen
  - `gen_union_edges`         — distinct edges covered by that gen's candidates
  - `cumulative_union_edges`  — distinct edges discovered so far (running union)
  Runs from initial (5 candidates, cumulative 16,427) to gen60 (cumulative 25,261).
- `per_gen_coverage_json.tar.zst` — raw per-gen `coverage.json`
  (`{"direct": {cand_id: [edge ids]}}`) for all 62 steps.

## pool/  — the evolving input pool (direct-mode specific)
Direct mode keeps one growing, coverage-curated pool (add / replace / evict),
unlike synth's independent per-generation populations.
- `inputs/` — the **1,264 final pool inputs** (the synthesized seed corpus).
- `index.json` — per-input record: `{input_id: {edges:[...], size}}`.
- `decisions_by_generation.csv` — the churn that produced the pool:
  per step `added`, `replaced`, `discarded` (+ `discarded_redundant /
  _no_coverage / _missing`) and running `cumulative_added` / `cumulative_replaced`.
  For cpython3 the pool grew monotonically to 1,264 (cumulative_added = 1,264,
  146 replacements, no dominated evictions).

## Notes on metrics
- Synth edge counts (evolution/) and AFL `edges_found` (afl_campaign/) come from
  different instrumentation, so they are not directly comparable in absolute terms.
- cpython3 does **not** saturate within the 6h AFL campaign — coverage is still
  climbing at the end — so the final-coverage comparison is meaningful (this run:
  direct 22,523 vs synth 24,277 AFL edges).
