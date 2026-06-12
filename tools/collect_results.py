#!/usr/bin/env python3
"""Collect the artefacts of one elfuzz run into results/elfuzz_<mode>_<sut>/.

The pipeline scripts (run_elfuzz_rq1.sh / run_elfuzz_direct_rq1.sh) leave their
output scattered across the elfuzz working tree:

    preset/<sut>/                  the evolution run dir (per-generation logs,
                                   and -- direct only -- the curated pool)
    analysis/rq1/results/*.xlsx    seed_cov + AFL coverage-over-time summaries
    extradata/rq1/afl_results/     the packed AFL++ output dir

This script gathers those into the committed results layout, deriving the two
summary CSVs (coverage_by_generation.csv, decisions_by_generation.csv) and the
per-generation coverage archive from the raw per-generation logs. Standard
library only.

Run it from (or point --run-root at) the working tree of the run you just
finished -- i.e. before the next run overwrites preset/<sut>/.

Layout produced (mirrors the existing runs):

    results/elfuzz_<mode>_<sut>/
      evolution/coverage_by_generation.csv
      evolution/per_gen_coverage_json.tar.zst
      pool/                              (direct mode only)
        inputs/  index.json  decisions_by_generation.csv
      rq1/*.xlsx
      afl_campaign/
        <sut>_<sub>_plot_data.csv
        <sut>_<sub>_fuzzer_stats.txt
        <sut>_<fuzzer>_<rep>.tar.zst

Usage:
    tools/collect_results.py --sut jsoncpp  --mode direct
    tools/collect_results.py --sut cpython3 --mode synth --rep 1 --run-root /home/appuser/elmfuzz
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# mode -> (fuzzer name used for the AFL tarball, "subname" used inside the AFL
# output dir and for the extracted plot_data/fuzzer_stats prefix).
MODE = {
    "synth":  {"fuzzer": "elfuzz",        "sub": "elm"},
    "direct": {"fuzzer": "elfuzz_direct", "sub": "elfuzz_direct"},
}


def _gen_dirs(rundir: str) -> list[tuple[str, int]]:
    """Ordered (dirname, gen_index) for every generation, incl. the direct
    'initial' bootstrap step at index -1 when present."""
    out = []
    if os.path.isdir(os.path.join(rundir, "initial", "logs")):
        out.append(("initial", -1))
    gens = []
    for name in os.listdir(rundir):
        if name.startswith("gen") and name[3:].isdigit():
            gens.append((name, int(name[3:])))
    gens.sort(key=lambda t: t[1])
    return out + gens


def _load_cov(path: str) -> dict[str, list[str]]:
    """coverage.json -> {candidate_id: [edge ids]} (flattened across models)."""
    with open(path) as f:
        doc = json.load(f)
    flat = {}
    for _model, cands in doc.items():
        for cid, edges in cands.items():
            flat[cid] = edges
    return flat


def _strip(edge: str) -> str:
    return edge.split(":", 1)[0]


def collect_evolution(rundir: str, out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)
    rows = []
    cumulative: set[str] = set()
    staging = tempfile.mkdtemp(prefix="pergen_")
    try:
        for name, idx in _gen_dirs(rundir):
            cov_path = os.path.join(rundir, name, "logs", "coverage.json")
            if not os.path.isfile(cov_path):
                continue
            cands = _load_cov(cov_path)
            num = len(cands)
            best = max((len({_strip(e) for e in es}) for es in cands.values()), default=0)
            gen_union = set()
            for es in cands.values():
                gen_union.update(_strip(e) for e in es)
            cumulative |= gen_union
            rows.append((name, idx, num, best, len(gen_union), len(cumulative)))
            # stage <name>/logs/coverage.json for the per-gen archive
            dst = os.path.join(staging, name, "logs")
            os.makedirs(dst, exist_ok=True)
            shutil.copy(cov_path, os.path.join(dst, "coverage.json"))

        csv_path = os.path.join(out_dir, "coverage_by_generation.csv")
        with open(csv_path, "w") as f:
            f.write("generation,gen_index,num_candidates,best_candidate_edges,"
                    "gen_union_edges,cumulative_union_edges\n")
            for name, idx, num, best, gu, cu in rows:
                f.write(f"{name},{idx},{num},{best},{gu},{cu}\n")
        print(f"  evolution: {len(rows)} generations -> {csv_path}")

        arch = os.path.join(out_dir, "per_gen_coverage_json.tar.zst")
        subprocess.run(["tar", "--zstd", "-cf", arch, "-C", staging, "."], check=True)
        print(f"  evolution: per-gen coverage -> {arch}")
    finally:
        shutil.rmtree(staging, ignore_errors=True)


def collect_pool(rundir: str, out_dir: str) -> None:
    """Direct mode only: the curated pool + per-generation churn summary."""
    pool_src = os.path.join(rundir, "pool")
    if not os.path.isdir(pool_src):
        print("  pool: no pool/ in run dir (synth mode?) - skipping")
        return
    os.makedirs(out_dir, exist_ok=True)

    inputs_dst = os.path.join(out_dir, "inputs")
    if os.path.isdir(inputs_dst):
        shutil.rmtree(inputs_dst)
    shutil.copytree(os.path.join(pool_src, "inputs"), inputs_dst)
    n_inputs = len(os.listdir(inputs_dst))
    if os.path.isfile(os.path.join(pool_src, "index.json")):
        shutil.copy(os.path.join(pool_src, "index.json"),
                    os.path.join(out_dir, "index.json"))
    print(f"  pool: {n_inputs} inputs + index.json")

    # decisions_by_generation.csv from each <gen>/logs/decisions.json
    reason_col = {"redundant": "discarded_redundant",
                  "no-coverage": "discarded_no_coverage",
                  "missing-file": "discarded_missing"}
    csv_path = os.path.join(out_dir, "decisions_by_generation.csv")
    cum_add = cum_repl = 0
    with open(csv_path, "w") as f:
        f.write("generation,gen_index,candidates,added,replaced,discarded,"
                "discarded_redundant,discarded_no_coverage,discarded_missing,"
                "cumulative_added,cumulative_replaced\n")
        for name, idx in _gen_dirs(rundir):
            dpath = os.path.join(rundir, name, "logs", "decisions.json")
            if not os.path.isfile(dpath):
                continue
            with open(dpath) as df:
                dec = json.load(df)
            counts = {"added": 0, "replaced": 0, "discarded": 0,
                      "discarded_redundant": 0, "discarded_no_coverage": 0,
                      "discarded_missing": 0}
            for entry in dec.values():
                act = entry.get("action")
                if act == "add":
                    counts["added"] += 1
                elif act == "replace":
                    counts["replaced"] += 1
                elif act == "discard":
                    counts["discarded"] += 1
                    col = reason_col.get(entry.get("reason"))
                    if col:
                        counts[col] += 1
            cum_add += counts["added"]
            cum_repl += counts["replaced"]
            f.write(f"{name},{idx},{len(dec)},{counts['added']},{counts['replaced']},"
                    f"{counts['discarded']},{counts['discarded_redundant']},"
                    f"{counts['discarded_no_coverage']},{counts['discarded_missing']},"
                    f"{cum_add},{cum_repl}\n")
    print(f"  pool: decisions -> {csv_path} (cumulative added={cum_add}, replaced={cum_repl})")


def collect_rq1(run_root: str, out_dir: str) -> None:
    src = os.path.join(run_root, "analysis", "rq1", "results")
    xlsx = sorted(glob.glob(os.path.join(src, "*.xlsx")))
    if not xlsx:
        print(f"  rq1: no .xlsx in {src} - skipping")
        return
    os.makedirs(out_dir, exist_ok=True)
    for x in xlsx:
        shutil.copy(x, os.path.join(out_dir, os.path.basename(x)))
    print(f"  rq1: copied {len(xlsx)} xlsx from {src}")


def collect_afl(run_root: str, out_dir: str, sut: str, fuzzer: str, sub: str, rep: int) -> None:
    tar = os.path.join(run_root, "extradata", "rq1", "afl_results",
                       f"{sut}_{fuzzer}_{rep}.tar.zst")
    if not os.path.isfile(tar):
        print(f"  afl: tarball not found at {tar} - skipping")
        return
    os.makedirs(out_dir, exist_ok=True)
    shutil.copy(tar, os.path.join(out_dir, os.path.basename(tar)))

    with tempfile.TemporaryDirectory(prefix="afl_") as tmp:
        subprocess.run(["tar", "--zstd", "-xf", tar, "-C", tmp], check=True)
        for kind, suffix in (("plot_data", "_plot_data.csv"),
                             ("fuzzer_stats", "_fuzzer_stats.txt")):
            hits = glob.glob(os.path.join(tmp, "*", "default", kind))
            if not hits:
                print(f"  afl: warning - no {kind} inside tarball")
                continue
            shutil.copy(hits[0], os.path.join(out_dir, f"{sut}_{sub}{suffix}"))
    print(f"  afl: tarball + plot_data + fuzzer_stats ({sut}_{sub}_*)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sut", required=True, help="e.g. jsoncpp, cpython3")
    ap.add_argument("--mode", required=True, choices=["synth", "direct"])
    ap.add_argument("--rep", type=int, default=1, help="AFL repetition index (default 1)")
    ap.add_argument("--run-root", default=REPO_ROOT,
                    help="working tree of the finished run (default: this repo). "
                         "In the container, e.g. /home/appuser/elmfuzz")
    ap.add_argument("--out", default=None,
                    help="output dir (default results/elfuzz_<mode>_<sut>/)")
    args = ap.parse_args()

    m = MODE[args.mode]
    run_root = os.path.abspath(args.run_root)
    rundir = os.path.join(run_root, "preset", args.sut)
    out = args.out or os.path.join(REPO_ROOT, "results", f"elfuzz_{args.mode}_{args.sut}")

    if not os.path.isdir(rundir):
        print(f"error: run dir not found: {rundir}", file=sys.stderr)
        return 1

    print(f"Collecting {args.mode} / {args.sut} from {run_root}\n  -> {out}")
    collect_evolution(rundir, os.path.join(out, "evolution"))
    if args.mode == "direct":
        collect_pool(rundir, os.path.join(out, "pool"))
    collect_rq1(run_root, os.path.join(out, "rq1"))
    collect_afl(run_root, os.path.join(out, "afl_campaign"),
                args.sut, m["fuzzer"], m["sub"], args.rep)
    print("done. (write/refresh the run's README.md by hand.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
