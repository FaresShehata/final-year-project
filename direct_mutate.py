#!/usr/bin/env python3
"""Mutate inputs from a single pool into candidate inputs via the LLM.

Picks one (or two, for ``lmsplice``) inputs at random from the pool, applies
one random allowed mutation operator per call, and writes each candidate into
its own per-candidate directory so the existing per-generator coverage tooling
(see ``getcov.py`` / ``getcov_fuzzbench.py``) treats each candidate as an
independent unit:

    <output_dir>/cand_NNNNNNNN/input_NNNNNNNN<ext>
"""

from __future__ import annotations

import argparse
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
    p.add_argument("--pool-dir", required=True,
                   help="Flat directory containing the current pool inputs")
    p.add_argument("--backend", choices=["huggingface", "copilot"], required=True)
    p.add_argument("-M", "--model", required=True)
    p.add_argument("-E", "--endpoint", default=None)
    p.add_argument("--output-dir", required=True)
    p.add_argument("-n", "--num-candidates", type=int, required=True)
    p.add_argument("--input-extension", required=True)
    p.add_argument("--format-name", required=True)
    p.add_argument("--format-description", required=True)
    p.add_argument("--temperature", type=float, default=0.6)
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("-j", "--jobs", type=int, default=16)
    return p.parse_args()


def list_pool_inputs(pool_dir: str) -> list[str]:
    return sorted(
        os.path.join(pool_dir, f)
        for f in os.listdir(pool_dir)
        if os.path.isfile(os.path.join(pool_dir, f))
    )


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def make_one_input(
    provider,
    backend: str,
    op: str,
    pool_inputs: list[str],
    fmt_name: str,
    fmt_desc: str,
    temperature: float,
    max_new_tokens: int,
) -> str:
    if op == "complete":
        text = read_text(random.choice(pool_inputs))
        prefix = random_complete_cut(text)
        suffix = ""
    elif op == "infilled":
        text = read_text(random.choice(pool_inputs))
        prefix, suffix = random_fim_cut(text)
    elif op == "lmsplice":
        if len(pool_inputs) >= 2:
            a, b = random.sample(pool_inputs, 2)
        else:
            a = b = pool_inputs[0]
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

    pool_inputs = list_pool_inputs(args.pool_dir)
    if not pool_inputs:
        print(f"[direct_mutate] ERROR: pool dir is empty: {args.pool_dir}",
              file=sys.stderr)
        return 1

    os.makedirs(args.output_dir, exist_ok=True)

    provider = create_provider(
        args.backend,
        model_id=args.model,
        endpoint=args.endpoint,
    )

    plan: list[tuple[int, str]] = []
    for ci in range(args.num_candidates):
        op = random.choice(allowed)
        plan.append((ci, op))

    total = len(plan)
    print(
        f"[direct_mutate] dispatching {total} LLM calls "
        f"(pool size = {len(pool_inputs)}, {args.jobs} workers)",
        file=sys.stderr,
        flush=True,
    )

    failures = 0
    done = 0
    report_every = max(1, total // 20)
    t0 = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {}
        for (ci, op) in plan:
            fut = ex.submit(
                make_one_input,
                provider,
                args.backend,
                op,
                pool_inputs,
                args.format_name,
                args.format_description,
                args.temperature,
                args.max_new_tokens,
            )
            futs[fut] = (ci, op)
        for fut in as_completed(futs):
            ci, op = futs[fut]
            cand_id = f"cand_{ci:08d}"
            cand_dir = os.path.join(args.output_dir, cand_id)
            os.makedirs(cand_dir, exist_ok=True)
            out_path = os.path.join(cand_dir, f"input_{ci:08d}{args.input_extension}")
            try:
                content = fut.result()
            except Exception as exc:
                failures += 1
                print(
                    f"[direct_mutate] LLM call failed for {cand_id} ({op}): {exc}",
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
                    f"[direct_mutate] {done}/{total} candidates done "
                    f"({done*100//total}%) "
                    f"| {elapsed:.0f}s elapsed | ETA {eta:.0f}s",
                    file=sys.stderr,
                    flush=True,
                )

    if failures:
        print(f"[direct_mutate] WARNING: {failures} LLM calls failed", file=sys.stderr)
    print(f"[direct_mutate] wrote {args.num_candidates} candidates to {args.output_dir}",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
