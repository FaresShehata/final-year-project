# jsoncpp ELFuzz run — results

Run: full RQ1 pipeline on `jsoncpp`, fuzzer `elfuzz`, small model (Qwen2.5-Coder-1.5B).
Synthesis evolved gen0–gen296 (~6h, in 4 resumed segments); AFL++ campaign ran 21,660s (6h), 1 repetition.
Collected from `analysis/rq1/results/`, `extradata/rq1/afl_results/`, and `preset/jsoncpp/gen*/logs/`.

## rq1/  — analysis outputs (xlsx)
- `rq1_sum.xlsx`        — AFL coverage-over-time, mean across repetitions (per sheet = benchmark).
- `rq1_sum_1..10.xlsx`  — per-repetition coverage-over-time (only rep 1 has jsoncpp_elfuzz data this run).
- `rq1_std.xlsx`        — standard deviation across repetitions.
- `seed_cov.xlsx`       — seed-corpus coverage (time 0 point).

## afl_campaign/  — raw AFL++ coverage-over-time (the fuzzing phase)
- `jsoncpp_elm_plot_data.csv` — AFL `plot_data`. Key columns: `relative_time` (s), `edges_found`.
  ~4,240 rows; final `edges_found = 667` at t=21,660s. This is the raw curve behind rq1_sum.
- `jsoncpp_elm_fuzzer_stats.txt` — final AFL `fuzzer_stats` (execs, paths, crashes, etc.).
- `jsoncpp_elfuzz_1.tar.zst` — full untouched AFL output dir (queue, crashes, hangs, plot_data).

## evolution/  — synth coverage throughout the run (the evolution phase)
- `coverage_by_generation.csv` — one row per generation. Columns:
  - `generation` / `gen_index` (`initial` = -1)
  - `num_variants`           — variants evaluated that generation
  - `best_variant_edges`     — max edges covered by a single variant that gen
  - `population_union_edges` — distinct edges covered by the whole generation
- `per_gen_coverage_json.tar.zst` — raw per-gen `coverage.json` (variant → list of covered edge IDs)
  for all 297 generations, if you need per-variant / per-edge detail.

## Notes on metrics
- Synth edge counts (evolution/) and AFL `edges_found` (afl_campaign/) come from different
  instrumentation, so they are not directly comparable in absolute terms.
- Per-generation `best_variant_edges` plateaus ~450 after ~gen50. The run log's "almost bests"
  (~588) is the best-ever *elite* kept by the lattice across all generations, not a single
  per-gen variant — recompute from the raw archive if you want the elite trajectory.
