# jsoncpp ELFuzz-DIRECT run — results

Run: full RQ1 pipeline via `run_elfuzz_direct_rq1.sh` on `jsoncpp`, fuzzer
`elfuzz_direct`, small model (Qwen2.5-Coder-1.5B).
Direct evolution ran (initial + gen0–gen69, 71 steps); AFL++ campaign ran
**18,060s (~5h)**, 1 repetition. Direct seeds its initial population from the
downloaded corpus (`seed_corpora/jsoncpp/`); for this run that was only **5
inputs**.

> **Note — this supersedes the earlier jsoncpp-direct run** (kept untouched at
> `../elfuzz_direct_jsoncpp_old/`). This run differs substantially from that one:
> 5 initial seeds (was 500), final pool of 116 inputs (was 450), seed coverage
> 163 (was 463), and a ~5h AFL campaign (was 6h). AFL still saturates jsoncpp's
> reachable frontier at 667 edges either way.

Layout mirrors `../elfuzz_synth_jsoncpp/` and `../elfuzz_direct_cpython3/`, plus a
`pool/` folder specific to direct mode (it evolves a single growing input pool).

## rq1/  — analysis outputs (xlsx)
Same as the synth folder: `rq1_sum.xlsx` (AFL coverage-over-time mean),
`rq1_sum_1..10.xlsx` (per-repetition), `rq1_std.xlsx`, `seed_cov.xlsx`. The
`elfuzz_direct` column/data is what this run produced; jsoncpp `elfuzz_direct`
seed coverage = **163** (afl-showmap).

## afl_campaign/  — raw AFL++ coverage-over-time (fuzzing phase)
- `jsoncpp_elfuzz_direct_plot_data.csv` — AFL `plot_data`; key columns
  `relative_time` (s), `edges_found` (final 667 at t=18,060s).
- `jsoncpp_elfuzz_direct_fuzzer_stats.txt` — final AFL stats. Headline:
  edges_found 667 / total_edges 5,236 (bitmap_cvg 12.74%), execs_done
  141,670,511 (7,844 execs/s), corpus_count 1,468, 0 crashes, 0 hangs, run_time 18,060s.
- `jsoncpp_elfuzz_direct_1.tar.zst` — full AFL output dir.

## evolution/  — coverage throughout the direct run
- `coverage_by_generation.csv` — one row per step (`initial` = gen_index -1):
  - `num_candidates`          — candidates evaluated that generation
  - `best_candidate_edges`    — max edges by a single candidate that gen
  - `gen_union_edges`         — distinct edges covered by that gen's candidates
  - `cumulative_union_edges`  — distinct edges discovered so far (running union)
  Runs from initial (5 candidates, cumulative 330) to gen69 (cumulative 625).
- `per_gen_coverage_json.tar.zst` — raw per-gen `coverage.json`
  (`{"direct": {cand_id: [edge ids]}}`) for all 71 steps.

## pool/  — the evolving input pool (direct-mode specific)
Direct mode keeps one growing, coverage-curated pool (add / replace / evict),
unlike synth's independent per-generation populations.
- `inputs/` — the **116 final pool inputs** (the synthesized seed corpus).
- `index.json` — per-input record: `{input_id: {edges:[...], size}}`.
- `decisions_by_generation.csv` — the churn that produced the pool:
  per step `added`, `replaced`, `discarded` (+ `discarded_redundant /
  _no_coverage / _missing`) and running `cumulative_added` / `cumulative_replaced`.
  For this run the pool ended at 116 (cumulative_added = 116, 605 replacements).

## Notes on metrics
- Synth edge counts (evolution/) and AFL `edges_found` (afl_campaign/) come from
  different instrumentation, so they are not directly comparable in absolute terms.
- jsoncpp **saturates** AFL's reachable frontier (667 edges) well within the
  campaign, so the final AFL coverage is not a discriminating metric here — the
  signal is in seed coverage and time-to-plateau.
