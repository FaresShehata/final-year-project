#!/usr/bin/env python3
"""Generate the initial seed corpus for `elfuzz direct` mode using an LLM.

Writes ``rundir/initial/seeds/coll_NNNN/input_NNNN.<ext>``.
"""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from llm_provider import create_provider
from direct_common import (
    build_direct_prompt,
    postprocess_copilot,
    stop_for,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rundir", required=True)
    p.add_argument("--backend", choices=["huggingface", "copilot"], required=True)
    p.add_argument("-M", "--model", required=True, help="Model name/id passed to LLMProvider")
    p.add_argument(
        "-E",
        "--endpoint",
        default=None,
        help="Endpoint URL (HuggingFace TGI backend); ignored for Copilot",
    )
    p.add_argument("--num-collections", type=int, required=True)
    p.add_argument("--inputs-per-collection", type=int, required=True)
    p.add_argument("--input-extension", required=True)
    p.add_argument("--format-name", required=True)
    p.add_argument("--format-description", required=True)
    p.add_argument(
        "--hf-initial-prefix",
        default="",
        help="Bare prefix fed to the HuggingFace model (often empty).",
    )
    p.add_argument("--temperature", type=float, default=0.9)
    p.add_argument("--max-new-tokens", type=int, default=512)
    p.add_argument("-j", "--jobs", type=int, default=16)
    return p.parse_args()


def generate_one(
    provider,
    backend: str,
    fmt_name: str,
    fmt_desc: str,
    hf_initial_prefix: str,
    temperature: float,
    max_new_tokens: int,
) -> str:
    prompt = build_direct_prompt(
        provider,
        backend,
        "initial",
        prefix=hf_initial_prefix,
        suffix="",
        fmt_name=fmt_name,
        fmt_desc=fmt_desc,
    )
    res = provider.generate_completion(
        prompt,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
        stop=stop_for(backend, "initial"),
    )
    text = res.get("generated_text", "") or ""
    if backend == "copilot":
        return postprocess_copilot(text)
    # HF: model just continues the bare prefix; reconstruct full input.
    return hf_initial_prefix + text


def main() -> int:
    args = parse_args()
    initial_seeds = os.path.join(args.rundir, "initial", "seeds")
    os.makedirs(initial_seeds, exist_ok=True)

    provider = create_provider(
        args.backend,
        model_id=args.model,
        endpoint=args.endpoint,
    )

    plan: list[tuple[int, int]] = []
    for ci in range(args.num_collections):
        coll_dir = os.path.join(initial_seeds, f"coll_{ci:04d}")
        os.makedirs(coll_dir, exist_ok=True)
        for ii in range(args.inputs_per_collection):
            plan.append((ci, ii))

    print(
        f"[direct_initial] generating {len(plan)} inputs "
        f"({args.num_collections} collections x {args.inputs_per_collection})",
        file=sys.stderr,
        flush=True,
    )

    failures = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {}
        for (ci, ii) in plan:
            fut = ex.submit(
                generate_one,
                provider,
                args.backend,
                args.format_name,
                args.format_description,
                args.hf_initial_prefix,
                args.temperature,
                args.max_new_tokens,
            )
            futs[fut] = (ci, ii)
        for fut in as_completed(futs):
            ci, ii = futs[fut]
            out_path = os.path.join(
                initial_seeds, f"coll_{ci:04d}", f"input_{ii:04d}{args.input_extension}"
            )
            try:
                content = fut.result()
            except Exception as exc:
                failures += 1
                print(f"[direct_initial] LLM call failed for coll_{ci:04d}/input_{ii:04d}: {exc}", file=sys.stderr)
                content = ""
            with open(out_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(content)

    if failures:
        print(f"[direct_initial] WARNING: {failures} LLM calls failed", file=sys.stderr)
    print(f"[direct_initial] wrote initial corpus to {initial_seeds}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
