#!/usr/bin/env python3
"""Compare the edge sets covered by elfuzz synth vs elfuzz direct.

Answers: is one tool's coverage a (proper) superset of the other's, or are they
incomparable (each reaches edges the other misses)? Reports |synth|, |direct|,
their intersection, each tool's unique edges, and the subset relation.

Two modes:

  evolution                Compare the synthesis-phase edge sets read from the
                           stored per-generation getcov data, for each SUT:
                           results/elfuzz_{synth,direct}_<sut>/evolution/
                               per_gen_coverage_json.tar.zst
                           Both tools share this getcov edge space, so the sets
                           are directly comparable. This is the *search reach*,
                           not the shipped corpus.

  sets L1 FILE1 L2 FILE2   Generic comparison of two edge-list files (one edge
                           per line, optionally "id:bucket"). Use this for the
                           AFL / seed-corpus comparison once you have afl-showmap
                           dumps from the container, e.g.
                             compare_edge_sets.py sets synth synth.cov direct direct.cov

Edge ids are compared with the ":bucket" hit-count suffix stripped, so the unit
is "distinct edge", matching the cumulative_union_edges counts in the CSVs.

Usage:
    tools/compare_edge_sets.py evolution [--suts jsoncpp cpython3] [--out FILE]
    tools/compare_edge_sets.py sets <label1> <file1> <label2> <file2> [--out FILE]
"""
import argparse
import glob
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(REPO_ROOT, "results")


def _strip(edge: str) -> str:
    return edge.split(":", 1)[0]


def load_archive_edges(arch: str) -> set:
    """Union of edges over every generation/variant in a per_gen getcov archive."""
    import json
    tmp = tempfile.mkdtemp(prefix="edgecmp_")
    try:
        subprocess.run(["tar", "-C", tmp, "-xf", arch], check=True)
        edges = set()
        for jf in glob.glob(os.path.join(tmp, "*", "logs", "coverage.json")):
            with open(jf) as f:
                doc = json.load(f)
            for _model, variants in doc.items():
                for _v, elist in variants.items():
                    edges.update(_strip(e) for e in elist)
        return edges
    finally:
        subprocess.run(["rm", "-rf", tmp], check=False)


def load_cov_file(path: str) -> set:
    """Edge set from an afl-showmap dump (one 'id:bucket' per line)."""
    with open(path) as f:
        return {_strip(line.strip()) for line in f if line.strip()}


def compare(name: str, la: str, A: set, lb: str, B: set, out) -> None:
    inter, a_only, b_only = A & B, A - B, B - A
    def p(*xs):
        print(*xs)
        if out:
            print(*xs, file=out)
    p(f"==================== {name} ====================")
    p(f"  {la} edges:              {len(A)}")
    p(f"  {lb} edges:              {len(B)}")
    p(f"  intersection (both):     {len(inter)}")
    p(f"  {la}-only:               {len(a_only)}")
    p(f"  {lb}-only:               {len(b_only)}")
    p(f"  {lb} subset of {la}?     {B.issubset(A)}")
    p(f"  {la} subset of {lb}?     {A.issubset(B)}")
    if A and B:
        rel = ("incomparable (each covers edges the other misses)"
               if a_only and b_only else
               f"{lb} is a subset of {la}" if not b_only else
               f"{la} is a subset of {lb}")
        p(f"  relation:                {rel}")
        p(f"  union of both:           {len(A | B)}")
    p("")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)

    ev = sub.add_parser("evolution", help="compare stored getcov evolution edge sets")
    ev.add_argument("--suts", nargs="+", default=["jsoncpp", "cpython3"])
    ev.add_argument("--out", help="also write the report to this file")

    st = sub.add_parser("sets", help="compare two afl-showmap edge-list files")
    st.add_argument("label1")
    st.add_argument("file1")
    st.add_argument("label2")
    st.add_argument("file2")
    st.add_argument("--out", help="also write the report to this file")

    args = ap.parse_args()
    out = open(args.out, "w") if getattr(args, "out", None) else None
    try:
        if out:
            print(f"# elfuzz synth vs direct - edge-set comparison\n", file=out)
        if args.mode == "evolution":
            if out:
                print("Mode: evolution (synthesis-phase getcov edge sets; search reach,"
                      " not shipped corpus).\n", file=out)
            for sut in args.suts:
                s = os.path.join(RESULTS, f"elfuzz_synth_{sut}/evolution/per_gen_coverage_json.tar.zst")
                d = os.path.join(RESULTS, f"elfuzz_direct_{sut}/evolution/per_gen_coverage_json.tar.zst")
                for p in (s, d):
                    if not os.path.isfile(p):
                        print(f"error: missing {p}", file=sys.stderr)
                        return 1
                print(f"[{sut}] loading synth ...", file=sys.stderr)
                S = load_archive_edges(s)
                print(f"[{sut}] loading direct ...", file=sys.stderr)
                D = load_archive_edges(d)
                compare(f"{sut} (evolution, getcov)", "synth", S, "direct", D, out)
        else:
            A = load_cov_file(args.file1)
            B = load_cov_file(args.file2)
            compare(f"{args.file1} vs {args.file2}", args.label1, A, args.label2, B, out)
        if out:
            print(f"written to {args.out}", file=sys.stderr)
    finally:
        if out:
            out.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
