#!/usr/bin/env python3
"""Mutate parent collections of inputs into new variant collections via the LLM.

Replaces the `genvariants_parallel.py + genoutputs.py` pipeline for direct mode.
Each variant is a *directory* of M inputs produced by repeatedly applying one
mutation operator to the parent's inputs.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm_provider import create_provider
from direct_common import (
    build_direct_prompt,
    postprocess_copilot,
    random_complete_cut,
    random_fim_cut,
    random_splice_cuts,
    stop_for,
)


ALL_OPS = ("complete", "infilled", "lmsplice")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("seed_paths", nargs="+", help="Parent collection directories")
    p.add_argument("--backend", choices=["huggingface", "copilot"], required=True)
    p.add_argument("-M", "--model", required=True)
    p.add_argument("-E", "--endpoint", default=None)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--log-dir", required=True)
    p.add_argument("-n", "--num-variants", type=int, required=True)
    p.add_argument("--inputs-per-collection", type=int, required=True)
    p.add_argument("--input-extension", required=True)
    p.add_argument("--format-name", required=True)
    p.add_argument("--format-description", required=True)
    p.add_argument("--temperature", type=float, default=0.6)
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("-j", "--jobs", type=int, default=16)
    return p.parse_args()


def list_collection_inputs(collection_dir: str) -> list[str]:
    return sorted(
        os.path.join(collection_dir, f)
        for f in os.listdir(collection_dir)
        if os.path.isfile(os.path.join(collection_dir, f))
    )


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def make_one_input(
    provider,
    backend: str,
    op: str,
    parent_inputs: list[str],
    fmt_name: str,
    fmt_desc: str,
    temperature: float,
    max_new_tokens: int,
) -> str:
    if op == "complete":
        text = read_text(random.choice(parent_inputs))
        prefix = random_complete_cut(text)
        suffix = ""
    elif op == "infilled":
        text = read_text(random.choice(parent_inputs))
        prefix, suffix = random_fim_cut(text)
    elif op == "lmsplice":
        if len(parent_inputs) >= 2:
            a, b = random.sample(parent_inputs, 2)
        else:
            a = b = parent_inputs[0]
        prefix, suffix = random_splice_cuts(read_text(a), read_text(b))
    else:
        raise ValueError(f"unknown op {op!r}")

    prompt = build_direct_prompt(
        provider,
        backend,
        op,
        prefix=prefix,
        suffix=suffix,
        fmt_name=fmt_name,
        fmt_desc=fmt_desc,
    )
    res = provider.generate_completion(
        prompt,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        stop=stop_for(backend, op),
    )
    body = res.get("generated_text", "") or ""
    if backend == "copilot":
        body = postprocess_copilot(body)

    if op == "complete":
        return prefix + body
    if op == "infilled":
        return prefix + body + suffix
    if op == "lmsplice":
        return prefix + body + suffix
    return body  # unreachable


def main() -> int:
    args = parse_args()
    forbidden_raw = os.environ.get("ELFUZZ_FORBIDDEN_MUTATORS", "").strip()
    forbidden = {f.strip() for f in forbidden_raw.split(",") if f.strip()}
    # accept both the synth-canonical names ("infilling", "lmsplicing") and
    # the names actually used in this module.
    forbidden_aliases = {
        "infilling": "infilled",
        "lmsplicing": "lmsplice",
        "completion": "complete",
    }
    forbidden = {forbidden_aliases.get(f, f) for f in forbidden}
    allowed = [op for op in ALL_OPS if op not in forbidden]
    if not allowed:
        print("[direct_mutate] ERROR: all mutation operators forbidden", file=sys.stderr)
        return 1

    seed_paths = [p for p in args.seed_paths if os.path.isdir(p)]
    if not seed_paths:
        print("[direct_mutate] ERROR: no valid seed (parent) collection directories", file=sys.stderr)
        return 1

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.log_dir, exist_ok=True)

    provider = create_provider(
        args.backend,
        model_id=args.model,
        endpoint=args.endpoint,
    )

    # Plan: one (var_idx, op, parent, input_idx) tuple per LLM call.
    plan: list[tuple[int, str, str, int]] = []
    variant_meta: dict[int, dict] = {}
    for var_idx in range(args.num_variants):
        parent = random.choice(seed_paths)
        op = random.choice(allowed)
        out_dir = os.path.join(args.output_dir, f"var_{var_idx:04d}.{op}")
        os.makedirs(out_dir, exist_ok=True)
        variant_meta[var_idx] = {
            "parent": parent,
            "operator": op,
            "out_dir": out_dir,
            "inputs_per_collection": args.inputs_per_collection,
        }
        for ii in range(args.inputs_per_collection):
            plan.append((var_idx, op, parent, ii))

    total = len(plan)
    print(
        f"[direct_mutate] dispatching {total} LLM calls "
        f"({args.num_variants} variants x {args.inputs_per_collection} inputs, "
        f"{args.jobs} workers)",
        file=sys.stderr,
        flush=True,
    )

    parent_inputs_cache: dict[str, list[str]] = {}

    def parent_inputs(parent: str) -> list[str]:
        if parent not in parent_inputs_cache:
            parent_inputs_cache[parent] = list_collection_inputs(parent)
        return parent_inputs_cache[parent]

    failures = 0
    done = 0
    report_every = max(1, total // 20)  # print ~20 progress lines per run
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {}
        for (var_idx, op, parent, ii) in plan:
            fut = ex.submit(
                make_one_input,
                provider,
                args.backend,
                op,
                parent_inputs(parent),
                args.format_name,
                args.format_description,
                args.temperature,
                args.max_new_tokens,
            )
            futs[fut] = (var_idx, op, ii)
        for fut in as_completed(futs):
            var_idx, op, ii = futs[fut]
            out_dir = variant_meta[var_idx]["out_dir"]
            out_path = os.path.join(
                out_dir, f"input_{ii:04d}{args.input_extension}"
            )
            try:
                content = fut.result()
            except Exception as exc:
                failures += 1
                print(
                    f"[direct_mutate] LLM call failed for var_{var_idx:04d}/{ii:04d}: {exc}",
                    file=sys.stderr,
                )
                content = ""
            with open(out_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(content)
            done += 1
            if done % report_every == 0 or done == total:
                elapsed = time.monotonic() - t0
                rate = done / elapsed if elapsed > 0 else 0
                eta = (total - done) / rate if rate > 0 else float("inf")
                print(
                    f"[direct_mutate] {done}/{total} inputs done "
                    f"({done*100//total}%) "
                    f"| {elapsed:.0f}s elapsed | ETA {eta:.0f}s",
                    file=sys.stderr,
                    flush=True,
                )

    for var_idx, meta in variant_meta.items():
        meta_path = os.path.join(args.log_dir, f"var_{var_idx:04d}.json")
        with open(meta_path, "w") as f:
            json.dump(meta, f)

    if failures:
        print(f"[direct_mutate] WARNING: {failures} LLM calls failed", file=sys.stderr)
    print(f"[direct_mutate] wrote {args.num_variants} variant collections to {args.output_dir}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
