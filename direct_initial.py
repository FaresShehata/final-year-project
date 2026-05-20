#!/usr/bin/env python3
"""Generate the initial flat input population for `elfuzz direct` mode.

Writes ``<output_dir>/input_NNNNNNNN.<ext>`` (no collection nesting).
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
    p.add_argument("--output-dir", required=True)
    p.add_argument("--backend", choices=["huggingface", "copilot"], required=True)
    p.add_argument("-M", "--model", required=True, help="Model name/id passed to LLMProvider")
    p.add_argument(
        "-E",
        "--endpoint",
        default=None,
        help="Endpoint URL (HuggingFace TGI backend); ignored for Copilot",
    )
    p.add_argument("--num-initial-inputs", type=int, required=True)
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
    return hf_initial_prefix + text


def main() -> int:
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    provider = create_provider(
        args.backend,
        model_id=args.model,
        endpoint=args.endpoint,
    )

    n = args.num_initial_inputs
    print(
        f"[direct_initial] generating {n} initial inputs into {args.output_dir}",
        file=sys.stderr,
        flush=True,
    )

    failures = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {}
        for i in range(n):
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
            futs[fut] = i
        for fut in as_completed(futs):
            i = futs[fut]
            out_path = os.path.join(
                args.output_dir, f"input_{i:08d}{args.input_extension}"
            )
            try:
                content = fut.result()
            except Exception as exc:
                failures += 1
                print(
                    f"[direct_initial] LLM call failed for input_{i:08d}: {exc}",
                    file=sys.stderr,
                )
                content = ""
            with open(out_path, "w", encoding="utf-8", errors="replace") as f:
                f.write(content)

    if failures:
        print(f"[direct_initial] WARNING: {failures} LLM calls failed", file=sys.stderr)
    print(f"[direct_initial] wrote {n} inputs to {args.output_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
