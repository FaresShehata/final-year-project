# Reproducing the data in `results/`

Every artefact under `results/` is produced by one of two end-to-end pipeline
scripts at the repository root:

| Script | Configuration | Produces |
| --- | --- | --- |
| [`run_elfuzz_rq1.sh`](../run_elfuzz_rq1.sh) | `elfuzz synth` (the original ELFuzz: evolve input *generators*, then run them) | `results/elfuzz_synth_<SUT>/` |
| [`run_elfuzz_direct_rq1.sh`](../run_elfuzz_direct_rq1.sh) | `elfuzz direct` (ours: the LLM generates *inputs* directly) | `results/elfuzz_direct_<SUT>/` |

Both wrap the `elfuzz` CLI and differ only in how the seed corpus is generated;
they share the same downstream `rq1.seed_cov` and `rq1.afl` measurement steps, so
the two configurations are directly comparable.

> The `results/` directory is the *curated copy* of each run, lifted out of the
> container after the pipeline completes. The scripts themselves write into the
> elfuzz working tree (`evaluation/`, `extradata/`, the analysis dirs); see
> [Copying results out](#5-copying-results-out-of-the-container) below.

## 1. Prerequisites

- The ELFuzz / OSS-Fuzz **container** with the `elfuzz` CLI on `PATH` (override
  with `ELFUZZ=/path/to/elfuzz`). All commands below run inside it.
- A **GPU** and the **TGI** model server reachable; the runs here use the small
  local model **Qwen2.5-Coder-1.5B** (`--use-small-model`, fits a 12 GB GPU).
- The per-SUT instrumented harnesses staged under
  `evaluation/workdir/<SUT>/` (the `prepare` step does this) and the SUT seed
  corpora under `extradata/seeds/`.
- `afl-showmap` / `afl-fuzz` (AFL++) on `PATH`.

## 2. Running a pipeline

Each script has a `CHOICES` block at the top. The key knobs:

- `SUT` — one of `jsoncpp | libxml2 | re2 | librsvg | cvc5 | sqlite3 | cpython3`.
  The committed runs cover **jsoncpp** and **cpython3**.
- evolution budget — `SYNTH_TOTAL_TIME` (synth) / `DIRECT_TOTAL_TIME` (direct),
  in seconds. The committed runs use a **6-hour** wall-clock budget.
- `AFL_TIME` — AFL++ campaign length in seconds (**~6 h** here), `AFL_REPEAT=1`.
- `SYNTH_RESUME=1` / `DIRECT_RESUME=1` — resume evolution from the last
  completed generation instead of starting fresh.

```bash
# synth, e.g. cpython3 (edit SUT= at the top of the script first)
./run_elfuzz_rq1.sh

# direct, e.g. jsoncpp
./run_elfuzz_direct_rq1.sh
```

Stages run by each script:

**`run_elfuzz_rq1.sh` (synth):**
1. `synth` — evolve a population of input generators (6 h budget).
2. `produce` — run the elite generators for ~200 s to emit a large seed corpus.
3. `minimize` — `afl-cmin` the corpus.
4. `run rq1.seed_cov` — coverage of the minimised corpus (writes `seed_cov.xlsx`).
5. `run rq1.afl` — the AFL++ campaign seeded with that corpus.

**`run_elfuzz_direct_rq1.sh` (direct):**
1. `direct` — the LLM generates inputs directly, evolving a single curated pool
   (6 h budget). There is **no `produce` step** — the evolved pool *is* the corpus.
2. `minimize` — `afl-cmin` the pool.
3. `run rq1.seed_cov` — coverage of the minimised corpus.
4. `run rq1.afl` — the AFL++ campaign.

Both scripts tee a timestamped log to `logs/run_*.log`.

## 3. What each `results/<run>/` subfolder is

(See each run's own `README.md` for the run-specific numbers.)

- `evolution/coverage_by_generation.csv` — one row per generation
  (`generation, gen_index, num_candidates, best_candidate_edges, gen_union_edges,
  cumulative_union_edges`); the coverage-vs-generation curve. From stages 1.
- `evolution/per_gen_coverage_json.tar.zst` — raw per-generation `coverage.json`
  (the `getcov` edge ids), used for the evolution-phase edge-set comparison.
- `pool/` (**direct only**) — the evolving input pool: `inputs/` (the final seed
  corpus), `index.json` (per-input edges/size), `decisions_by_generation.csv`
  (add/replace/discard churn).
- `rq1/seed_cov.xlsx` — seed-corpus coverage (the RQ1 metric). From stage
  `rq1.seed_cov`.
- `rq1/rq1_sum*.xlsx`, `rq1_std.xlsx` — AFL coverage-over-time summaries.
- `afl_campaign/<SUT>_<fuzzer>_plot_data.csv` — AFL `plot_data` (`relative_time`,
  `edges_found`, …); the coverage-over-time curve for the fuzzing phase.
- `afl_campaign/<SUT>_<fuzzer>_fuzzer_stats.txt` — final AFL stats.
- `afl_campaign/<SUT>_<fuzzer>_1.tar.zst` — the full AFL output directory.

## 4. Derived data used by the report

These regenerate the figures/tables and the auxiliary analyses; none require a
re-run of the pipeline.

**Tidy CSVs for the evaluation chapter** (`Report/data/<SUT>/*.csv`):

```bash
python Report/data/extract_results.py --run results/elfuzz_synth_jsoncpp  --sut jsoncpp  --tool synth
python Report/data/extract_results.py --run results/elfuzz_direct_jsoncpp --sut jsoncpp  --tool direct
# ...and likewise for cpython3
```

**Input validity** of each final direct pool:

```bash
python tools/check_validity_jsoncpp.py   # 0/116 valid JSON  (jsoncpp)
python tools/check_validity_cpython3.py  # 422/1264 compile  (cpython3)
```

**Synth-vs-direct edge-set comparison** ([`results/edge_set_comparison.txt`](edge_set_comparison.txt)):

- *Evolution phase* (synthesis-phase `getcov` edge sets, from the stored
  `per_gen_coverage_json.tar.zst`):

  ```bash
  python tools/compare_edge_sets.py evolution --out results/edge_set_comparison.txt
  ```

- *Shipped seed corpus* (`afl-showmap`, run **in the container**). This must match
  the `rq1.seed_cov` measurement exactly to be comparable to the figures in the
  report — in particular `-t 5000`, the **staged `workdir`** harness (run
  `prepare` first), and for cpython3 `AFL_MAP_SIZE=2097152`. Pointing at the
  un-staged `binary/` harness or using afl-showmap's default ~1 s timeout
  silently under-counts cpython3 (slow Python inputs time out). For each SUT and
  tool, extract the minimised seed tarball from
  `extradata/seeds/cmined_with_control_bytes/<SUT>/{elm,elfuzz_direct}/<latest>.tar.zst`
  and run:

  ```bash
  cd "$ELFUZZ_PROJECT_ROOT"                       # the elmfuzz tree in the container
  python evaluation/workdir/prepare.py -f -z elm cpython3        # stage synth harness
  export AFL_MAP_SIZE=2097152                                    # cpython3 only
  BIN=evaluation/workdir/cpython3/fuzzer
  afl-showmap -q -C -t 5000 -m none -i <synth_seeds_dir> -o synth.cov  -- $BIN @@
  python evaluation/workdir/prepare.py -f -z elfuzz_direct cpython3   # stage direct harness
  afl-showmap -q -C -t 5000 -m none -i <direct_seeds_dir> -o direct.cov -- $BIN @@
  ```

  Then compare the two dumps (works on the host):

  ```bash
  python tools/compare_edge_sets.py sets synth synth.cov direct direct.cov
  ```

  For jsoncpp the binary is `evaluation/workdir/jsoncpp/jsoncpp_fuzzer` and no
  `AFL_MAP_SIZE` is needed. Edge counts should reproduce `seed_cov.xlsx`
  (jsoncpp 568/163; cpython3 ≈19,634/9,790, with a few edges of run-to-run
  nondeterminism on cpython3).

## 5. Collecting a run into `results/`

After a pipeline finishes, the artefacts live scattered across the elfuzz working
tree, not in this repo:

| Source (in the run's working tree) | Becomes |
| --- | --- |
| `preset/<SUT>/{initial,gen0..genN}/logs/coverage.json` | `evolution/coverage_by_generation.csv` + `per_gen_coverage_json.tar.zst` (derived) |
| `preset/<SUT>/{initial,gen0..genN}/logs/decisions.json` | `pool/decisions_by_generation.csv` (derived, direct only) |
| `preset/<SUT>/pool/{inputs,index.json}` | `pool/inputs/`, `pool/index.json` (direct only) |
| `analysis/rq1/results/*.xlsx` | `rq1/*.xlsx` |
| `extradata/rq1/afl_results/<SUT>_<fuzzer>_<rep>.tar.zst` | `afl_campaign/*` (the tarball + extracted `plot_data.csv` / `fuzzer_stats.txt`) |

[`tools/collect_results.py`](../tools/collect_results.py) does this gathering and
derivation in one step. Run it **before the next run overwrites
`preset/<SUT>/`**, pointing `--run-root` at the working tree:

```bash
# from this repo, with the run still in ./preset/<SUT>/
python tools/collect_results.py --sut jsoncpp  --mode direct
python tools/collect_results.py --sut cpython3 --mode synth

# or against the container's elmfuzz tree
python tools/collect_results.py --sut cpython3 --mode direct \
    --run-root /home/appuser/elmfuzz --rep 1
```

It writes `results/elfuzz_<mode>_<SUT>/`. The two summary CSVs and the
per-generation archive are computed from the raw per-generation logs (the
`coverage_by_generation.csv` schema is `generation, gen_index, num_candidates,
best_candidate_edges, gen_union_edges, cumulative_union_edges`); `rq1/*.xlsx`,
the AFL tarball, `plot_data`, and `fuzzer_stats` are copied verbatim. The small
CSV/xlsx/txt files are committed; the large `.tar.zst` archives hold the raw
per-generation and AFL output for recomputing edge sets. The per-run `README.md`
is written by hand.
