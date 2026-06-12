# cpython3 ELFuzz run — results

Run: full RQ1 pipeline on `cpython3`, fuzzer `elfuzz`, small model (Qwen2.5-Coder-1.5B).
Synthesis evolved gen0–gen94 (~6h); AFL++ campaign ran 21,660s (6h), 1 repetition.
Collected from `analysis/rq1/results/`, `extradata/rq1/afl_results/`, and `preset/cpython3/gen*/logs/`.

## rq1/  — analysis outputs (xlsx)
- `rq1_sum.xlsx`        — AFL coverage-over-time, mean across repetitions (per sheet = benchmark).
- `rq1_sum_1..10.xlsx`  — per-repetition coverage-over-time (only rep 1 has cpython3_elfuzz data this run).
- `rq1_std.xlsx`        — standard deviation across repetitions.
- `seed_cov.xlsx`       — seed-corpus coverage (time 0 point); cpython3 `elfuzz` = 19,634.

## afl_campaign/  — raw AFL++ coverage-over-time (the fuzzing phase)
- `cpython3_elm_plot_data.csv` — AFL `plot_data`. Key columns: `relative_time` (s), `edges_found`.
  ~4,230 rows; final `edges_found = 24,277` at t=21,660s. This is the raw curve behind rq1_sum.
- `cpython3_elm_fuzzer_stats.txt` — final AFL `fuzzer_stats` (execs, paths, crashes, etc.).
  Headline: edges_found 24,277 / total_edges 133,395 (bitmap_cvg 18.20%), execs_done 3,307,926
  (152.72 execs/s), corpus_count 6,043, 0 crashes, 0 hangs.
- `cpython3_elfuzz_1.tar.zst` — full untouched AFL output dir (queue, crashes, hangs, plot_data).

## evolution/  — synth coverage throughout the run (the evolution phase)
- `coverage_by_generation.csv` — one row per generation. Columns:
  - `generation` / `gen_index` (`initial` = -1)
  - `num_variants`           — variants evaluated that generation
  - `best_variant_edges`     — max edges covered by a single variant that gen
  - `population_union_edges` — distinct edges covered by the whole generation
- `per_gen_coverage_json.tar.zst` — raw per-gen `coverage.json` (variant → list of covered edge IDs)
  for all 95 generations, if you need per-variant / per-edge detail.

## Notes on metrics
- Synth edge counts (evolution/) and AFL `edges_found` (afl_campaign/) come from different
  instrumentation, so they are not directly comparable in absolute terms.
- cpython3 is a large SUT: AFL throughput is low (~150 execs/s vs ~7,700 for jsoncpp), so synthesis
  reaches far fewer generations (95 vs 297 for jsoncpp) within the same ~6h budget.
- Unlike jsoncpp, cpython3 does **not** saturate within the 6h AFL campaign — `edges_found` is still
  climbing at the end (22,531 at 1h → 24,277 at 6h), so the final-coverage comparison is meaningful here.
- Per-generation `population_union_edges` grows from 15,389 (gen0) to 20,399 (gen94); the run log's
  best-ever *elite* coverage is kept by the lattice across all generations — recompute from the raw
  archive if you want the elite trajectory.
